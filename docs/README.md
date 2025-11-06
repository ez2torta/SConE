# 📚 Documentación SNES Controller Emulator ESP32

Esta carpeta contiene toda la documentación del proyecto de adaptación ESP32.

## 🚀 Inicio Rápido

**Si es tu primera vez, empieza aquí:**

1. **[INICIO_RAPIDO_ESP32.md](INICIO_RAPIDO_ESP32.md)** ⭐
   - Instalación paso a paso
   - Configuración de Arduino IDE
   - Primeras pruebas

## 📖 Documentación Completa

### Guías Principales

| Documento | Descripción |
|-----------|-------------|
| **[INDICE.md](INDICE.md)** | Navegación completa del proyecto |
| **[README_ESP32.md](README_ESP32.md)** | Documentación técnica completa |
| **[REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md)** | Cheatsheet de una página |

### Referencias Técnicas

| Documento | Descripción |
|-----------|-------------|
| **[BUTTON_MAPPING.md](BUTTON_MAPPING.md)** | Mapeo detallado de botones |
| **[PINOUT_SNES.md](PINOUT_SNES.md)** | Conexiones y pinout del SNES |
| **[FLUJO_DATOS.md](FLUJO_DATOS.md)** | Arquitectura del sistema |
| **[CAMBIOS_ESP32.md](CAMBIOS_ESP32.md)** | Changelog técnico |

### Guías de Desarrollo

| Documento | Descripción |
|-----------|-------------|
| **[ARDUINO_IDE_VISUAL.md](ARDUINO_IDE_VISUAL.md)** | Guía visual de Arduino IDE |

## 🎯 Rutas de Aprendizaje

### Para Usuarios Nuevos

```
1. INICIO_RAPIDO_ESP32.md    → Instalación
2. ../test_snes_serial.py    → Probar funcionamiento  
3. REFERENCIA_RAPIDA.md      → Comandos comunes
```

### Para Desarrolladores

```
1. README_ESP32.md           → Documentación completa
2. BUTTON_MAPPING.md         → Entender mapeo
3. FLUJO_DATOS.md            → Arquitectura
4. CAMBIOS_ESP32.md          → Cambios técnicos
```

### Para Hardware

```
1. PINOUT_SNES.md            → Conexiones
2. INICIO_RAPIDO_ESP32.md    → Configuración
3. ../examples/              → Ver ejemplos
```

## 📂 Estructura del Proyecto

```
SConE/
├── docs/                    ← Estás aquí
│   ├── README.md           
│   ├── INDICE.md            
│   ├── INICIO_RAPIDO_ESP32.md
│   ├── README_ESP32.md      
│   ├── REFERENCIA_RAPIDA.md 
│   ├── BUTTON_MAPPING.md    
│   ├── PINOUT_SNES.md       
│   ├── FLUJO_DATOS.md       
│   ├── CAMBIOS_ESP32.md     
│   └── ARDUINO_IDE_VISUAL.md
│
├── src/snes_esp32/          ← Código ESP32
│   ├── snes_esp32.ino
│   ├── pins_esp32.h
│   └── README.md
│
├── examples/                ← Ejemplos
│   ├── test_serial_input.py
│   └── send_commands_example.ino
│
└── test_snes_serial.py      ← Script de prueba
```

## 🔗 Enlaces Rápidos

- [Volver al README principal](../README.md)
- [Ver código ESP32](../src/snes_esp32/)
- [Ver ejemplos](../examples/)

---

**Última actualización:** Noviembre 2025  
**Versión:** ESP32 v1.0
