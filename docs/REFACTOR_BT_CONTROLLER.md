# Refactor de bt_controller.py

**Fecha**: 27 de noviembre de 2025  
**Objetivo**: Refactorizar `bt_controller.py` siguiendo el patrón de diseño de `serial_controller.py`

## Cambios Principales

### 1. **Simplificación de la interfaz BLE**

#### Antes
- Métodos separados: `send_buttons()` (síncrono, lanzaba error) y `send_buttons_async()` (asíncrono)
- Requería manejo explícito de `asyncio` en el código cliente
- No había métodos auxiliares como `press_button()` o `press_buttons()`

#### Después
- Método único `send_buttons(button_mask: int)` que funciona de manera síncrona
- Manejo interno de asyncio usando `asyncio.run()` o event loop existente
- Métodos auxiliares añadidos:
  - `press_button(button: SNESButton)` - Presiona un solo botón
  - `press_buttons(buttons: List[SNESButton])` - Presiona múltiples botones
  - `release_all()` - Suelta todos los botones

### 2. **Uso de SNESButton Enum**

#### Antes
```python
BUTTONS = {
    'B': 1 << 0,
    'Y': 1 << 1,
    # ...
}
```

#### Después
```python
from enum import Enum

class SNESButton(Enum):
    B = 1 << 0
    Y = 1 << 1
    # ...
```

**Ventajas**:
- Type safety
- Auto-completado en IDEs
- Menos errores de typos
- Interfaz consistente entre Serial y BLE

### 3. **Interfaz Controller Abstracta**

Se implementa la clase abstracta `Controller` para que tanto `SNESControllerSerial` como `SNESControllerBLE` compartan la misma interfaz:

```python
class Controller(ABC):
    @abstractmethod
    def send_buttons(self, button_mask: int) -> None: ...
    
    @abstractmethod
    def close(self) -> None: ...
```

Esto permite:
- Intercambiar controladores sin cambiar código cliente
- Polimorfismo
- Testing más sencillo (mocks)

### 4. **Gestión Automática del Event Loop**

#### Antes
```python
# El usuario tenía que hacer:
async def main():
    controller = SNESControllerBLE()
    await controller.connect()
    await controller.send_buttons_async(0xFF)
    
asyncio.run(main())
```

#### Después
```python
# Ahora es tan simple como:
controller = SNESControllerBLE()
controller.connect()  # Síncrono
controller.send_buttons(0xFF)  # Síncrono
```

El manejo de asyncio se hace internamente usando:
- `asyncio.run()` para operaciones puntuales
- Detección del event loop existente cuando se ejecuta dentro de código async

### 5. **Métodos de Conveniencia**

Se añaden los siguientes métodos que no estaban en la versión original:

```python
# Presionar un solo botón
controller.press_button(SNESButton.A)

# Presionar múltiples botones
controller.press_buttons([SNESButton.A, SNESButton.B])

# Soltar todos
controller.release_all()
```

### 6. **Corrección del Mapeo de Botones**

#### Antes
```python
'SELECT': 1 << 2,  # Compartía bit con X ❌
'A': 1 << 12,      # Posición incorrecta
```

#### Después
```python
SELECT = 1 << 4   # Bit propio ✅
A = 1 << 12       # Consistente con serial_controller.py
```

### 7. **Funciones de Testing Actualizadas**

Todas las funciones de testing (`test_sequence`, `interactive_mode`, `continuous_spam`) se actualizaron para:
- Usar la nueva interfaz síncrona
- Trabajar con `SNESButton` enum
- Eliminar complejidad de async/await del código de test

## Impacto en Código Existente

### ⚠️ Breaking Changes

1. **Imports**:
   ```python
   # Antes
   from bt_controller import SNESControllerBLE, BUTTONS
   
   # Después
   from bt_controller import SNESControllerBLE, SNESButton
   ```

2. **Uso de botones**:
   ```python
   # Antes
   controller.send_buttons(BUTTONS['A'])
   
   # Después
   controller.send_buttons(SNESButton.A.value)
   # O mejor:
   controller.press_button(SNESButton.A)
   ```

3. **Conexión y envío**:
   ```python
   # Antes (async)
   controller = SNESControllerBLE()
   await controller.connect()
   await controller.send_buttons_async(mask)
   
   # Después (síncrono)
   controller = SNESControllerBLE()
   controller.connect()
   controller.send_buttons(mask)
   ```

### ✅ Código Compatible

El código que usa `send_buttons()` con máscaras de bits sigue funcionando:

```python
# Esto sigue funcionando
controller.send_buttons(0xFF)
controller.send_buttons((1 << 0) | (1 << 1))
```

## Ventajas del Refactor

1. **Simplicidad**: API síncrona más simple de usar
2. **Consistencia**: Misma interfaz que `serial_controller.py`
3. **Type Safety**: Uso de Enum en lugar de diccionarios
4. **Mantenibilidad**: Código más limpio y organizado
5. **Testing**: Más fácil de testear con interfaz uniforme
6. **Intercambiabilidad**: Puedes cambiar entre Serial y BLE sin cambiar el código cliente

## Estructura del Archivo Refactorizado

```
1. Imports y dependencias
2. Clase SNESButton (Enum)
3. Clase Controller (ABC)
4. Clase SNESControllerSerial
5. Clase SNESControllerBLE (refactorizada)
6. Funciones de testing (actualizadas)
7. Función main() (actualizada)
```

## Ejemplo de Uso (Antes vs Después)

### Antes
```python
import asyncio
from bt_controller import SNESControllerBLE, BUTTONS

async def main():
    controller = SNESControllerBLE()
    await controller.connect()
    
    # Presionar A
    await controller.send_buttons_async(BUTTONS['A'])
    await asyncio.sleep(0.5)
    await controller.send_buttons_async(0)
    
    await controller.disconnect()

asyncio.run(main())
```

### Después
```python
from bt_controller import SNESControllerBLE, SNESButton

controller = SNESControllerBLE()
controller.connect()

# Presionar A
controller.press_button(SNESButton.A)
time.sleep(0.5)
controller.release_all()

controller.close()
```

## Notas de Implementación

- Se mantiene la compatibilidad con `bleak` y `pyserial`
- Se conservan los UUIDs de BLE
- Se mantiene el baudrate de 115200 para Serial
- Las funciones de testing permanecen funcionales
- El modo interactivo sigue disponible

## Pruebas Recomendadas

Después de aplicar el refactor, probar:

1. ✅ Conexión BLE automática (por nombre)
2. ✅ Conexión BLE con dirección específica
3. ✅ Envío de botones individuales
4. ✅ Envío de combinaciones de botones
5. ✅ Modo interactivo
6. ✅ Modo turbo
7. ✅ Secuencia de test completa
8. ✅ Uso desde `sequence_player.py`

## Archivos Relacionados

- `/app/controllers/serial_controller.py` - Implementación de referencia
- `/app/controllers/bt_controller.py` - Archivo a refactorizar
- `/app/sequence_player.py` - Cliente principal que usa estos controladores
