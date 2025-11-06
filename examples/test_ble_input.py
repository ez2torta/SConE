#!/usr/bin/env python3
"""
Script de prueba para SNES Controller Emulator (ESP32) con soporte BLE

Este script envía comandos de botones al ESP32 vía USB Serial o Bluetooth BLE
que luego los transmite al SNES. Útil para testing y debugging.

Protocolo: uint32_t (4 bytes, little-endian)
Baudrate (Serial): 115200
BLE Service UUID: 4fafc201-1fb5-459e-8fcc-c5c9c331914b
BLE Characteristic UUID: beb5483e-36e1-4688-b7f5-ea07361b26a8

Dependencias para BLE:
    pip install bleak
"""

import struct
import time
import sys
import asyncio
from typing import Optional

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


class SNESController:
    """Clase base para comunicación con ESP32"""
    
    def send_buttons(self, button_mask: int):
        """
        Envía un mask de botones al ESP32/SNES
        Debe ser implementado por las subclases
        """
        raise NotImplementedError
    
    def close(self):
        """Cierra la conexión"""
        pass


class SNESControllerSerial(SNESController):
    """Comunicación vía USB Serial"""
    
    def __init__(self, port: str, baudrate: int = 115200):
        if not SERIAL_AVAILABLE:
            raise RuntimeError("pyserial no está instalado")
        
        self.ser = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ Conectado a {port} (Serial)")
        
        # Dar tiempo al ESP32 para inicializar
        time.sleep(2)
        
        # Leer mensajes de inicio del ESP32
        while self.ser.in_waiting:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"ESP32: {line}")
    
    def send_buttons(self, button_mask: int):
        data = struct.pack('<I', button_mask)
        self.ser.write(data)
        self.ser.flush()
    
    def close(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            print("✅ Conexión Serial cerrada")


class SNESControllerBLE(SNESController):
    """Comunicación vía Bluetooth BLE"""
    
    def __init__(self, address: Optional[str] = None):
        if not BLE_AVAILABLE:
            raise RuntimeError("bleak no está instalado")
        
        self.address = address
        self.client: Optional[BleakClient] = None
        self.connected = False
    
    async def connect(self):
        """Conecta al dispositivo BLE"""
        if self.address is None:
            # Buscar dispositivo por nombre
            print(f"🔍 Buscando dispositivo '{BLE_DEVICE_NAME}'...")
            devices = await BleakScanner.discover(timeout=10.0)
            
            for device in devices:
                if device.name == BLE_DEVICE_NAME:
                    self.address = device.address
                    print(f"✅ Dispositivo encontrado: {device.name} ({device.address})")
                    break
            
            if self.address is None:
                raise RuntimeError(f"No se encontró el dispositivo '{BLE_DEVICE_NAME}'")
        
        # Conectar al dispositivo
        print(f"🔗 Conectando a {self.address}...")
        self.client = BleakClient(self.address)
        await self.client.connect()
        self.connected = True
        print(f"✅ Conectado a {self.address} (BLE)")
        
        # Verificar que el servicio existe (services es una propiedad en bleak)
        service_found = False
        for service in self.client.services:
            if service.uuid.lower() == BLE_SERVICE_UUID.lower():
                service_found = True
                break
        
        if not service_found:
            raise RuntimeError(f"Servicio {BLE_SERVICE_UUID} no encontrado")
    
    def send_buttons(self, button_mask: int):
        """
        Versión síncrona - NO usar con BLE en contexto async
        Esta versión solo funciona si se llama desde código no-async
        """
        raise RuntimeError("No uses send_buttons() con BLE. Usa send_buttons_async() en un contexto async")
    
    async def send_buttons_async(self, button_mask: int):
        """Envía datos por BLE (versión async) - USAR ESTA"""
        if not self.connected or self.client is None:
            raise RuntimeError("No conectado al dispositivo BLE")
        
        data = struct.pack('<I', button_mask)
        await self.client.write_gatt_char(BLE_CHARACTERISTIC_UUID, data)
    
    async def disconnect(self):
        """Desconecta del dispositivo BLE"""
        if self.client and self.connected:
            await self.client.disconnect()
            self.connected = False
            print("✅ Conexión BLE cerrada")
    
    def close(self):
        """Versión síncrona de disconnect"""
        asyncio.run(self.disconnect())


async def test_sequence(controller):
    """Ejecuta una secuencia de prueba para botones SNES (async para BLE)"""
    print("=== Iniciando secuencia de prueba SNES ===\n")
    
    # Función auxiliar para enviar botones (maneja tanto Serial como BLE)
    async def send(mask):
        if isinstance(controller, SNESControllerBLE):
            await controller.send_buttons_async(mask)
        else:
            controller.send_buttons(mask)
    
    # Test 1: Botones de acción
    print("Test 1: Botones de acción")
    action_buttons = ['B', 'Y', 'A', 'X']
    for name in action_buttons:
        print(f"  Presionando {name}...")
        await send(BUTTONS[name])
        await asyncio.sleep(0.4)
        await send(0)  # Soltar
        await asyncio.sleep(0.2)
    
    # Test 2: D-Pad
    print("\nTest 2: D-Pad (direccionales)")
    dpad_sequence = ['UP', 'RIGHT', 'DOWN', 'LEFT']
    for direction in dpad_sequence:
        print(f"  D-Pad {direction}")
        await send(BUTTONS[direction])
        await asyncio.sleep(0.4)
        await send(0)
        await asyncio.sleep(0.2)
    
    # Test 3: Botones de hombro
    print("\nTest 3: Botones de hombro")
    for name in ['L', 'R']:
        print(f"  Presionando {name}...")
        await send(BUTTONS[name])
        await asyncio.sleep(0.4)
        await send(0)
        await asyncio.sleep(0.2)
    
    # Test 4: Botones de sistema
    print("\nTest 4: Botones de sistema")
    for name in ['SELECT', 'START']:
        print(f"  Presionando {name}...")
        await send(BUTTONS[name])
        await asyncio.sleep(0.4)
        await send(0)
        await asyncio.sleep(0.2)
    
    # Test 5: Combos comunes
    print("\nTest 5: Combinaciones comunes")
    
    print("  A + B (combo clásico)")
    combo = BUTTONS['A'] | BUTTONS['B']
    await send(combo)
    await asyncio.sleep(0.5)
    await send(0)
    await asyncio.sleep(0.3)
    
    print("  UP + A (salto hacia arriba)")
    combo = BUTTONS['UP'] | BUTTONS['A']
    await send(combo)
    await asyncio.sleep(0.5)
    await send(0)
    await asyncio.sleep(0.3)
    
    print("  L + R (combo de hombros)")
    combo = BUTTONS['L'] | BUTTONS['R']
    await send(combo)
    await asyncio.sleep(0.5)
    await send(0)
    await asyncio.sleep(0.3)
    
    print("  START + SELECT (pausa/reset)")
    combo = BUTTONS['START'] | BUTTONS['SELECT']
    await send(combo)
    await asyncio.sleep(0.5)
    await send(0)
    
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
        await send(BUTTONS[button])
        await asyncio.sleep(0.3)
        await send(0)
        await asyncio.sleep(0.2)
    
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
            
            if user_input == 'QUIT':
                break
            
            if not user_input:
                # Sin input = soltar todos los botones
                controller.send_buttons(0)
                continue
            
            button_names = user_input.split()
            mask = 0
            
            for name in button_names:
                if name in BUTTONS:
                    mask |= BUTTONS[name]
                else:
                    print(f"Botón desconocido: {name}")
            
            controller.send_buttons(mask)
            print(f"Enviado: 0x{mask:04X}")
            
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    finally:
        # Soltar todos los botones al salir
        controller.send_buttons(0)


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
            controller.send_buttons(BUTTONS['A'])
            time.sleep(delay / 2)
            controller.send_buttons(0)
            time.sleep(delay / 2)
            count += 1
            
            if count % rate_hz == 0:  # Cada segundo
                elapsed = time.time() - start_time
                actual_rate = count / elapsed
                print(f"Enviados: {count} ciclos, Rate actual: {actual_rate:.1f} Hz")
    
    except KeyboardInterrupt:
        print("\nDetenido")
    finally:
        controller.send_buttons(0)


async def async_main():
    """Función principal async para manejar BLE"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    connection_type = sys.argv[1].lower()
    mode = sys.argv[3] if len(sys.argv) > 3 else 'test'
    
    controller: Optional[SNESController] = None
    
    try:
        # Crear controlador según el tipo de conexión
        if connection_type == 'serial':
            if not SERIAL_AVAILABLE:
                print("❌ pyserial no instalado. Instala con: pip install pyserial")
                sys.exit(1)
            
            if len(sys.argv) < 3:
                print("❌ Debes especificar el puerto serial")
                print("Ejemplo: python test_ble_input.py serial /dev/ttyUSB0")
                sys.exit(1)
            
            port = sys.argv[2]
            controller = SNESControllerSerial(port)
        
        elif connection_type == 'ble':
            if not BLE_AVAILABLE:
                print("❌ bleak no instalado. Instala con: pip install bleak")
                sys.exit(1)
            
            address = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('test') else None
            controller = SNESControllerBLE(address)
            await controller.connect()
        
        else:
            print(f"❌ Tipo de conexión desconocido: {connection_type}")
            print_usage()
            sys.exit(1)
        
        print()  # Línea en blanco
        
        # Ejecutar el modo seleccionado
        if mode == 'test':
            await test_sequence(controller)
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
            if isinstance(controller, SNESControllerBLE):
                await controller.disconnect()
            else:
                controller.close()


def print_usage():
    """Imprime información de uso del script"""
    print("SNES Controller Emulator - Script de Prueba (BLE + Serial)")
    print("=" * 60)
    print("\nUso: python3 test_ble_input.py <tipo> [parámetro] [modo]")
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
    print("  python3 test_ble_input.py serial /dev/ttyUSB0")
    print("  python3 test_ble_input.py serial /dev/ttyUSB0 test")
    print("  python3 test_ble_input.py serial /dev/cu.usbserial-140 interactive")
    print()
    print("  # Conexión BLE (autodetección)")
    print("  python3 test_ble_input.py ble")
    print("  python3 test_ble_input.py ble test")
    print("  python3 test_ble_input.py ble interactive")
    print()
    print("  # Conexión BLE (dirección específica)")
    print("  python3 test_ble_input.py ble AA:BB:CC:DD:EE:FF")
    print("  python3 test_ble_input.py ble AA:BB:CC:DD:EE:FF turbo")
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
        except:
            pass


def main():
    """Punto de entrada del script"""
    # Usar asyncio para soportar BLE
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
