#!/usr/bin/env python3
"""
Script de prueba BLE para SNES Controller Emulator (ESP32)

Este script envía comandos de botones al ESP32 vía Bluetooth LE
que luego los transmite al SNES. Útil para testing y debugging.

Protocolo: uint32_t (4 bytes, little-endian)
Requiere: pip install bleak

Basado en test_serial_input.py pero usando BLE en lugar de Serial
"""

import asyncio
import struct
import time
import sys
from bleak import BleakScanner, BleakClient

# UUIDs del servicio BLE (deben coincidir con el ESP32)
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

# Mapeo de botones específico para SNES
# El SNES tiene 12 botones: 4 direccionales, 6 de acción, 2 auxiliares
BUTTONS = {
    # Botones de acción (4 botones principales)
    'B':      1 << 0,   # Botón B (inferior derecha)
    'Y':      1 << 1,   # Botón Y (superior izquierda)
    'A':      1 << 12,  # Botón A (superior derecha)
    'X':      1 << 2,   # Botón X (superior centro)

    # Botones de hombro (2 botones)
    'L':      1 << 6,   # Hombro izquierdo
    'R':      1 << 7,   # Hombro derecho

    # Botones de sistema (2 botones)
    'SELECT': 1 << 2,   # Select (comparte bit con X)
    'START':  1 << 3,   # Start

    # D-Pad (4 direcciones)
    'UP':     1 << 8,   # Arriba
    'DOWN':   1 << 9,   # Abajo
    'LEFT':   1 << 10,  # Izquierda
    'RIGHT':  1 << 11,  # Derecha
}

class SNESBLEController:
    def __init__(self):
        self.client = None
        self.device = None

    async def scan_and_connect(self):
        """Escanea dispositivos BLE y conecta al SNES Controller"""
        print("Escaneando dispositivos BLE...")

        devices = await BleakScanner.discover()
        snes_device = None

        for device in devices:
            if device.name and "SNES Controller" in device.name:
                snes_device = device
                break

        if not snes_device:
            print("❌ No se encontró el dispositivo 'SNES Controller'")
            print("Asegúrate de que el ESP32 esté encendido y transmitiendo")
            return False

        print(f"Conectando a {snes_device.name} ({snes_device.address})...")
        self.client = BleakClient(snes_device)

        try:
            await self.client.connect()
            if self.client.is_connected:
                print("✅ Conectado exitosamente!")
                return True
            else:
                print("❌ Error al conectar")
                return False
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    async def send_buttons(self, button_mask):
        """
        Envía un mask de botones al ESP32/SNES vía BLE

        Args:
            button_mask: uint32_t con los bits de botones activos
        """
        if not self.client or not self.client.is_connected:
            print("❌ No conectado al dispositivo")
            return False

        # Convertir uint32_t a bytes little-endian (igual que Serial)
        data = struct.pack('<I', button_mask)

        # Debug: mostrar bytes que se envían
        byte0, byte1, byte2, byte3 = data
        print(f"Enviando bytes (little-endian): {byte0:02X} {byte1:02X} {byte2:02X} {byte3:02X} (0x{button_mask:08X})")

        try:
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, data)
            print(f"✅ Enviado: 0x{button_mask:08X}")
            return True
        except Exception as e:
            print(f"❌ Error al enviar: {e}")
            return False

    async def disconnect(self):
        """Desconecta del dispositivo"""
        if self.client:
            try:
                await self.client.disconnect()
                print("✅ Desconectado")
            except:
                pass

async def test_sequence(controller):
    """Ejecuta una secuencia de prueba para botones SNES vía BLE"""
    print("=== Iniciando secuencia de prueba SNES vía BLE ===\n")

    # Test 1: Botones de acción
    print("Test 1: Botones de acción")
    action_buttons = ['B', 'Y', 'A', 'X']
    for name in action_buttons:
        print(f"  Presionando {name}...")
        await controller.send_buttons(BUTTONS[name])
        await asyncio.sleep(0.4)
        await controller.send_buttons(0)  # Soltar
        await asyncio.sleep(0.2)

    # Test 2: D-Pad
    print("\nTest 2: D-Pad (direccionales)")
    dpad_sequence = ['UP', 'RIGHT', 'DOWN', 'LEFT']
    for direction in dpad_sequence:
        print(f"  D-Pad {direction}")
        await controller.send_buttons(BUTTONS[direction])
        await asyncio.sleep(0.4)
        await controller.send_buttons(0)
        await asyncio.sleep(0.2)

    # Test 3: Botones de hombro
    print("\nTest 3: Botones de hombro")
    for name in ['L', 'R']:
        print(f"  Presionando {name}...")
        await controller.send_buttons(BUTTONS[name])
        await asyncio.sleep(0.4)
        await controller.send_buttons(0)
        await asyncio.sleep(0.2)

    # Test 4: Botones de sistema
    print("\nTest 4: Botones de sistema")
    for name in ['SELECT', 'START']:
        print(f"  Presionando {name}...")
        await controller.send_buttons(BUTTONS[name])
        await asyncio.sleep(0.4)
        await controller.send_buttons(0)
        await asyncio.sleep(0.2)

    # Test 5: Combos comunes
    print("\nTest 5: Combinaciones comunes")

    print("  A + B (combo clásico)")
    combo = BUTTONS['A'] | BUTTONS['B']
    await controller.send_buttons(combo)
    await asyncio.sleep(0.5)
    await controller.send_buttons(0)
    await asyncio.sleep(0.3)

    print("  UP + A (salto hacia arriba)")
    combo = BUTTONS['UP'] | BUTTONS['A']
    await controller.send_buttons(combo)
    await asyncio.sleep(0.5)
    await controller.send_buttons(0)
    await asyncio.sleep(0.3)

    print("  L + R (combo de hombros)")
    combo = BUTTONS['L'] | BUTTONS['R']
    await controller.send_buttons(combo)
    await asyncio.sleep(0.5)
    await controller.send_buttons(0)
    await asyncio.sleep(0.3)

    print("  START + SELECT (pausa/reset)")
    combo = BUTTONS['START'] | BUTTONS['SELECT']
    await controller.send_buttons(combo)
    await asyncio.sleep(0.5)
    await controller.send_buttons(0)

    # Test 6: Konami Code!
    print("\nTest 6: Konami Code! ⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️🅱️🅰️")
    konami = [
        ('UP', "⬆️  UP"),
        ('UP', "⬆️  UP"),
        ('DOWN', "⬇️  DOWN"),
        ('DOWN', "⬇️  DOWN"),
        ('LEFT', "⬅️  LEFT"),
        ('RIGHT', "➡️  RIGHT"),
        ('LEFT', "⬅️  LEFT"),
        ('RIGHT', "➡️  RIGHT"),
        ('B', "🅱️  B"),
        ('A', "🅰️  A"),
    ]

    for button, label in konami:
        print(f"  {label}")
        await controller.send_buttons(BUTTONS[button])
        await asyncio.sleep(0.3)
        await controller.send_buttons(0)
        await asyncio.sleep(0.2)

    print("\n=== Test completado! ===")

