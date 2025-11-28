#!/usr/bin/env python3
"""
SNES Controller Emulator - Controlador BLE

Este módulo proporciona una interfaz orientada a objetos para controlar
un emulador de controlador SNES vía Bluetooth BLE y USB Serial.

Protocolo: uint32_t (4 bytes, little-endian)
Baudrate (Serial): 115200
BLE Service UUID: 4fafc201-1fb5-459e-8fcc-c5c9c331914b
BLE Characteristic UUID: beb5483e-36e1-4688-b7f5-ea07361b26a8

Dependencias:
    pip install bleak pyserial
"""

import struct
import time
import sys
import asyncio
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List

# Intentar importar librerías (algunas pueden no estar instaladas)
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠️  pyserial no instalado. Instala con: pip install pyserial")

try:
    from bleak import BleakClient, BleakScanner
    BLE_AVAILABLE = True
except ImportError:
    BLE_AVAILABLE = False
    print("⚠️  bleak no instalado. Instala con: pip install bleak")

# BLE UUIDs (deben coincidir con el firmware ESP32)
BLE_SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
BLE_CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
BLE_DEVICE_NAME = "SNES Controller"  # Sin guión - así lo anuncia el ESP32


class SNESButton(Enum):
    """Enumeración de botones del SNES con sus valores de máscara."""

    B = 1 << 0  # Botón B (inferior derecha)
    Y = 1 << 1  # Botón Y (superior izquierda)
    X = 1 << 2  # Botón X (superior centro)
    START = 1 << 3  # Start
    SELECT = 1 << 4  # Select
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
        ...

    @abstractmethod
    def close(self) -> None:
        """Cierra la conexión con el dispositivo."""
        ...


class SNESControllerSerial(Controller):
    """Controlador para emulador SNES vía puerto serial."""

    def __init__(self, port: str = None):
        """
        Inicializa la conexión serial con el ESP32.

        Args:
            port: Puerto serial a usar. Si None, usa SNES_SERIAL_PORT
                  o '/dev/cu.usbserial-2120'
        """
        if port is None:
            port = os.environ.get("SNES_SERIAL_PORT", "/dev/cu.usbserial-2120")

        if not SERIAL_AVAILABLE:
            raise RuntimeError("pyserial no está instalado")

        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            print(f"✅ Conectado a {port} (Serial)")

            # Dar tiempo al ESP32 para inicializar
            time.sleep(2)

            # Leer mensajes de inicio del ESP32
            while self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8', errors='ignore')
                line = line.strip()
                if line:
                    print(f"ESP32: {line}")
        except serial.SerialException as e:
            msg = f"No se pudo conectar al puerto {port}: {e}"
            raise ConnectionError(msg) from e

    def send_buttons(self, button_mask: int) -> None:
        """
        Envía una máscara de botones al ESP32/SNES.

        Args:
            button_mask: uint32_t con los bits de botones activos
        """
        data = struct.pack('<I', button_mask)
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
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            print("✅ Conexión Serial cerrada")


class SNESControllerBLE(Controller):
    """Controlador para emulador SNES vía Bluetooth BLE."""

    def __init__(self, address: Optional[str] = None):
        """
        Inicializa el controlador BLE.

        Args:
            address: Dirección MAC del dispositivo BLE.
                     Si None, se busca por nombre.
        """
        if not BLE_AVAILABLE:
            raise RuntimeError("bleak no está instalado")

        self.address = address
        self.client: Optional[BleakClient] = None
        self.connected = False
        self._loop = None

    def _get_or_create_event_loop(self):
        """Obtiene el event loop actual o crea uno nuevo."""
        try:
            loop = asyncio.get_running_loop()
            return loop, False  # Loop existente, no cerrar
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop, True  # Loop nuevo, cerrar después

    def _run_async(self, coro):
        """Ejecuta una corrutina de manera síncrona."""
        loop, should_close = self._get_or_create_event_loop()
        try:
            if should_close:
                return loop.run_until_complete(coro)
            else:
                # Si ya estamos en un loop, crear una tarea
                return asyncio.create_task(coro)
        finally:
            if should_close and not loop.is_running():
                loop.close()

    def connect(self) -> None:
        """Conecta al dispositivo BLE de manera síncrona."""
        self._run_async(self._connect_async())

    async def _connect_async(self):
        """Conecta al dispositivo BLE (versión async interna)."""
        if self.address is None:
            # Buscar dispositivo por nombre
            print(f"🔍 Buscando dispositivo '{BLE_DEVICE_NAME}'...")
            devices = await BleakScanner.discover(timeout=10.0)

            for device in devices:
                if device.name == BLE_DEVICE_NAME:
                    self.address = device.address
                    print(f"✅ Encontrado: {device.name} "
                          f"({device.address})")
                    break

            if self.address is None:
                raise RuntimeError(
                    f"No se encontró '{BLE_DEVICE_NAME}'"
                )

        # Conectar al dispositivo
        print(f"🔗 Conectando a {self.address}...")
        self.client = BleakClient(self.address)
        await self.client.connect()
        self.connected = True
        print(f"✅ Conectado a {self.address} (BLE)")

        # Verificar que el servicio existe
        service_found = False
        for service in self.client.services:
            if service.uuid.lower() == BLE_SERVICE_UUID.lower():
                service_found = True
                break

        if not service_found:
            raise RuntimeError(
                f"Servicio {BLE_SERVICE_UUID} no encontrado"
            )

    def send_buttons(self, button_mask: int) -> None:
        """
        Envía una máscara de botones al ESP32/SNES vía BLE.

        Args:
            button_mask: uint32_t con los bits de botones activos
        """
        self._run_async(self._send_buttons_async(button_mask))

    async def _send_buttons_async(self, button_mask: int):
        """Envía datos por BLE (versión async interna)."""
        if not self.connected or self.client is None:
            raise RuntimeError("No conectado al dispositivo BLE")

        data = struct.pack('<I', button_mask)
        await self.client.write_gatt_char(BLE_CHARACTERISTIC_UUID, data)

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
        """Cierra la conexión BLE."""
        if self.connected:
            self._run_async(self._disconnect_async())

    async def _disconnect_async(self):
        """Desconecta del dispositivo BLE (versión async interna)."""
        if self.client and self.connected:
            await self.client.disconnect()
            self.connected = False
            print("✅ Conexión BLE cerrada")


