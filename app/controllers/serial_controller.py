#!/usr/bin/env python3
"""
SNES Controller Emulator - Controlador Principal

Este módulo proporciona una interfaz orientada a objetos para controlar
un emulador de controlador SNES vía puerto serial. Incluye tipos y
interfaces para facilitar el uso como un controlador de videojuegos.

Protocolo: uint32_t (4 bytes, little-endian)
Baudrate: 115200
"""

import os
import serial
import struct
import time
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class SNESButton(Enum):
    """Enumeración de botones del SNES con sus valores de máscara."""

    B = 1 << 0  # Botón B (inferior derecha)
    Y = 1 << 1  # Botón Y (superior izquierda)
    X = 1 << 2  # Botón X (superior centro)
    START = 1 << 3  # Start
    SELECT = 1 << 4  # Select (corregido para no compartir con X)
    L = 1 << 6  # Hombro izquierdo
    R = 1 << 7  # Hombro derecho
    UP = 1 << 8  # Arriba
    DOWN = 1 << 9  # Abajo
    LEFT = 1 << 10  # Izquierda
    RIGHT = 1 << 11  # Derecha
    A = 1 << 12  # Botón A (superior derecha)


class Controller(ABC):
    """Interfaz abstracta para controladores de videojuegos."""

    @abstractmethod
    def send_buttons(self, button_mask: int) -> None:
        """Envía una máscara de botones al dispositivo."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Cierra la conexión con el dispositivo."""
        pass


class SNESController(Controller):
    """Controlador para emulador SNES vía puerto serial."""

    def __init__(self, port: str = None):
        """
        Inicializa la conexión serial con el ESP32.

        Args:
            port: Puerto serial a usar. Si None, usa SNES_SERIAL_PORT o '/dev/cu.usbserial-2120'
        """
        if port is None:
            port = os.environ.get("SNES_SERIAL_PORT", "/dev/cu.usbserial-2120")

        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            print(f"✅ Conectado a {port}")
            # Dar tiempo al ESP32 para inicializar
            time.sleep(2)
            # Leer mensajes de inicio
            while self.ser.in_waiting:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(f"ESP32: {line}")
        except serial.SerialException as e:
            raise ConnectionError(f"No se pudo conectar al puerto {port}: {e}")

    def send_buttons(self, button_mask: int) -> None:
        """
        Envía una máscara de botones al ESP32/SNES.

        Args:
            button_mask: uint32_t con los bits de botones activos
        """
        data = struct.pack("<I", button_mask)
        self.ser.write(data)
        self.ser.flush()

    def press_button(self, button: SNESButton) -> None:
        """
        Presiona un botón específico.

        Args:
            button: El botón a presionar
        """
        self.send_buttons(button.value)

    def press_buttons(self, buttons: List[SNESButton]) -> None:
        """
        Presiona múltiples botones simultáneamente.

        Args:
            buttons: Lista de botones a presionar
        """
        mask = 0
        for button in buttons:
            mask |= button.value
        self.send_buttons(mask)

    def release_all(self) -> None:
        """Suelta todos los botones."""
        self.send_buttons(0)

    def close(self) -> None:
        """Cierra la conexión serial."""
        if hasattr(self, "ser"):
            self.ser.close()
            print("✅ Conexión cerrada")


def test_sequence(controller: SNESController):
    """Ejecuta una secuencia de prueba para botones SNES"""
    print("=== Iniciando secuencia de prueba SNES ===\n")

    # Test 1: Botones de acción
    print("Test 1: Botones de acción")
    action_buttons = [SNESButton.B, SNESButton.Y, SNESButton.A, SNESButton.X]
    for button in action_buttons:
        print(f"  Presionando {button.name}...")
        controller.press_button(button)
        time.sleep(0.4)
        controller.release_all()
        time.sleep(0.2)

    # Test 2: D-Pad
    print("\nTest 2: D-Pad (direccionales)")
    dpad_sequence = [SNESButton.UP, SNESButton.RIGHT, SNESButton.DOWN, SNESButton.LEFT]
    for direction in dpad_sequence:
        print(f"  D-Pad {direction.name}")
        controller.press_button(direction)
        time.sleep(0.4)
        controller.release_all()
        time.sleep(0.2)

    # Test 3: Botones de hombro
    print("\nTest 3: Botones de hombro")
    for button in [SNESButton.L, SNESButton.R]:
        print(f"  Presionando {button.name}...")
        controller.press_button(button)
        time.sleep(0.4)
        controller.release_all()
        time.sleep(0.2)

    # Test 4: Botones de sistema
    print("\nTest 4: Botones de sistema")
    for button in [SNESButton.SELECT, SNESButton.START]:
        print(f"  Presionando {button.name}...")
        controller.press_button(button)
        time.sleep(0.4)
        controller.release_all()
        time.sleep(0.2)

    # Test 5: Combos comunes
    print("\nTest 5: Combinaciones comunes")

    print("  A + B (combo clásico)")
    controller.press_buttons([SNESButton.A, SNESButton.B])
    time.sleep(0.5)
    controller.release_all()
    time.sleep(0.3)

    print("  UP + A (salto hacia arriba)")
    controller.press_buttons([SNESButton.UP, SNESButton.A])
    time.sleep(0.5)
    controller.release_all()
    time.sleep(0.3)

    print("  L + R (combo de hombros)")
    controller.press_buttons([SNESButton.L, SNESButton.R])
    time.sleep(0.5)
    controller.release_all()
    time.sleep(0.3)

    print("  START + SELECT (pausa/reset)")
    controller.press_buttons([SNESButton.START, SNESButton.SELECT])
    time.sleep(0.5)
    controller.release_all()

    # Test 6: Konami Code!
    print("\nTest 6: Konami Code! ⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️🅱️🅰️")
    konami = [
        (SNESButton.UP, "⬆️  UP"),
        (SNESButton.UP, "⬆️  UP"),
        (SNESButton.DOWN, "⬇️  DOWN"),
        (SNESButton.DOWN, "⬇️  DOWN"),
        (SNESButton.LEFT, "⬅️  LEFT"),
        (SNESButton.RIGHT, "➡️  RIGHT"),
        (SNESButton.LEFT, "⬅️  LEFT"),
        (SNESButton.RIGHT, "➡️  RIGHT"),
        (SNESButton.B, "🅱️  B"),
        (SNESButton.A, "🅰️  A"),
    ]

    for button, label in konami:
        print(f"  {label}")
        controller.press_button(button)
        time.sleep(0.3)
        controller.release_all()
        time.sleep(0.2)

    print("\n=== Test completado! ===")


