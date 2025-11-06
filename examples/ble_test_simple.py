#!/usr/bin/env python3
"""
Script de prueba simple para BLE SNES Controller

Envía valores específicos para probar el mapeo de botones.
"""

import asyncio
import struct
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

async def test_buttons():
    print("Buscando dispositivo SNES Controller...")

    devices = await BleakScanner.discover()
    snes_device = None

    for device in devices:
        if device.name and "SNES Controller" in device.name:
            snes_device = device
            break

    if not snes_device:
        print("❌ No se encontró el dispositivo SNES Controller")
        return

    print(f"✅ Conectando a {snes_device.name} ({snes_device.address})...")

    async with BleakClient(snes_device) as client:
        print("✅ Conectado!")

        # Test cases: (description, button_mask)
        tests = [
            ("Sin botones", 0),
            ("Botón A (bit 12)", 1 << 12),
            ("Botón B (bit 0)", 1 << 0),
            ("Arriba (bit 8)", 1 << 8),
            ("Abajo (bit 9)", 1 << 9),
            ("Izquierda (bit 10)", 1 << 10),
            ("Derecha (bit 11)", 1 << 11),
            ("Start (bit 3)", 1 << 3),
            ("Select (bit 2)", 1 << 2),
            ("A + B", (1 << 12) | (1 << 0)),
            ("Arriba + A", (1 << 8) | (1 << 12)),
        ]

        for description, button_mask in tests:
            print(f"\n🧪 Probando: {description}")
            print(f"   Enviando: 0x{button_mask:08X}")

            # Mostrar bytes
            data = struct.pack('<I', button_mask)
            byte0, byte1, byte2, byte3 = data
            print(f"   Bytes: {byte0:02X} {byte1:02X} {byte2:02X} {byte3:02X}")

            await client.write_gatt_char(CHARACTERISTIC_UUID, data)
            await asyncio.sleep(2)  # Esperar para ver el output del Arduino

        print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    asyncio.run(test_buttons())