def test_sequence(controller: Controller):
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
    dpad_sequence = [
        SNESButton.UP, SNESButton.RIGHT, SNESButton.DOWN, SNESButton.LEFT
    ]
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


def interactive_mode(controller: Controller):
    """Modo interactivo para enviar botones SNES"""
    print("\n=== Modo Interactivo SNES ===")
    print("\nBotones disponibles:")
    print("  Acción: A, B, X, Y")
    print("  D-Pad:  UP, DOWN, LEFT, RIGHT")
    print("  Hombro: L, R")
    print("  Sistema: SELECT, START")
    print("\nEscribe los nombres de botones separados por espacio")
    print("(ej: A B START)")
    print("Deja vacío para soltar todos los botones")
    print("Escribe 'quit' para salir\n")

    try:
        while True:
            user_input = input("> ").strip().upper()

            if user_input == 'QUIT':
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


def continuous_spam(controller: Controller, rate_hz: int = 60):
    """
    Envía inputs continuamente a una tasa específica

    Nota: El SNES lee a ~60 Hz, por lo que no tiene sentido
    enviar comandos más rápido que eso.
    """
    print(f"\n=== Modo Turbo a {rate_hz} Hz ===")
    print("Presionando A continuamente (turbo). Ctrl+C para detener")
    print("Nota: SNES lee a ~60 Hz, rate mayor no tendrá efecto\n")

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
                print(f"Enviados: {count} ciclos, "
                      f"Rate actual: {actual_rate:.1f} Hz")

    except KeyboardInterrupt:
        print("\nDetenido")
    finally:
        controller.release_all()


def main():
    """Punto de entrada del script"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    connection_type = sys.argv[1].lower()
    mode = sys.argv[3] if len(sys.argv) > 3 else 'test'

    controller: Optional[Controller] = None

    try:
        # Crear controlador según el tipo de conexión
        if connection_type == 'serial':
            if not SERIAL_AVAILABLE:
                print("❌ pyserial no instalado. "
                      "Instala con: pip install pyserial")
                sys.exit(1)

            if len(sys.argv) < 3:
                print("❌ Debes especificar el puerto serial")
                print("Ejemplo: python bt_controller.py serial /dev/ttyUSB0")
                sys.exit(1)

            port = sys.argv[2]
            controller = SNESControllerSerial(port)

        elif connection_type == 'ble':
            if not BLE_AVAILABLE:
                print("❌ bleak no instalado. "
                      "Instala con: pip install bleak")
                sys.exit(1)

            address = None
            if len(sys.argv) > 2 and not sys.argv[2].startswith('test'):
                address = sys.argv[2]

            controller = SNESControllerBLE(address)
            controller.connect()

        else:
            print(f"❌ Tipo de conexión desconocido: {connection_type}")
            print_usage()
            sys.exit(1)

        print()  # Línea en blanco

        # Ejecutar el modo seleccionado
        if mode == 'test':
            test_sequence(controller)
        elif mode == 'interactive':
            interactive_mode(controller)
        elif mode in ['turbo', 'spam']:
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


def print_usage():
    """Imprime información de uso del script"""
    print("SNES Controller Emulator - Script de Prueba (BLE + Serial)")
    print("=" * 60)
    print("\nUso: python3 bt_controller.py <tipo> [parámetro] [modo]")
    print("\nTipos de conexión:")
    print("  serial <puerto>    - Conexión vía USB Serial")
    print("  ble [dirección]    - Conexión vía Bluetooth BLE")
    print("                       (dirección opcional, se autodetecta)")
    print("\nModos disponibles:")
    print("  test        - Ejecuta secuencia completa de tests (default)")
    print("  interactive - Modo interactivo para control manual")
    print("  turbo       - Presiona A continuamente (modo turbo)")
    print("\nEjemplos:")
    print("  # Conexión Serial")
    print("  python3 bt_controller.py serial /dev/ttyUSB0")
    print("  python3 bt_controller.py serial /dev/ttyUSB0 test")
    print("  python3 bt_controller.py serial /dev/cu.usbserial-140 "
          "interactive")
    print()
    print("  # Conexión BLE (autodetección)")
    print("  python3 bt_controller.py ble")
    print("  python3 bt_controller.py ble test")
    print("  python3 bt_controller.py ble interactive")
    print()
    print("  # Conexión BLE (dirección específica)")
    print("  python3 bt_controller.py ble AA:BB:CC:DD:EE:FF")
    print("  python3 bt_controller.py ble AA:BB:CC:DD:EE:FF turbo")
    print("\nDependencias:")
    print("  pip install pyserial bleak")

    # Intentar listar puertos seriales disponibles
    if SERIAL_AVAILABLE:
        try:
            from serial.tools import list_ports
            ports = list_ports.comports()
            if ports:
                print("\nPuertos seriales detectados:")
                for port in ports:
                    print(f"  - {port.device}: {port.description}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
