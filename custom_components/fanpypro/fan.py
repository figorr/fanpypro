import logging

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import *

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
    num_speeds = entry.data.get(CONF_NUM_SPEEDS, 6)

    async_add_entities([
        FanpyProFanEntity(hass, entry, prefix, name, num_speeds),
    ])


class FanpyProFanEntity(FanEntity, RestoreEntity):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str, num_speeds: int) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._num_speeds = num_speeds
        self._attr_name = f"Fanpy Pro {name}"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}"
        self._attr_is_on = False
        self._attr_percentage = 0
        self._attr_supported_features = (
            FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF | FanEntityFeature.SET_SPEED
        )
        self._attr_percentage_step = 100.0 / max(num_speeds, 1)
        self._attr_speed_count = num_speeds
        self._last_percentage = 0

    @property
    def extra_state_attributes(self):
        return {"last_percentage": self._last_percentage}

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._hass.data.setdefault(DOMAIN, {}).setdefault(self._entry.entry_id, {})["fan_entity"] = self

        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_is_on = last_state.state == "on"
            if self._attr_is_on:
                self._attr_percentage = last_state.attributes.get("percentage", 0)
            self._last_percentage = last_state.attributes.get("last_percentage", 0)

        if not self._last_percentage:
            speed_select = f"select.{CONF_ENTITY_PREFIX}_{self._prefix}_velocidad"
            select_state = self.hass.states.get(speed_select)
            if select_state is not None and select_state.state not in ("unknown", "unavailable"):
                try:
                    level = int(select_state.state)
                    self._last_percentage = self._percentage_for_level(level)
                except (ValueError, TypeError):
                    pass

        if not self._last_percentage:
            self._last_percentage = self._percentage_for_level(1)

        self.async_write_ha_state()
        self.async_on_remove(
            self.hass.bus.async_listen("state_changed", self._handle_speed_change)
        )
        self.async_on_remove(
            self.hass.bus.async_listen("timer.finished", self._handle_timer_finished)
        )

    async def _handle_timer_finished(self, event) -> None:
        entity_id = event.data.get("entity_id", "")
        if self._prefix in entity_id:
            await self.async_turn_off()

    async def _handle_speed_change(self, event) -> None:
        speed_select = f"select.{CONF_ENTITY_PREFIX}_{self._prefix}_velocidad"
        if event.data.get("entity_id", "") != speed_select:
            return
        new_state = event.data.get("new_state")
        if new_state is not None and new_state.state not in ("unknown", "unavailable"):
            try:
                level = int(new_state.state)
                percentage = self._percentage_for_level(level)
                self._attr_percentage = percentage
                self._last_percentage = percentage
                self.async_write_ha_state()
            except (ValueError, TypeError):
                pass

    def _level_from_percentage(self, percentage: int) -> int:
        if percentage <= 0:
            return 0
        return max(1, min(round(percentage / 100 * self._num_speeds), self._num_speeds))

    def _percentage_for_level(self, level: int) -> int:
        return min(round(level / self._num_speeds * 100), 100)

    async def async_process_rf_command(self, matching_commands: list[str]) -> None:
        if not matching_commands:
            return

        # "on" siempre restaura la última velocidad (nunca aplica velocidad concreta)
        if "on" in matching_commands:
            if not self._attr_is_on:
                self._attr_is_on = True
                self._attr_percentage = self._last_percentage
                self.async_write_ha_state()
                _LOGGER.info("Fan ON from RF (restored last speed %s%%)", self._attr_percentage)
            return

        # Velocidad solo cuando NO hay "on" en los comandos coincidentes
        for c in matching_commands:
            if c.startswith("velocidad"):
                try:
                    level = int(c.replace("velocidad", ""))
                except ValueError:
                    continue
                self._attr_is_on = True
                self._attr_percentage = self._percentage_for_level(level)
                self._last_percentage = self._attr_percentage
                speed_select = f"select.{CONF_ENTITY_PREFIX}_{self._prefix}_velocidad"
                await self._hass.services.async_call(
                    "select", "select_option",
                    {"entity_id": speed_select, "option": str(level)},
                    blocking=True
                )
                self.async_write_ha_state()
                _LOGGER.info("Fan speed %d from RF", level)
                return

        # "off"
        if "off" in matching_commands:
            self._attr_is_on = False
            self._attr_percentage = 0
            self.async_write_ha_state()
            _LOGGER.info("Fan OFF from RF")

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs):
        if percentage is None:
            level = self._level_from_percentage(self._last_percentage) or 1
            self._attr_percentage = self._percentage_for_level(level)
            self._last_percentage = self._attr_percentage
            self._attr_is_on = True
            self.async_write_ha_state()
            await self._hass.services.async_call(
                "script", f"{self._prefix}_velocidad_{level}", {}, blocking=True
            )
            speed_select = f"select.{CONF_ENTITY_PREFIX}_{self._prefix}_velocidad"
            await self._hass.services.async_call(
                "select", "select_option", {"entity_id": speed_select, "option": str(level)}, blocking=True
            )
        else:
            level = self._level_from_percentage(percentage)
            self._last_percentage = percentage
            self._attr_percentage = percentage
            self._attr_is_on = True
            self.async_write_ha_state()
            await self._hass.services.async_call(
                "script", f"{self._prefix}_velocidad_{level}", {}, blocking=True
            )
            speed_select = f"select.{CONF_ENTITY_PREFIX}_{self._prefix}_velocidad"
            await self._hass.services.async_call(
                "select", "select_option", {"entity_id": speed_select, "option": str(level)}, blocking=True
            )

    async def _cancel_active_timers(self) -> None:
        for state_obj in self.hass.states.async_all():
            if (state_obj.state == "active"
                    and state_obj.entity_id.startswith("timer.")
                    and self._prefix in state_obj.entity_id):
                await self._hass.services.async_call(
                    "timer", "cancel", {"entity_id": state_obj.entity_id}, blocking=True
                )

    async def async_turn_off(self, **kwargs):
        if not self._attr_is_on:
            return
        self._last_percentage = self._attr_percentage
        self._attr_is_on = False
        self._attr_percentage = 0
        self.async_write_ha_state()
        await self._cancel_active_timers()
        await self._hass.services.async_call(
            "script", f"{self._prefix}_power_off", {}, blocking=True
        )

    async def async_set_percentage(self, percentage: int):
        level = self._level_from_percentage(percentage)
        if level > 0:
            self._last_percentage = percentage
        self._attr_percentage = percentage
        self._attr_is_on = level > 0
        self.async_write_ha_state()
        speed_select = f"select.{CONF_ENTITY_PREFIX}_{self._prefix}_velocidad"
        if level > 0:
            await self._hass.services.async_call(
                "script", f"{self._prefix}_velocidad_{level}", {}, blocking=True
            )
            await self._hass.services.async_call(
                "select", "select_option", {"entity_id": speed_select, "option": str(level)}, blocking=True
            )
        else:
            await self._cancel_active_timers()
            await self._hass.services.async_call(
                "script", f"{self._prefix}_power_off", {}, blocking=True
            )
