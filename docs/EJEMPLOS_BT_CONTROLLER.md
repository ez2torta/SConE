# Ejemplos de Uso - bt_controller.py (Refactorizado)

## Instalación de Dependencias

```bash
pip install pyserial bleak
```

## Ejemplos Básicos

### 1. Conexión Serial Simple

```python
from app.controllers.bt_controller import SNESControllerSerial, SNESButton

# Conectar al ESP32 vía Serial
controller = SNESControllerSerial("/dev/cu.usbserial-2120")

# Presionar un botón
controller.press_button(SNESButton.A)
time.sleep(0.5)
controller.release_all()

# Presionar múltiples botones
controller.press_buttons([SNESButton.A, SNESButton.B])
time.sleep(0.5)
controller.release_all()

# Cerrar conexión
controller.close()
```

### 2. Conexión BLE Simple

```python
from app.controllers.bt_controller import SNESControllerBLE, SNESButton

# Conectar al ESP32 vía BLE (autodetección)
controller = SNESControllerBLE()
controller.connect()

# Presionar botón
controller.press_button(SNESButton.START)
time.sleep(0.5)
controller.release_all()

# Cerrar conexión
controller.close()
```

### 3. BLE con Dirección Específica

```python
from app.controllers.bt_controller import SNESControllerBLE, SNESButton

# Conectar con dirección MAC específica
controller = SNESControllerBLE("AA:BB:CC:DD:EE:FF")
controller.connect()

controller.press_button(SNESButton.A)
controller.close()
```

## Ejemplos Avanzados

### 4. Combo de Botones (Hadouken de Street Fighter)

```python
from app.controllers.bt_controller import SNESControllerBLE, SNESButton
import time

controller = SNESControllerBLE()
controller.connect()

# ⬇️ ↘️ ➡️ + Punch (Hadouken!)
hadouken = [
    SNESButton.DOWN,
    (SNESButton.DOWN, SNESButton.RIGHT),  # Diagonal
    SNESButton.RIGHT,
    SNESButton.Y  # Punch
]

for move in hadouken:
    if isinstance(move, tuple):
        controller.press_buttons(list(move))
    else:
        controller.press_button(move)
    time.sleep(0.15)
    controller.release_all()
    time.sleep(0.05)

controller.close()
```

### 5. Konami Code

```python
from app.controllers.bt_controller import SNESControllerBLE, SNESButton
import time

controller = SNESControllerBLE()
controller.connect()

konami_code = [
    SNESButton.UP, SNESButton.UP,
    SNESButton.DOWN, SNESButton.DOWN,
    SNESButton.LEFT, SNESButton.RIGHT,
    SNESButton.LEFT, SNESButton.RIGHT,
    SNESButton.B, SNESButton.A
]

for button in konami_code:
    controller.press_button(button)
    time.sleep(0.3)
    controller.release_all()
    time.sleep(0.2)

controller.close()
```

### 6. Context Manager (Gestión Automática)

```python
from app.controllers.bt_controller import SNESControllerBLE, SNESButton
import time

class ControllerContext:
    def __init__(self, controller):
        self.controller = controller
    
    def __enter__(self):
        if isinstance(self.controller, SNESControllerBLE):
            self.controller.connect()
        return self.controller
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.controller.close()

# Uso con context manager
with ControllerContext(SNESControllerBLE()) as controller:
    controller.press_button(SNESButton.A)
    time.sleep(0.5)
    controller.release_all()
# Automáticamente se cierra la conexión
```

### 7. Función de Utilidad para Secuencias

```python
from app.controllers.bt_controller import SNESControllerBLE, SNESButton
import time

def execute_sequence(controller, sequence, press_time=0.3, release_time=0.2):
    """
    Ejecuta una secuencia de botones.
    
    Args:
        controller: Instancia de Controller
        sequence: Lista de SNESButton o tuplas de SNESButton
        press_time: Tiempo que se mantiene presionado (segundos)
        release_time: Tiempo entre botones (segundos)
    """
    for item in sequence:
        if isinstance(item, (list, tuple)):
            controller.press_buttons(list(item))
        else:
            controller.press_button(item)
        
        time.sleep(press_time)
        controller.release_all()
        time.sleep(release_time)

# Uso
controller = SNESControllerBLE()
controller.connect()

# Secuencia personalizada
my_sequence = [
    SNESButton.START,  # Iniciar juego
    SNESButton.A,      # Confirmar
    SNESButton.DOWN,   # Seleccionar
    SNESButton.A,      # Confirmar
]

execute_sequence(controller, my_sequence)
controller.close()
```

