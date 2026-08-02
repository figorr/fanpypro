import asyncio
import logging
import time

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import *
from . import _normalize_rf_code

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    mode = entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
    if mode == CONF_MODE_DIRECT:
        return

    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)

    async_add_entities([
        FanpyProLightEntity(hass, entry, prefix, name),
    ])


class FanpyProLightEntity(LightEntity, RestoreEntity):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._lock = asyncio.Lock()
        self._last_tx_codes: dict[str, float] = {}
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"FanpyPro {name} Luz"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_luz"
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.hass.data.setdefault(DOMAIN, {}).setdefault(self._entry.entry_id, {})["light_entity"] = self
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_is_on = last_state.state == "on"
        self.async_write_ha_state()

    def _tx_code(self, cmd_key: str) -> str | None:
        zone = self._entry.data.get(CONF_GATEWAY_ZONE)
        if not zone:
            return None
        cache = self.hass.data.get(DOMAIN, {}).get("codes_cache", {})
        fan_codes = cache.get(zone, {}).get(self._prefix, {})
        cmd_data = fan_codes.get(cmd_key)
        if isinstance(cmd_data, dict):
            return _normalize_rf_code(cmd_data.get("code"))
        return None

    def _record_tx_codes(self, codes) -> None:
        now = time.monotonic()
        self._last_tx_codes = {
            c: ts for c, ts in self._last_tx_codes.items()
            if now - ts < RF_ECHO_WINDOW
        }
        for c in codes:
            if c:
                self._last_tx_codes[c] = now

    async def async_process_rf_command(self, code: str, matching_commands: list[str]) -> None:
        async with self._lock:
            now = time.monotonic()
            if code and code in self._last_tx_codes and now - self._last_tx_codes[code] < RF_ECHO_WINDOW:
                _LOGGER.debug("Suppressed RF echo: code=%s (%.1fs since TX)", code, now - self._last_tx_codes[code])
                return
            if "luz_on" in matching_commands and "luz_off" in matching_commands:
                self._attr_is_on = not self._attr_is_on
                self.async_write_ha_state()
                _LOGGER.debug("Light toggled from RF: is_on=%s", self._attr_is_on)
                return
            for c in matching_commands:
                if c == "luz_on":
                    self._attr_is_on = True
                elif c == "luz_off":
                    self._attr_is_on = False
                else:
                    continue
                self.async_write_ha_state()
                _LOGGER.debug("Light updated from RF: is_on=%s", self._attr_is_on)
                return

    async def async_turn_on(self, **kwargs) -> None:
        async with self._lock:
            self._attr_is_on = True
            self.async_write_ha_state()
            self._record_tx_codes([self._tx_code("luz_on")])
            await self.hass.services.async_call(
                "script", f"{self._prefix}_luz_on", {}, blocking=True
            )

    async def async_turn_off(self, **kwargs) -> None:
        async with self._lock:
            self._attr_is_on = False
            self.async_write_ha_state()
            self._record_tx_codes([self._tx_code("luz_off")])
            await self.hass.services.async_call(
                "script", f"{self._prefix}_luz_off", {}, blocking=True
            )