async def interactive_mode(controller):
    """Modo interactivo para enviar botones SNES vía BLE"""
    print("\n=== Modo Interactivo SNES vía BLE ===")
    print("\nBotones disponibles:")
    print("  Acción: A, B, X, Y")
    print("  D-Pad:  UP, DOWN, LEFT, RIGHT")
    print("  Hombro: L, R")
    print("  Sistema: SELECT, START")
    print("\nEscribe los nombres de botones separados por espacio (ej: A B START)")
    print("Deja vacío para soltar todos los botones")
    print("Escribe 'quit' para salir\n")

    try:
        while True:
            # Usar asyncio para input no bloqueante
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(None, input, "> ")
            user_input = user_input.strip().upper()

            if user_input == 'QUIT':
                break

            if not user_input:
                # Sin input = soltar todos los botones
                await controller.send_buttons(0)
                continue

            button_names = user_input.split()
            mask = 0

            for name in button_names:
                if name in BUTTONS:
                    mask |= BUTTONS[name]
                else:
                    print(f"❌ Botón desconocido: {name}")

            await controller.send_buttons(mask)
            print(f"Enviado: 0x{mask:04X}")

    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except Exception as e:
        print(f"❌ Error en modo interactivo: {e}")
    finally:
        # Soltar todos los botones al salir
        await controller.send_buttons(0)

async def continuous_spam(controller, rate_hz=60):
    """
    Envía inputs continuamente a una tasa específica vía BLE

    Nota: El SNES lee a ~60 Hz, por lo que no tiene sentido
    enviar comandos más rápido que eso.
    """
    print(f"\n=== Modo Turbo a {rate_hz} Hz vía BLE ===")
    print("Presionando A continuamente (turbo). Ctrl+C para detener")
    print("Nota: SNES lee a ~60 Hz, rate mayor no tendrá efecto adicional\n")

    delay = 1.0 / rate_hz
    count = 0

    try:
        start_time = time.time()
        while True:
            # Alternar entre presionado y soltado para efecto turbo
            success = await controller.send_buttons(BUTTONS['A'])
            if not success:
                print("❌ Error en envío, deteniendo turbo")
                break
            await asyncio.sleep(delay / 2)

            success = await controller.send_buttons(0)
            if not success:
                print("❌ Error en envío, deteniendo turbo")
                break
            await asyncio.sleep(delay / 2)

            count += 1

            if count % rate_hz == 0:  # Cada segundo
                elapsed = time.time() - start_time
                actual_rate = count / elapsed
                print(f"Enviados: {count} ciclos, Rate actual: {actual_rate:.1f} Hz")

    except KeyboardInterrupt:
        print("\nDetenido")
    except Exception as e:
        print(f"❌ Error en modo turbo: {e}")
    finally:
        await controller.send_buttons(0)

async def main():
    if len(sys.argv) < 2:
        print("SNES Controller Emulator - Script de Prueba BLE")
        print("=" * 55)
        print("\nUso: python3 test_ble_input.py <modo>")
        print("\nModos disponibles:")
        print("  test        - Ejecuta secuencia completa de tests (default)")
        print("  interactive - Modo interactivo para control manual")
        print("  turbo       - Presiona A continuamente (modo turbo)")
        print("\nEjemplos:")
        print("  python3 test_ble_input.py test")
        print("  python3 test_ble_input.py interactive")
        print("  python3 test_ble_input.py turbo")
        print("\nRequisitos:")
        print("  pip install bleak")
        print("  ESP32 con firmware BLE encendido")

        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else 'test'

    controller = SNESBLEController()

    try:
        print("SNES Controller Emulator - Conectando vía BLE...")
        if not await controller.scan_and_connect():
            print("❌ No se pudo conectar. Verifica que el ESP32 esté encendido.")
            return

        # Dar tiempo para que el ESP32 esté listo
        await asyncio.sleep(1)

        print()  # Línea en blanco

        if mode == 'test':
            await test_sequence(controller)
        elif mode == 'interactive':
            await interactive_mode(controller)
        elif mode in ['turbo', 'spam']:
            await continuous_spam(controller)
        else:
            print(f"❌ Modo desconocido: {mode}")
            print("Modos disponibles: test, interactive, turbo")

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await controller.disconnect()

if __name__ == "__main__":
    asyncio.run(main())