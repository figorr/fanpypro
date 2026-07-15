# Fanpy Pro Gateway — ESPHome

Gateway RF multicanal con ESP32 NodeMCU + CC1101 para cada zona de la casa.

## Variantes

| Archivo | Destino | IP | Nombre ESPHome |
|---|---|---|---|
| `gateway-salon.yaml` | Salón | `192.168.2.150` | `gateway_salon` |
| `gateway-cocina.yaml` | Cocina | `192.168.2.151` | `gateway_cocina` |
| `gateway-pasillo.yaml` | Pasillo | `192.168.2.152` | `gateway_pasillo` |

Cada archivo YAML es autónomo e incluye toda la configuración (WiFi, SPI, CC1101, API, OTA).

## Conexiones

Conecta cada pin del ESP32 NodeMCU al CC1101 con cables Dupont hembra-hembra:

- **ESP32 pinout**

  ![ESP32 Pinout](img/esp32-elegoo-pinout.png)

- **CC1101 pinout**

  ![CC1101 Pinout](img/cc1101-pinout.png)

- **Wiring**

  ![Wiring](img/wiring.png)

  | ESP32 NodeMCU | CC1101 Pin | CC1101 | Color cable |
  |---|---|---|---|
  | GPIO26 | 3 | GDO0 (TX) | Amarillo |
  | GPIO25 | 8 | GDO2 (RX) | Gris |
  | GPIO32 (CS) | 4 | CSN | Rosa |
  | GPIO14 (SCK) | 5 | SCK | Verde |
  | GPIO23 (MOSI) | 6 | MOSI | Azul |
  | GPIO19 (MISO) | 7 | MISO | Rojo |
  | 3.3V | 2 | VCC | Negro|
  | GND | 1 | GND | Naranja |

  > Basado en el pinout del proyecto [Daedilus/cc1101-esp32-esphome-fan-controller](https://github.com/Daedilus/cc1101-esp32-esphome-fan-controller).

## Requisitos

- ESP32 NodeMCU + CC1101 (módulo 8-pin v2.0)
- Cableado Dupont hembra-hembra
- Home Assistant con ESPHome Builder 2026.5+
- Framework ESP-IDF (configurado en los YAMLs)

## Primeros pasos

1. Completa tus datos en `secrets.yaml` (WiFi, API key, OTA password).
2. Conecta los cables según la tabla de conexiones.
3. Flashea el primer dispositivo:

```bash
esphome run gateway-salon.yaml
```

4. Desde los logs de ESPHome, pulsa cada botón del mando original. Busca líneas como:

```
[I][remote.rc_switch:260]: Received RCSwitch Raw: protocol=1 data='11011101011010000001100110011'
```

5. Con los códigos capturados, crea un archivo `gateway_salon_codes.yaml` en `{config_dir}/custom_components/fanpypro_codes/` (usa la [plantilla](../custom_components/fanpypro/codes/gateway_template_codes.yaml)).
6. Repite para cocina y pasillo con sus YAMLs.

## Servicios API

### `transmit_rc_switch` (recomendado)

Envía un código RC Switch usando el protocolo detectado (protocolo 1 para este mando):

```yaml
service: esphome.gateway_salon_transmit_rc_switch
data:
  code: "11011101011010000001100110011"
  repeat_times: 10
```

### `transmit_raw`

Envía un código RF crudo (array de pulsos) — método alternativo si RC Switch no funciona:

```yaml
service: esphome.gateway_salon_transmit_raw
data:
  raw_code: [560, -620, 280, -310, ...]
  repeat_times: 10
  wait_time_ms: 0
```

## Eventos

Cuando se pulsa un botón del mando físico, el gateway dispara el evento `esphome.fanpypro_rf_code`:

```json
{
  "device": "gateway-salon",
  "code": "11011101011010000001100110011",
  "protocol": "1"
}
```

La integración fanpypro se suscribe a este evento para sincronizar el estado del ventilador cuando se usa el mando físico.

## Sincronización de la luz (toggle)

Si el mando físico usa el mismo código para encender y apagar la luz (toggle), puede producirse una desincronización entre el estado físico y el de Home Assistant tras un corte de luz, reinicio de HA, o cualquier evento no controlado.

Para resolverlo, la integración incluye el botón **Resync Luz** en cada dispositivo (Settings → Devices & Services → tu dispositivo → Controles). Al pulsarlo:

- Togglea el estado de la luz en HA (igual que haría el mando físico)
- **No** envía la señal RF al ventilador

Si el estado no se corrige al primer toque, pulsa de nuevo.

## Archivos del proyecto

| Archivo | Propósito |
|---|---|
| `gateway-salon.yaml` | Gateway salón (IP: 192.168.2.150) |
| `gateway-cocina.yaml` | Gateway cocina (IP: 192.168.2.151) |
| `gateway-pasillo.yaml` | Gateway pasillo (IP: 192.168.2.152) |
| `secrets.yaml` | Credenciales (no subir a git) |
| `../custom_components/fanpypro/codes/gateway_template_codes.yaml` | Plantilla para crear archivos de códigos |
