#!/usr/bin/env python3
"""
Ejemplo de cliente BLE para controlar el emulador SNES via Bluetooth

Requiere: pip install bleak

Uso:
1. Ejecuta este script
2. El script escaneará dispositivos BLE
3. Selecciona el dispositivo "SNES Controller"
4. Una vez conectado, puedes enviar comandos

Mapeo de bits para el uint32_t:
  bit 0  = B
  bit 1  = Y
  bit 2  = Select / X
  bit 3  = Start
  bit 4  = (n/a)
  bit 5  = (n/a)
  bit 6  = L
  bit 7  = R
  bit 8  = D-Up
  bit 9  = D-Down
  bit 10 = D-Left
  bit 11 = D-Right
  bit 12 = A
  bit 13 = (n/a)
  bit 14 = (n/a)
  bit 15 = (n/a)
"""

import asyncio
import struct
from bleak import BleakScanner, BleakClient

# UUIDs del servicio BLE (deben coincidir con el ESP32)
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class SNESController:
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
            print("No se encontró el dispositivo SNES Controller")
            return False

        print(f"Conectando a {snes_device.name} ({snes_device.address})...")
        self.client = BleakClient(snes_device)
        await self.client.connect()

        if self.client.is_connected:
            print("Conectado exitosamente!")
            return True
        else:
            print("Error al conectar")
            return False

    async def send_buttons(self, button_mask):
        """Envía el estado de los botones como uint32_t (igual que Serial)"""
        if not self.client or not self.client.is_connected:
            print("No conectado al dispositivo")
            return

        # Convertir uint32_t a bytes little-endian (igual que Serial.write en Arduino)
        data = struct.pack('<I', button_mask)

        # Debug: mostrar bytes que se envían (igual que Serial)
        byte0, byte1, byte2, byte3 = data
        print(f"Enviando bytes (little-endian): {byte0:02X} {byte1:02X} {byte2:02X} {byte3:02X} (0x{button_mask:08X})")

        try:
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, data)
            print(f"✅ Enviado: 0x{button_mask:08X}")
        except Exception as e:
            print(f"❌ Error al enviar: {e}")

    async def disconnect(self):
        """Desconecta del dispositivo"""
        if self.client:
            await self.client.disconnect()
            print("Desconectado")

async def main():
    controller = SNESController()

    try:
        if not await controller.scan_and_connect():
            return

        print("\nControles:")
        print("w/s/a/d - D-Pad (arriba/abajo/izquierda/derecha)")
        print("j/k     - Botones A/B")
        print("u/i     - Botones X/Y")
        print("q/e     - Botones L/R")
        print("space   - Select")
        print("enter   - Start")
        print("r       - Reset (todos los botones sueltos)")
        print("x       - Salir")

        # Definir máscaras de botones
        BUTTON_A = 1 << 12
        BUTTON_B = 1 << 0
        BUTTON_X = 1 << 2
        BUTTON_Y = 1 << 1
        BUTTON_L = 1 << 6
        BUTTON_R = 1 << 7
        BUTTON_SELECT = 1 << 2  # Compartido con X
        BUTTON_START = 1 << 3
        DPAD_UP = 1 << 8
        DPAD_DOWN = 1 << 9
        DPAD_LEFT = 1 << 10
        DPAD_RIGHT = 1 << 11

        current_buttons = 0

        while True:
            # Leer entrada del teclado (no bloqueante)
            try:
                import sys
                import select

                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()
                else:
                    continue

                if key == 'x':
                    break
                elif key == 'r':
                    current_buttons = 0
                elif key == 'w':
                    current_buttons |= DPAD_UP
                elif key == 's':
                    current_buttons |= DPAD_DOWN
                elif key == 'a':
                    current_buttons |= DPAD_LEFT
                elif key == 'd':
                    current_buttons |= DPAD_RIGHT
                elif key == 'j':
                    current_buttons |= BUTTON_A
                elif key == 'k':
                    current_buttons |= BUTTON_B
                elif key == 'u':
                    current_buttons |= BUTTON_X
                elif key == 'i':
                    current_buttons |= BUTTON_Y
                elif key == 'q':
                    current_buttons |= BUTTON_L
                elif key == 'e':
                    current_buttons |= BUTTON_R
                elif key == ' ':
                    current_buttons |= BUTTON_SELECT
                elif key == '\n':  # Enter
                    current_buttons |= BUTTON_START

                await controller.send_buttons(current_buttons)

                # Reset buttons after sending (for single press)
                current_buttons = 0

            except KeyboardInterrupt:
                break

    finally:
        await controller.disconnect()

if __name__ == "__main__":
    asyncio.run(main())