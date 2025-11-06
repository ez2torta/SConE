#!/usr/bin/env python3
"""
Ejemplo de uso de SNES Controller con BLE
Muestra cómo integrar el controlador BLE en tus propios scripts
"""

import asyncio
import sys
import os

# Añadir el directorio examples al path para importar
sys.path.insert(0, os.path.dirname(__file__))

from test_ble_input import SNESControllerBLE, SNESControllerSerial, BUTTONS


async def example_ble_combo():
    """Ejemplo: Ejecutar un combo específico vía BLE"""
    print("=== Ejemplo: Combo Shoryuken (➡️⬇️↘️+A) vía BLE ===\n")
    
    # Conectar al controlador BLE
    controller = SNESControllerBLE()
    await controller.connect()
    
    print("Ejecutando Shoryuken...")
    
    # ➡️ Forward
    await controller.send_buttons_async(BUTTONS['RIGHT'])
    await asyncio.sleep(0.1)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.05)
    
    # ⬇️ Down
    await controller.send_buttons_async(BUTTONS['DOWN'])
    await asyncio.sleep(0.1)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.05)
    
    # ↘️ Down-Forward
    await controller.send_buttons_async(BUTTONS['DOWN'] | BUTTONS['RIGHT'])
    await asyncio.sleep(0.1)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.05)
    
    # + A (Punch)
    await controller.send_buttons_async(BUTTONS['A'])
    await asyncio.sleep(0.15)
    await controller.send_buttons_async(0)
    
    print("✅ Shoryuken ejecutado!")
    
    await controller.disconnect()


def example_serial_combo(port: str):
    """Ejemplo: Ejecutar un combo específico vía Serial"""
    print("=== Ejemplo: Combo Hadouken (⬇️↘️➡️+B) vía Serial ===\n")
    
    # Conectar al controlador Serial
    controller = SNESControllerSerial(port)
    
    print("Ejecutando Hadouken...")
    
    # ⬇️ Down
    controller.send_buttons(BUTTONS['DOWN'])
    import time
    time.sleep(0.1)
    controller.send_buttons(0)
    time.sleep(0.05)
    
    # ↘️ Down-Forward
    controller.send_buttons(BUTTONS['DOWN'] | BUTTONS['RIGHT'])
    time.sleep(0.1)
    controller.send_buttons(0)
    time.sleep(0.05)
    
    # ➡️ Forward
    controller.send_buttons(BUTTONS['RIGHT'])
    time.sleep(0.1)
    controller.send_buttons(0)
    time.sleep(0.05)
    
    # + B (Punch)
    controller.send_buttons(BUTTONS['B'])
    time.sleep(0.15)
    controller.send_buttons(0)
    
    print("✅ Hadouken ejecutado!")
    
    controller.close()


async def example_game_sequence():
    """Ejemplo: Secuencia de juego automatizada"""
    print("=== Ejemplo: Secuencia automatizada de juego ===\n")
    print("Simulando navegación de menú + inicio de partida\n")
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    # Navegar menú
    print("1. Navegando menú...")
    await controller.send_buttons_async(BUTTONS['DOWN'])
    await asyncio.sleep(0.3)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.2)
    
    await controller.send_buttons_async(BUTTONS['DOWN'])
    await asyncio.sleep(0.3)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.2)
    
    # Seleccionar opción
    print("2. Seleccionando opción (A)...")
    await controller.send_buttons_async(BUTTONS['A'])
    await asyncio.sleep(0.3)
    await controller.send_buttons_async(0)
    await asyncio.sleep(1.0)
    
    # Presionar START para comenzar
    print("3. Iniciando juego (START)...")
    await controller.send_buttons_async(BUTTONS['START'])
    await asyncio.sleep(0.3)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.5)
    
    # Simulación de gameplay básico
    print("4. Simulando gameplay...")
    
    # Caminar hacia la derecha
    print("   - Caminando →")
    await controller.send_buttons_async(BUTTONS['RIGHT'])
    await asyncio.sleep(1.0)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.2)
    
    # Saltar
    print("   - Saltando (B)")
    await controller.send_buttons_async(BUTTONS['B'])
    await asyncio.sleep(0.3)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.5)
    
    # Atacar
    print("   - Atacando (Y)")
    await controller.send_buttons_async(BUTTONS['Y'])
    await asyncio.sleep(0.2)
    await controller.send_buttons_async(0)
    
    print("\n✅ Secuencia completada!")
    
    await controller.disconnect()


