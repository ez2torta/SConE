# 📦 Índice Completo - Proyecto SConE ESP32

Guía de navegación de todos los archivos del proyecto.

## 🎯 Para Empezar (Lectura Recomendada)

1. **[INICIO_RAPIDO_ESP32.md](INICIO_RAPIDO_ESP32.md)** ⭐
   - Guía paso a paso para principiantes
   - Instalación en 3 pasos
   - Ejemplos básicos
   - **LEE ESTO PRIMERO**

2. **[REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md)** ⚡
   - Cheatsheet de una página
   - Comandos más usados
   - Mapeo de bits resumido
   - **GUARDA ESTO A MANO**

## 📚 Documentación Completa

### Guías Principales

| Archivo | Descripción | Cuándo Leer |
|---------|-------------|-------------|
| **[README_ESP32.md](README_ESP32.md)** | Documentación técnica completa del proyecto ESP32 | Después del inicio rápido |
| **[BUTTON_MAPPING.md](BUTTON_MAPPING.md)** | Referencia detallada del mapeo de botones con ejemplos | Cuando necesites mapear botones |
| **[BLE_CONTROL.md](BLE_CONTROL.md)** | Control inalámbrico via Bluetooth BLE | Para control remoto |
| **[PINOUT_SNES.md](PINOUT_SNES.md)** | Diagramas de conexión y pinout del SNES | Al conectar hardware |
| **[FLUJO_DATOS.md](FLUJO_DATOS.md)** | Arquitectura y flujo de datos del sistema | Para entender el funcionamiento |
| **[CAMBIOS_ESP32.md](CAMBIOS_ESP32.md)** | Resumen de adaptaciones desde Arduino Uno | Para desarrolladores |

### Documentación Original

| Archivo | Descripción |
|---------|-------------|
| **[README.md](README.md)** | README original del proyecto (Arduino Uno) actualizado |
| **[snes-flow.md](snes-flow.md)** | Especificación del protocolo SNES original |

## 💾 Código Fuente

### ESP32 (Nuevo)

```
src/snes_esp32/
├── snes_esp32.ino          ← Código principal ESP32
└── pins_esp32.h            ← Definiciones de pines GPIO
```

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| **snes_esp32.ino** | ~230 | Lógica principal, mapeo, protocolo SNES |
| **pins_esp32.h** | ~50 | Configuración de pines GPIO del ESP32 |

**Características:**
- ✅ Control via Serial (uint32_t)
- ✅ Mapeo automático de 12 botones
- ✅ Opción de botones físicos
- ✅ Comentado extensivamente

### Arduino Uno (Original)

```
src/
├── snes.ino                ← Código original Arduino Uno
└── pins.h                  ← Pines originales
```

## 🧪 Scripts y Ejemplos

### Scripts de Prueba

| Archivo | Lenguaje | Propósito |
|---------|----------|-----------|
| **[test_snes_serial.py](test_snes_serial.py)** | Python | Script completo de pruebas automatizadas |

**Incluye:**
- Test de botones individuales
- Test de direccionales (D-Pad)
- Test de combinaciones
- Konami Code demo 🎮

### Ejemplos de Código

```
examples/
├── send_commands_example.ino    ← Ejemplo Arduino para enviar comandos Serial
├── ble_snes_example.py          ← Cliente Python BLE
├── ble_test_simple.py           ← Script de pruebas BLE
├── ble_snes_client_arduino.ino  ← Cliente Arduino BLE
└── requirements.txt             ← Dependencias Python
```

**Incluye:**
- Función para enviar uint32_t por Serial
- Helpers para cada botón
- Secuencias de ejemplo
- **Clientes BLE para Python y Arduino**

## 📋 Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| **platformio.ini** | Configuración PlatformIO (original) |

## 🗂️ Estructura Visual del Proyecto

```
SConE/
│
├── 📖 DOCUMENTACIÓN NUEVA (ESP32)
│   ├── INICIO_RAPIDO_ESP32.md        ⭐ Empezar aquí
│   ├── REFERENCIA_RAPIDA.md          ⚡ Cheatsheet
│   ├── README_ESP32.md               📚 Guía completa
│   ├── BUTTON_MAPPING.md             🗺️ Mapeo de botones
│   ├── PINOUT_SNES.md                🔌 Conexiones hardware
│   ├── FLUJO_DATOS.md                🔄 Arquitectura
│   ├── CAMBIOS_ESP32.md              📝 Changelog
│   └── INDICE.md                     📦 Este archivo
│
├── 💾 CÓDIGO ESP32
│   └── src/snes_esp32/
│       ├── snes_esp32.ino            🎯 Código principal
│       └── pins_esp32.h              📌 Pines GPIO
│
├── 🧪 TESTS Y EJEMPLOS
│   ├── test_snes_serial.py           🐍 Script Python
│   └── examples/
│       └── send_commands_example.ino  📝 Ejemplo Arduino
│
├── 📜 CÓDIGO ORIGINAL (Arduino Uno)
│   ├── src/
│   │   ├── snes.ino                  Arduino Uno original
│   │   └── pins.h                    Pines originales
│   └── UnoJoy/                       Librería UnoJoy
│
├── 📖 DOCUMENTACIÓN ORIGINAL
│   ├── README.md                     README actualizado
│   └── snes-flow.md                  Protocolo SNES
│
└── ⚙️ CONFIGURACIÓN
    └── platformio.ini                Config PlatformIO
```

