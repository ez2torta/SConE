# Control via Bluetooth BLE

La versión ESP32 del SConE ahora soporta control inalámbrico mediante Bluetooth Low Energy (BLE), eliminando la necesidad de conexiones físicas para los botones.

## 📋 Requisitos

- ESP32 con soporte BLE (ESP32, ESP32-S2, ESP32-S3, etc.)
- Dispositivo cliente con BLE (computadora, teléfono, otro ESP32)
- Biblioteca BLE de Arduino (incluida por defecto en ESP32)

## 🔧 Configuración del ESP32

### 1. Cargar el código

Sube el archivo `src/snes_esp32/snes_esp32.ino` a tu ESP32 usando Arduino IDE o PlatformIO.

### 2. Verificar conexión BLE

Después de cargar, abre el monitor serial (115200 baud). Deberías ver:

```
SNES Controller Emulator - ESP32 BLE
BLE iniciado. Esperando conexiones...
```

### 3. Conectar pines SNES

Conecta los pines del ESP32 a la consola SNES según `docs/PINOUT_SNES.md`.

### 📡 Protocolo BLE

### Servicio y Característica

- **Nombre del dispositivo:** "SNES Controller"
- **UUID del servicio:** `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
- **UUID de la característica:** `beb5483e-36e1-4688-b7f5-ea07361b26a8`

### Formato de datos

**Envía exactamente 4 bytes (little-endian) que representan un `uint32_t`**

Esta implementación BLE funciona **idénticamente** al modo Serial:
- ✅ Mismo formato de datos (4 bytes little-endian)
- ✅ Mismo procesamiento en Arduino
- ✅ Mismo mapeo de botones
- ✅ Mismo protocolo SNES

### Ejemplo de uso

Para presionar el botón A:
- Valor: `0x00001000` (bit 12 activado)
- Bytes: `00 10 00 00` (little-endian)

Para presionar A + B + Arriba:
- Valor: `0x00001101` (bits 0, 8, 12 activados)
- Bytes: `01 11 00 00` (little-endian)

## 💻 Ejemplos de código

### Python (con bleak)

```bash
# Instalar dependencias
pip install -r examples/requirements.txt

# Ejecutar el ejemplo
python examples/ble_snes_example.py
```

### Arduino/ESP32 (cliente)

```cpp
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEClient.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

BLEClient* pClient;
BLERemoteCharacteristic* pCharacteristic;

void setup() {
    BLEDevice::init("SNES Client");

    // Escanear y conectar (implementar lógica de escaneo)
    // ...

    // Enviar botón A
    uint32_t buttonMask = (1 << 12);  // Botón A
    uint8_t data[4];
    memcpy(data, &buttonMask, 4);  // little-endian
    pCharacteristic->writeValue(data, 4);
}

void loop() {
    // Tu lógica aquí
}
```

**Archivo completo:** `examples/ble_snes_client_arduino.ino`

### Script de Prueba Simple

Para debugging y verificación del mapeo de botones:

```bash
python examples/ble_test_simple.py
```

**Archivo:** `examples/ble_test_simple.py`

## 🔍 Solución de problemas

### No se conecta el dispositivo
- Verifica que el ESP32 esté encendido y ejecutando el código
- Asegúrate de que BLE esté habilitado en tu dispositivo cliente
- Revisa la distancia (BLE tiene alcance limitado)

### No responde a comandos
- Verifica que estés escribiendo en la característica correcta
- Asegúrate de enviar exactamente 4 bytes
- Confirma que el formato sea little-endian

### Baja latencia
BLE tiene latencia inherente (~10-20ms). Para juegos que requieren respuesta inmediata, considera usar Serial USB.

## 📚 Referencias

- [BLE con ESP32 - Documentación oficial](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/bluetooth/index.html)
- [Biblioteca BLE de Arduino](https://www.arduino.cc/reference/en/libraries/esp32_ble_arduino/)
- [Bleak - BLE para Python](https://github.com/hbldh/bleak)