async def example_turbo_button():
    """Ejemplo: Implementar botón turbo personalizado"""
    print("=== Ejemplo: Botón Turbo personalizado ===\n")
    print("Presionando B en modo turbo por 3 segundos...")
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    # Turbo a 30 Hz (presionar/soltar 15 veces por segundo)
    duration = 3.0  # segundos
    rate_hz = 30
    delay = 1.0 / rate_hz / 2  # Dividir por 2 para presionar/soltar
    
    start_time = asyncio.get_event_loop().time()
    count = 0
    
    while (asyncio.get_event_loop().time() - start_time) < duration:
        await controller.send_buttons_async(BUTTONS['B'])
        await asyncio.sleep(delay)
        await controller.send_buttons_async(0)
        await asyncio.sleep(delay)
        count += 1
    
    print(f"✅ Ejecutados {count} pulsos en {duration}s ({count/duration:.1f} Hz)")
    
    await controller.disconnect()


async def example_parallel_buttons():
    """Ejemplo: Presionar múltiples botones simultáneamente"""
    print("=== Ejemplo: Múltiples botones simultáneos ===\n")
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    # Ejemplo 1: Correr (RIGHT + Y)
    print("1. Correr hacia la derecha (RIGHT + Y)")
    combo = BUTTONS['RIGHT'] | BUTTONS['Y']
    await controller.send_buttons_async(combo)
    await asyncio.sleep(0.8)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.3)
    
    # Ejemplo 2: Salto con ataque (UP + A + B)
    print("2. Salto con ataque (UP + A + B)")
    combo = BUTTONS['UP'] | BUTTONS['A'] | BUTTONS['B']
    await controller.send_buttons_async(combo)
    await asyncio.sleep(0.5)
    await controller.send_buttons_async(0)
    await asyncio.sleep(0.3)
    
    # Ejemplo 3: Combo de hombros (L + R + START)
    print("3. Pausa con hombros (L + R + START)")
    combo = BUTTONS['L'] | BUTTONS['R'] | BUTTONS['START']
    await controller.send_buttons_async(combo)
    await asyncio.sleep(0.4)
    await controller.send_buttons_async(0)
    
    print("\n✅ Ejemplos de combos completados!")
    
    await controller.disconnect()


async def main():
    """Menú principal de ejemplos"""
    print("\n" + "="*60)
    print("SNES Controller - Ejemplos de Uso")
    print("="*60)
    print("\nSelecciona un ejemplo:")
    print("  1. Combo Shoryuken vía BLE (➡️⬇️↘️+A)")
    print("  2. Combo Hadouken vía Serial (⬇️↘️➡️+B)")
    print("  3. Secuencia automatizada de juego")
    print("  4. Botón turbo personalizado")
    print("  5. Múltiples botones simultáneos")
    print("  0. Ejecutar todos los ejemplos BLE")
    
    try:
        choice = input("\nOpción (0-5): ").strip()
        
        if choice == '1':
            await example_ble_combo()
        elif choice == '2':
            port = input("Puerto serial (ej: /dev/ttyUSB0): ").strip()
            example_serial_combo(port)
        elif choice == '3':
            await example_game_sequence()
        elif choice == '4':
            await example_turbo_button()
        elif choice == '5':
            await example_parallel_buttons()
        elif choice == '0':
            print("\n🚀 Ejecutando todos los ejemplos BLE...\n")
            await example_ble_combo()
            await asyncio.sleep(1)
            await example_game_sequence()
            await asyncio.sleep(1)
            await example_turbo_button()
            await asyncio.sleep(1)
            await example_parallel_buttons()
            print("\n✅ ¡Todos los ejemplos completados!")
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n💡 Asegúrate de que el ESP32 esté encendido y con el firmware BLE cargado")
    print("💡 Dependencias: pip install bleak pyserial\n")
    
    asyncio.run(main())