def interactive_mode(controller: SNESController):
    """Modo interactivo para enviar botones SNES"""
    print("\n=== Modo Interactivo SNES ===")
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
            user_input = input("> ").strip().upper()

            if user_input == "QUIT":
                break

            if not user_input:
                # Sin input = soltar todos los botones
                controller.release_all()
                continue

            button_names = user_input.split()
            buttons = []

            for name in button_names:
                try:
                    button = SNESButton[name]
                    buttons.append(button)
                except KeyError:
                    print(f"Botón desconocido: {name}")

            if buttons:
                controller.press_buttons(buttons)
                mask = sum(b.value for b in buttons)
                print(f"Enviado: 0x{mask:04X}")

    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    finally:
        # Soltar todos los botones al salir
        controller.release_all()


def continuous_spam(controller: SNESController, rate_hz: int = 60):
    """
    Envía inputs continuamente a una tasa específica

    Nota: El SNES lee a ~60 Hz, por lo que no tiene sentido
    enviar comandos más rápido que eso.
    """
    print(f"\n=== Modo Turbo a {rate_hz} Hz ===")
    print("Presionando A continuamente (turbo). Ctrl+C para detener")
    print("Nota: SNES lee a ~60 Hz, rate mayor no tendrá efecto adicional\n")

    delay = 1.0 / rate_hz
    count = 0

    try:
        start_time = time.time()
        while True:
            # Alternar entre presionado y soltado para efecto turbo
            controller.press_button(SNESButton.A)
            time.sleep(delay / 2)
            controller.release_all()
            time.sleep(delay / 2)
            count += 1

            if count % rate_hz == 0:  # Cada segundo
                elapsed = time.time() - start_time
                actual_rate = count / elapsed
                print(f"Enviados: {count} ciclos, Rate actual: {actual_rate:.1f} Hz")

    except KeyboardInterrupt:
        print("\nDetenido")
    finally:
        controller.release_all()


def main():
    if len(sys.argv) < 2:
        print("SNES Controller Emulator - Script de Prueba")
        print("=" * 50)
        print("\nUso: python3 test_serial_input.py <puerto_serial> [modo]")
        print("\nPuertos comunes:")
        print("  Linux:   /dev/ttyUSB0, /dev/ttyACM0")
        print("  macOS:   /dev/cu.usbserial-XXXX")
        print("  Windows: COM3, COM4, etc.")
        print("\nModos disponibles:")
        print("  test        - Ejecuta secuencia completa de tests (default)")
        print("  interactive - Modo interactivo para control manual")
        print("  turbo       - Presiona A continuamente (modo turbo)")
        print("\nEjemplos:")
        print("  python3 test_serial_input.py /dev/ttyUSB0")
        print("  python3 test_serial_input.py /dev/ttyUSB0 test")
        print("  python3 test_serial_input.py /dev/ttyUSB0 interactive")
        print("  python3 test_serial_input.py /dev/cu.usbserial-140 turbo")

        # Intentar listar puertos disponibles
        try:
            from serial.tools import list_ports

            ports = list_ports.comports()
            if ports:
                print("\nPuertos seriales detectados:")
                for port in ports:
                    print(f"  - {port.device}: {port.description}")
        except:
            pass

        sys.exit(1)

    port = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "test"

    controller = None
    try:
        controller = SNESController(port)

        if mode == "test":
            test_sequence(controller)
        elif mode == "interactive":
            interactive_mode(controller)
        elif mode in ["turbo", "spam"]:
            continuous_spam(controller)
        else:
            print(f"❌ Modo desconocido: {mode}")
            print("Modos disponibles: test, interactive, turbo")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if controller:
            controller.close()


if __name__ == "__main__":
    main()
