import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)
    num_speeds = entry.data.get(CONF_NUM_SPEEDS, 6)

    entities = [
        FanSpeedSelect(hass, entry, prefix, name, num_speeds),
    ]

    num_timers = int(entry.data.get(CONF_NUM_TIMERS, 0))
    if num_timers >= 0:
        entities.append(FanpyProTimerCountSelect(hass, entry, prefix, name))

    async_add_entities(entities)


class FanSpeedSelect(SelectEntity):

    _attr_icon = "mdi:format-list-bulleted"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str, num_speeds: int) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._num_speeds = num_speeds
        self._attr_name = f"Fanpy Pro {name} Velocidad"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_velocidad"
        self._attr_options = [str(i) for i in range(1, num_speeds + 1)]
        self._attr_current_option = self._attr_options[0]

    @property
    def extra_state_attributes(self):
        attrs = {
            "fanpypro_mode": self._entry.data.get(CONF_MODE, CONF_MODE_REMOTE),
        }
        mode = self._entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
        if mode == CONF_MODE_DIRECT:
            attrs["entity_fan"] = self._entry.data.get(CONF_ENTITY_FAN, "")
            entity_light = self._entry.data.get(CONF_ENTITY_LIGHT, "")
            if entity_light:
                attrs["entity_light"] = entity_light
        return attrs

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()


class FanpyProTimerCountSelect(SelectEntity):

    _attr_icon = "mdi:timer-outline"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"Fanpy Pro {name} Timers"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_num_timers"
        self._attr_options = [str(i) for i in range(0, 4)]
        self._attr_current_option = str(int(entry.data.get(CONF_NUM_TIMERS, 0)))

    async def async_select_option(self, option: str) -> None:
        self._hass.config_entries.async_update_entry(
            self._entry,
            data={**self._entry.data, CONF_NUM_TIMERS: int(option)},
        )
        await self._hass.config_entries.async_reload(self._entry.entry_id)
