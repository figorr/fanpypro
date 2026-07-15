import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MODE
from homeassistant.core import HomeAssistant

from .const import *

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fanpypro"

PLATFORMS = ["select", "fan", "light", "button"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await _generate_scripts_yaml(hass, entry)

    mode = entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
    if mode == CONF_MODE_DIRECT:
        entity_fan = entry.data.get(CONF_ENTITY_FAN, "")
        prefix = entry.data.get(CONF_PREFIX, "ventilador")
        if entity_fan:

            async def _direct_timer_finished(event):
                entity_id = event.data.get("entity_id", "")
                if prefix in entity_id:
                    await hass.services.async_call(
                        "switch", "turn_off", {"entity_id": entity_fan}, blocking=True
                    )

            remove_listener = hass.bus.async_listen(
                "timer.finished", _direct_timer_finished
            )
            hass.data[DOMAIN][entry.entry_id]["timer_listener"] = remove_listener

    if mode == CONF_MODE_REMOTE and not hass.data[DOMAIN].get("rf_listener_setup"):
        hass.data[DOMAIN]["rf_listener_setup"] = True

        async def _handle_rf_code(event) -> None:
            device = event.data.get("device", "")
            code = event.data.get("code", "")
            if not device or not code:
                return

            zone = device.replace("gateway-", "", 1) if device.startswith("gateway-") else device
            cache = hass.data.get(DOMAIN, {}).get("codes_cache", {})
            zone_codes = cache.get(zone, {})

            for entry in hass.config_entries.async_entries(DOMAIN):
                if entry.data.get(CONF_GATEWAY_ZONE) != zone:
                    continue
                prefix = entry.data.get(CONF_PREFIX)
                if not prefix:
                    continue
                fan_codes = zone_codes.get(prefix, {})
                matching_commands = _find_commands_by_code(fan_codes, code)
                if not matching_commands:
                    continue

                fan_entity = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("fan_entity")
                if fan_entity:
                    await fan_entity.async_process_rf_command(matching_commands)

                light_cmds = [c for c in matching_commands if c.startswith("luz_") or c.startswith("intensidad_") or c.startswith("luz_calida") or c.startswith("luz_fria")]
                if light_cmds:
                    light_entity = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("light_entity")
                    if light_entity:
                        await light_entity.async_process_rf_command(light_cmds)

        hass.bus.async_listen("esphome.fanpypro_rf_code", _handle_rf_code)
        await _load_and_cache_codes(hass)

    _LOGGER.info("Setup complete for entry %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    remove_listener = hass.data[DOMAIN].get(entry.entry_id, {}).get("timer_listener")
    if remove_listener:
        remove_listener()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    integration_dir = os.path.dirname(__file__)

    def _remove_file(filename):
        path = os.path.join(integration_dir, "generated", filename)
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        marker = f"# Prefix: {prefix}"
        if marker not in content:
            return
        lines = content.split("\n")
        result = []
        i = 0
        while i < len(lines):
            if lines[i].strip() == marker:
                i += 1
                while i < len(lines) and not lines[i].startswith("# Prefix:"):
                    i += 1
            else:
                result.append(lines[i])
                i += 1
        cleaned = "\n".join(result)
        if cleaned.strip():
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned + "\n")
        else:
            os.remove(path)

    await hass.async_add_executor_job(_remove_file, "scripts.yaml")


def _load_codes(codes_dir: str, zone: str) -> dict | None:
    codes_path = os.path.join(codes_dir, f"gateway_{zone}_codes.yaml")
    if not os.path.exists(codes_path):
        return None
    import yaml
    with open(codes_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_raw_code(command_data):
    if isinstance(command_data, dict):
        return command_data.get("raw", command_data)
    return command_data


def _get_rc_code(command_data):
    if isinstance(command_data, dict):
        return command_data.get("code")
    return None


def _get_rc_protocol(command_data):
    if isinstance(command_data, dict):
        return command_data.get("protocol", 1)
    return 1


def _get_repeat(command_data, defaults):
    if isinstance(command_data, dict) and "repeat" in command_data:
        return command_data["repeat"]
    return defaults.get("repeat", DEFAULT_GATEWAY_REPEAT)


def _get_wait(command_data, defaults):
    if isinstance(command_data, dict) and "wait" in command_data:
        return command_data["wait"]
    return defaults.get("wait", DEFAULT_GATEWAY_WAIT_MS)


async def _load_and_cache_codes(hass: HomeAssistant) -> None:
    codes_dir = hass.config.path("custom_components", CODES_DIR)

    def _load():
        if not os.path.isdir(codes_dir):
            return None
        cache = {}
        for fname in os.listdir(codes_dir):
            if not fname.startswith("gateway_") or not fname.endswith("_codes.yaml"):
                continue
            zone = fname[len("gateway_"):-len("_codes.yaml")]
            path = os.path.join(codes_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    import yaml
                    cache[zone] = yaml.safe_load(f)
            except Exception as e:
                _LOGGER.warning("Failed to load codes for '%s': %s", zone, e)
        return cache

    cache = await hass.async_add_executor_job(_load)
    if cache is not None:
        hass.data.setdefault(DOMAIN, {})["codes_cache"] = cache


def _find_commands_by_code(fan_codes: dict, code: str) -> list[str]:
    matches = []
    # The event code from ESPHome arrives as decimal; also try binary conversion
    code_bin = None
    try:
        code_bin = bin(int(code))[2:]
    except (ValueError, TypeError):
        pass

    for cmd_key, cmd_data in fan_codes.items():
        if isinstance(cmd_data, dict):
            rc_code = cmd_data.get("code")
        else:
            continue
        if rc_code and (str(rc_code) == code or (code_bin and str(rc_code) == code_bin)):
            matches.append(cmd_key)
    return matches


def _pick_best_command(matching_commands: list[str]) -> str:
    preferred = None
    for c in matching_commands:
        if c.startswith("velocidad"):
            return c
        if c in ("power_on", "power_off", "luz_on", "luz_off"):
            preferred = c
    return preferred or matching_commands[0]





async def _generate_scripts_yaml(hass: HomeAssistant, entry: ConfigEntry) -> None:
    integration_dir = os.path.dirname(__file__)
    output_dir = os.path.join(integration_dir, "generated")
    os.makedirs(output_dir, exist_ok=True)
    scripts_path = os.path.join(output_dir, "scripts.yaml")

    entries = hass.config_entries.async_entries(DOMAIN)
    codes_dir = hass.config.path("custom_components", CODES_DIR)

    def _write():
        blocks = []
        for e in entries:
            d = e.data
            mode = d.get(CONF_MODE, CONF_MODE_REMOTE)
            p = d.get(CONF_PREFIX, "ventilador")
            n = d.get(CONF_NAME, p)

            if mode == CONF_MODE_REMOTE:
                gateway_zone = d.get(CONF_GATEWAY_ZONE)
                if gateway_zone:
                    block = _build_gateway_scripts_yaml(
                        codes_dir, p, n, d
                    )
                else:
                    block = ""
            else:
                block = ""

            if block and block.strip():
                blocks.append(block)

        content = "\n\n".join(blocks)
        if content.strip():
            with open(scripts_path, "w", encoding="utf-8") as f:
                f.write(content + "\n")
        else:
            if os.path.exists(scripts_path):
                os.remove(scripts_path)

    await hass.async_add_executor_job(_write)

    _LOGGER.info("Fanpy Pro: regenerated scripts.yaml for all entries")


def _build_gateway_scripts_yaml(
    codes_dir: str, prefix: str, name: str, data: dict
) -> str:
    zone = data.get(CONF_GATEWAY_ZONE)
    if not zone:
        _LOGGER.warning("No gateway zone configured for '%s'", prefix)
        return ""

    codes = _load_codes(codes_dir, zone)
    if codes is None:
        _LOGGER.warning(
            "Codes file not found for gateway '%s'. Create gateway_%s_codes.yaml in fanpypro_codes/",
            zone, zone,
        )
        return ""

    device_name = codes.get("device")
    if not device_name:
        _LOGGER.warning(
            "Missing 'device' field in gateway_%s_codes.yaml", zone
        )
        return ""

    defaults = codes.get("defaults", {})
    fan_codes = codes.get(prefix)
    if fan_codes is None:
        _LOGGER.warning(
            "Prefix '%s' not found in gateway_%s_codes.yaml", prefix, zone
        )
        return ""

    lines = []
    lines.append(f"# Prefix: {prefix}")
    lines.append(f"# Name: {name}")
    lines.append(f"# Gateway: {zone} ({device_name})")
    lines.append("")

    ns = int(data.get(CONF_NUM_SPEEDS, 6))
    has_light = data.get(CONF_HAS_LIGHT, False)
    has_temp = data.get(CONF_HAS_LIGHT_TEMPERATURE, False)
    has_intensity = data.get(CONF_HAS_LIGHT_INTENSITY, False)

    commands = [
        ("power_on", f"{name} Power ON", "on"),
        ("power_off", f"{name} Power OFF", "off"),
    ]

    if has_light:
        commands.append(("luz_on", f"{name} Luz ON", "luz_on"))
        commands.append(("luz_off", f"{name} Luz OFF", "luz_off"))
        if has_temp:
            commands.append(("luz_calida", f"{name} Luz Cálida", "luz_calida"))
            commands.append(("luz_fria", f"{name} Luz Fría", "luz_fria"))
        if has_intensity:
            commands.append(("intensidad_alta", f"{name} Intensidad Alta", "intensidad_alta"))
            commands.append(("intensidad_baja", f"{name} Intensidad Baja", "intensidad_baja"))

    if ns > 1:
        for i in range(1, ns + 1):
            cmd_alias = f"velocidad_{i}"
            cmd_name = f"velocidad{i}"
            commands.append((cmd_alias, f"{name} Velocidad {i}", cmd_name))

    device_service = device_name.replace("-", "_")

    for alias, display_name, cmd_key in commands:
        cmd_data = fan_codes.get(cmd_key)
        if cmd_data is None:
            _LOGGER.info(
                "Command '%s' not found for prefix '%s' in gateway '%s' — skipping",
                cmd_key, prefix, zone,
            )
            continue

        repeat = _get_repeat(cmd_data, defaults)
        rc_code = _get_rc_code(cmd_data)
        raw = _get_raw_code(cmd_data)

        lines.append(f"{prefix}_{alias}:")
        lines.append("  sequence:")

        if rc_code:
            protocol = _get_rc_protocol(cmd_data)
            lines.append(f"  - action: esphome.{device_service}_transmit_rc_switch")
            lines.append("    data:")
            lines.append(f"      code: '{rc_code}'")
            lines.append(f"      repeat_times: {repeat}")
        else:
            wait = _get_wait(cmd_data, defaults)
            lines.append(f"  - action: esphome.{device_service}_transmit_raw")
            lines.append("    data:")
            lines.append(f"      raw_code: {raw}")
            lines.append(f"      repeat_times: {repeat}")
            lines.append(f"      wait_time_ms: {wait}")

        lines.append(f"  alias: \"{display_name}\"")
        lines.append("  description: ''")
        lines.append("")

    return "\n".join(lines)
