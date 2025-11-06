# Instalación de Librerías BLE para Arduino IDE

## 📚 Librería Necesaria

Para compilar `snes_esp32_ble.ino` necesitas la librería BLE de ESP32.

---

## 🔧 Método 1: Library Manager (Recomendado)

### Paso 1: Abrir Library Manager
1. Abre Arduino IDE
2. Ve a: **Sketch → Include Library → Manage Libraries...**
3. O usa el atajo: `Ctrl+Shift+I` (Windows/Linux) o `Cmd+Shift+I` (macOS)

### Paso 2: Buscar la librería
1. En el cuadro de búsqueda escribe: **"ESP32 BLE Arduino"**
2. Busca la librería oficial de **Espressif Systems**
3. Versión recomendada: **>= 2.0.0**

### Paso 3: Instalar
1. Click en el botón **"Install"**
2. Espera a que termine la descarga e instalación
3. Cierra el Library Manager

✅ ¡Listo! Ya puedes compilar el código BLE.

---

## 🔧 Método 2: Instalación Manual

Si el Library Manager no funciona, puedes instalar manualmente:

### Opción A: Desde ESP32 Board Manager

La librería BLE viene incluida con el ESP32 Board Manager.

1. Ve a: **File → Preferences** (o `Ctrl+,`)
2. En **"Additional Board Manager URLs"** añade:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Ve a: **Tools → Board → Boards Manager**
4. Busca **"esp32"** e instala **"esp32 by Espressif Systems"**
5. La librería BLE se instala automáticamente

### Opción B: Descarga Manual

1. Descarga desde: https://github.com/espressif/arduino-esp32
2. Copia la carpeta `BLE` a tu carpeta de librerías Arduino:
   - **Windows:** `C:\Users\[Usuario]\Documents\Arduino\libraries\`
   - **macOS:** `~/Documents/Arduino/libraries/`
   - **Linux:** `~/Arduino/libraries/`
3. Reinicia Arduino IDE

---

## ✅ Verificar Instalación

### Test 1: Compilar Ejemplo BLE
1. Ve a: **File → Examples → ESP32 BLE Arduino → BLE_server**
2. Selecciona tu placa ESP32: **Tools → Board → ESP32 Dev Module**
3. Click en **Verify** (✓)
4. Si compila sin errores, ✅ la librería está instalada correctamente

### Test 2: Incluir Headers
Abre un nuevo sketch y escribe:
```cpp
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

void setup() {
  Serial.begin(115200);
  Serial.println("BLE libraries OK!");
}

void loop() {}
```

Si compila sin errores, ✅ todo está correcto.

---

## 🐛 Troubleshooting

### Error: "BLEDevice.h: No such file or directory"

**Solución 1:** Verifica que tengas seleccionada una placa ESP32
- **Tools → Board → ESP32 Arduino → ESP32 Dev Module**

**Solución 2:** Reinstala el ESP32 Board Manager
1. Tools → Board → Boards Manager
2. Busca "esp32"
3. Click en "Remove"
4. Reinstala la última versión

**Solución 3:** Verifica la versión del core ESP32
- Necesitas ESP32 Arduino Core **>= 2.0.0**
- Versiones más antiguas tienen librerías BLE diferentes

### Error de compilación relacionado con Bluetooth

**Solución:** Asegúrate de tener estas configuraciones:
```
Tools → Partition Scheme → Default 4MB with spiffs (1.2MB APP/1.5MB SPIFFS)
Tools → Core Debug Level → None
Tools → Erase All Flash Before Sketch Upload → Disabled
```

### ESP32 no se reconoce

**Solución:** Instala drivers USB-Serial:
- **CP2102:** https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **CH340:** https://sparks.gogo.co.nz/ch340.html
- **FTDI:** https://ftdichip.com/drivers/vcp-drivers/

---

## 📦 Librerías Incluidas con ESP32 BLE

Al instalar la librería BLE, obtienes:

| Librería | Propósito |
|----------|-----------|
| `BLEDevice.h` | Inicialización del dispositivo BLE |
| `BLEServer.h` | Creación de servidor GATT |
| `BLEClient.h` | Creación de cliente BLE |
| `BLEUtils.h` | Utilidades y helpers |
| `BLEService.h` | Definición de servicios |
| `BLECharacteristic.h` | Características GATT |
| `BLEDescriptor.h` | Descriptores de características |
| `BLE2902.h` | CCCD (notificaciones) |
| `BLE2904.h` | Presentation format |
| `BLEAdvertising.h` | Configuración de advertising |

---

## 🔍 Versiones Probadas

| ESP32 Core | BLE Library | Estado |
|------------|-------------|--------|
| 2.0.0 | Incluida | ✅ Funcional |
| 2.0.1 | Incluida | ✅ Funcional |
| 2.0.2 | Incluida | ✅ Funcional |
| 2.0.3+ | Incluida | ✅ Funcional |
| 1.x.x | Incluida | ⚠️ API diferente |

**Recomendado:** ESP32 Arduino Core **>= 2.0.0**

---

## 📱 Dependencias del Sistema

### Windows
- ✅ Sin dependencias adicionales
- ✅ Drivers USB incluidos en instalador Arduino

### macOS
- ✅ Sin dependencias adicionales
- ✅ Drivers USB incluidos en el sistema

### Linux
Añade tu usuario al grupo `dialout`:
```bash
sudo usermod -a -G dialout $USER
# Luego cierra sesión y vuelve a entrar
```

---

## 🚀 Próximos Pasos

Una vez instalada la librería:

1. **Abre el firmware BLE:**
   ```
   File → Open → src/snes_esp32/snes_esp32_ble.ino
   ```

2. **Selecciona tu placa:**
   ```
   Tools → Board → ESP32 Arduino → ESP32 Dev Module
   ```

3. **Configura el puerto:**
   ```
   Tools → Port → /dev/cu.usbserial-XXXX (macOS/Linux)
                  COM3 (Windows)
   ```

4. **Compila y sube:**
   ```
   Sketch → Upload (Ctrl+U)
   ```

5. **Abre el Serial Monitor:**
   ```
   Tools → Serial Monitor (Ctrl+Shift+M)
   Baudrate: 115200
   ```

Deberías ver:
```
==============================================
SNES Controller Emulator - ESP32 with BLE
==============================================

Modos de comunicación:
  1. USB Serial (115200 baud)
  2. Bluetooth BLE (GATT Service)
...
BLE: Servicio iniciado
BLE: Esperando conexión de cliente...
```

---

## 📚 Recursos Adicionales

- [ESP32 BLE Arduino GitHub](https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE)
- [ESP32 BLE Examples](https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE/examples)
- [ESP32 Documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/)
- [Bluetooth SIG GATT Specifications](https://www.bluetooth.com/specifications/gatt/)

---

## ✅ Checklist de Instalación

- [ ] Arduino IDE instalado
- [ ] ESP32 Board Manager instalado (>= 2.0.0)
- [ ] Librería BLE disponible
- [ ] Placa ESP32 seleccionada
- [ ] Puerto serial configurado
- [ ] Ejemplo BLE compila sin errores
- [ ] `snes_esp32_ble.ino` compila correctamente

Si todos los puntos están marcados, ✅ **¡estás listo para usar BLE!**

---

**Última actualización:** 6 de noviembre de 2025
