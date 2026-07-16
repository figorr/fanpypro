# Códigos RF por gateway

Guarda aquí los archivos `gateway_{zona}_codes.yaml` con los raw codes capturados desde ESPHome.

> **Atención**: Esta carpeta está dentro de `custom_components/fanpypro/codes/` solo como referencia.
> Los archivos reales deben ir en `{config_dir}/custom_components/fanpypro_codes/`
> para que sobrevivan a actualizaciones de HA y de la integración.
>
> Ejemplo: `homeassistant/custom_components/fanpypro_codes/gateway_salon_codes.yaml`

## Formato

```yaml
device: gateway_salon
defaults:
  repeat: 10
  wait: 4733

ventilador_salon:
  "on": [560, -620, 280, -310, ...]
  "off": [580, -640, ...]
  luz_on: [490, -500, ...]
  luz_off: [490, -500, ...]
  luz_calida: [...]
  luz_fria: [...]
  intensidad_alta: [...]
  intensidad_baja: [...]
  velocidad1: [...]
  velocidad2: [...]
  velocidad3: [...]
  velocidad4: [...]
  velocidad5: [...]
  velocidad6: [...]
```

El campo `device` debe coincidir con el `name` del YAML de ESPHome (ej: `gateway_salon`, `gateway_cocina`, `gateway_pasillo`).

## Valores por comando individual

Si un comando necesita `repeat` o `wait` diferente al default:

```yaml
ventilador_salon:
  "on":
    raw: [560, -620, ...]
    repeat: 5
    wait: 2000
  "off": [580, -640, ...]
```

## Archivos esperados

| Zona | Archivo |
|---|---|
| salón | `gateway_salon_codes.yaml` |
| cocina | `gateway_cocina_codes.yaml` |
| pasillo | `gateway_pasillo_codes.yaml` |

Deben estar en `{config_dir}/custom_components/fanpypro_codes/`

## Plantilla

Usa `gateway_template_codes.yaml` como base para crear nuevos archivos de códigos:

```bash
cp gateway_template_codes.yaml /ruta/a/homeassistant/custom_components/fanpypro_codes/gateway_mizona_codes.yaml
```