## 🎯 Rutas de Aprendizaje

### 👤 Usuario Nuevo (Solo Quiero que Funcione)

```
1. INICIO_RAPIDO_ESP32.md    → Instalación básica
2. test_snes_serial.py       → Probar funcionamiento
3. REFERENCIA_RAPIDA.md      → Comandos comunes
```

### 👨‍💻 Desarrollador (Integrar en mi Proyecto)

```
1. README_ESP32.md           → Documentación completa
2. BUTTON_MAPPING.md         → Entender el mapeo
3. examples/*.ino            → Ver ejemplos de código
4. FLUJO_DATOS.md            → Comprender arquitectura
```

### 🔧 Hardware (Conectar Físicamente)

```
1. PINOUT_SNES.md            → Diagramas de conexión
2. INICIO_RAPIDO_ESP32.md    → Configuración de pines
3. test_snes_serial.py       → Verificar conexiones
```

### 🎓 Investigador (Entender Todo)

```
1. FLUJO_DATOS.md            → Arquitectura del sistema
2. CAMBIOS_ESP32.md          → Cambios vs original
3. snes-flow.md              → Protocolo SNES original
4. snes_esp32.ino            → Código comentado
```

## 📊 Estadísticas del Proyecto

### Documentación

- **Archivos nuevos:** 10
- **Páginas de docs:** ~50 páginas equivalentes
- **Diagramas:** 15+
- **Ejemplos de código:** 20+
- **Idioma:** Español 🇪🇸

### Código

- **Archivos de código:** 4 (2 nuevos, 2 originales)
- **Líneas de código nuevo:** ~300
- **Comentarios:** ~150 líneas
- **Funciones nuevas:** 7

### Ejemplos y Tests

- **Scripts Python:** 1 completo
- **Ejemplos Arduino:** 1 completo
- **Tests automatizados:** 7 secuencias

## 🔍 Búsqueda Rápida

### ¿Necesitas información sobre...?

| Tema | Archivo |
|------|---------|
| Cómo empezar | INICIO_RAPIDO_ESP32.md |
| Comandos rápidos | REFERENCIA_RAPIDA.md |
| Conexión de cables | PINOUT_SNES.md |
| Qué bit es qué botón | BUTTON_MAPPING.md |
| Cómo funciona internamente | FLUJO_DATOS.md |
| Cambios del original | CAMBIOS_ESP32.md |
| Código completo ESP32 | src/snes_esp32/snes_esp32.ino |
| Ejemplo Python | test_snes_serial.py |
| Ejemplo Arduino | examples/send_commands_example.ino |
| Protocolo SNES | snes-flow.md |

## 💡 Tips de Navegación

### Para Imprimir

Estos archivos son ideales para imprimir:
- ✅ REFERENCIA_RAPIDA.md (1 página)
- ✅ BUTTON_MAPPING.md (referencia visual)
- ✅ PINOUT_SNES.md (diagrama de conexiones)

### Para el Monitor

Estos son mejores en pantalla:
- 💻 README_ESP32.md (con links)
- 💻 FLUJO_DATOS.md (diagramas ASCII)
- 💻 INICIO_RAPIDO_ESP32.md (tutorial paso a paso)

### Para Compartir

Enlace directo para compartir:
- 🔗 INICIO_RAPIDO_ESP32.md → Para usuarios nuevos
- 🔗 REFERENCIA_RAPIDA.md → Para developers

## 📞 Contacto y Contribuciones

- **Proyecto original:** [SConE by jtrinklein](https://github.com/jtrinklein/SConE)
- **Adaptación ESP32:** Noviembre 2025
- **Repositorio:** [GitHub - ez2torta/SConE](https://github.com/ez2torta/SConE)

## 📜 Licencia

Mismo que el proyecto original SConE.

---

## 🎯 Próximos Pasos Sugeridos

Dependiendo de tu objetivo:

### Si quieres probarlo YA:
→ [INICIO_RAPIDO_ESP32.md](INICIO_RAPIDO_ESP32.md)

### Si eres developer:
→ [README_ESP32.md](README_ESP32.md)

### Si necesitas referencia rápida:
→ [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md)

### Si conectas hardware:
→ [PINOUT_SNES.md](PINOUT_SNES.md)

---

**Última actualización:** Noviembre 2025  
**Versión:** ESP32 v1.0