### 8. Polimorfismo - Cambio Dinámico entre Serial y BLE

```python
from app.controllers.bt_controller import (
    SNESControllerSerial, 
    SNESControllerBLE, 
    SNESButton,
    Controller
)
import time

def play_sequence(controller: Controller):
    """
    Esta función acepta cualquier tipo de controlador
    y ejecuta la misma secuencia.
    """
    sequence = [SNESButton.A, SNESButton.B, SNESButton.START]
    
    for button in sequence:
        controller.press_button(button)
        time.sleep(0.3)
        controller.release_all()
        time.sleep(0.2)

# Funciona con Serial
serial_controller = SNESControllerSerial("/dev/ttyUSB0")
play_sequence(serial_controller)
serial_controller.close()

# Funciona con BLE
ble_controller = SNESControllerBLE()
ble_controller.connect()
play_sequence(ble_controller)
ble_controller.close()
```

### 9. Uso desde Línea de Comandos

```bash
# Test automático con Serial
python3 -m app.controllers.bt_controller serial /dev/ttyUSB0 test

# Test automático con BLE
python3 -m app.controllers.bt_controller ble test

# Modo interactivo Serial
python3 -m app.controllers.bt_controller serial /dev/ttyUSB0 interactive

# Modo interactivo BLE
python3 -m app.controllers.bt_controller ble interactive

# Modo turbo Serial
python3 -m app.controllers.bt_controller serial /dev/ttyUSB0 turbo

# Modo turbo BLE con dirección específica
python3 -m app.controllers.bt_controller ble AA:BB:CC:DD:EE:FF turbo
```

### 10. Integración con Sequence Player

```python
# En app/sequence_player.py
from app.controllers.bt_controller import SNESControllerBLE, SNESButton
from app.sequences import get_sequence

controller = SNESControllerBLE()
controller.connect()

# Cargar secuencia predefinida
sequence = get_sequence("kof_combo_1")

# Ejecutar cada paso de la secuencia
for step in sequence:
    buttons = [SNESButton[btn] for btn in step['buttons']]
    controller.press_buttons(buttons)
    time.sleep(step['duration'])
    controller.release_all()
    time.sleep(step.get('wait', 0.1))

controller.close()
```

## Diferencias con la Versión Anterior

### ❌ Versión Antigua (Async)

```python
import asyncio
from bt_controller import SNESControllerBLE, BUTTONS

async def main():
    controller = SNESControllerBLE()
    await controller.connect()
    await controller.send_buttons_async(BUTTONS['A'])
    await controller.disconnect()

asyncio.run(main())
```

### ✅ Versión Nueva (Síncrona)

```python
from app.controllers.bt_controller import SNESControllerBLE, SNESButton

controller = SNESControllerBLE()
controller.connect()
controller.press_button(SNESButton.A)
controller.close()
```

## Tips y Mejores Prácticas

1. **Siempre cerrar la conexión**: Usa `controller.close()` o un context manager
2. **Usar `release_all()` frecuentemente**: Evita que botones queden "pegados"
3. **Type safety con Enum**: Usa `SNESButton.A` en lugar de valores mágicos
4. **Polimorfismo**: Escribe funciones que acepten `Controller` para máxima flexibilidad
5. **Tiempos apropiados**: El SNES lee a ~60Hz, no envíes comandos más rápido
6. **Manejo de errores**: Envuelve las operaciones en try/except

## Troubleshooting

### Error: "pyserial no está instalado"
```bash
pip install pyserial
```

### Error: "bleak no está instalado"
```bash
pip install bleak
```

### Error: "No se encontró el dispositivo 'SNES Controller'"
- Verifica que el ESP32 esté encendido y en modo BLE
- Asegúrate que el nombre del dispositivo BLE es "SNES Controller" (sin guión)
- Usa la dirección MAC específica si conoces el dispositivo

### Error: "No se pudo conectar al puerto /dev/ttyUSB0"
- Verifica que el ESP32 esté conectado
- Comprueba los permisos: `sudo chmod 666 /dev/ttyUSB0`
- En macOS, busca `/dev/cu.usbserial-*`
- En Windows, usa `COM3`, `COM4`, etc.

## Referencias

- [Documentación completa del refactor](./REFACTOR_BT_CONTROLLER.md)
- [Serial Controller](../app/controllers/serial_controller.py)
- [BT Controller](../app/controllers/bt_controller.py)
- [Sequence Player](../app/sequence_player.py)
