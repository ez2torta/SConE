#!/usr/bin/env python3
"""
Script de diagnóstico para escanear dispositivos BLE disponibles

Útil para verificar si el ESP32 está anunciando correctamente
y qué nombre/dirección tiene.
"""

import asyncio
import sys

try:
    from bleak import BleakScanner
    BLE_AVAILABLE = True
except ImportError:
    print("❌ bleak no instalado. Instala con: pip install bleak")
    sys.exit(1)

# UUIDs que estamos buscando
TARGET_SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
TARGET_DEVICE_NAME = "SNES Controller"  # Sin guión - así lo anuncia el ESP32


async def scan_devices(duration: int = 15):
    """Escanea dispositivos BLE por un tiempo determinado"""
    print("=" * 70)
    print("🔍 ESCANEANDO DISPOSITIVOS BLUETOOTH BLE")
    print("=" * 70)
    print(f"\n⏱️  Escaneando durante {duration} segundos...")
    print(f"🎯 Buscando: '{TARGET_DEVICE_NAME}'\n")
    
    # Escanear dispositivos
    devices = await BleakScanner.discover(timeout=duration, return_adv=True)
    
    if not devices:
        print("❌ No se encontraron dispositivos BLE")
        print("\n💡 Posibles causas:")
        print("   1. El ESP32 no está encendido")
        print("   2. El ESP32 no ha iniciado el servicio BLE")
        print("   3. Bluetooth deshabilitado en este dispositivo")
        print("   4. El ESP32 está fuera de rango (~10m)")
        return
    
    print(f"✅ Encontrados {len(devices)} dispositivos BLE:\n")
    
    found_target = False
    
    # Mostrar todos los dispositivos
    for address, (device, adv_data) in devices.items():
        name = device.name or "(sin nombre)"
        rssi = adv_data.rssi
        
        # Verificar si es nuestro dispositivo objetivo
        is_target = False
        if device.name:
            # Comparación case-insensitive y parcial
            if TARGET_DEVICE_NAME.lower() in device.name.lower():
                is_target = True
                found_target = True
        
        # Marcar dispositivo objetivo con emoji
        marker = "🎯" if is_target else "  "
        
        print(f"{marker} Dispositivo: {name}")
        print(f"   Dirección:  {address}")
        print(f"   RSSI:       {rssi} dBm")
        
        # Mostrar UUIDs de servicios si están disponibles
        if adv_data.service_uuids:
            print(f"   Servicios:  {len(adv_data.service_uuids)} UUID(s)")
            for uuid in adv_data.service_uuids:
                uuid_str = str(uuid).lower()
                is_target_service = uuid_str == TARGET_SERVICE_UUID.lower()
                service_marker = "   ✓" if is_target_service else "    "
                print(f"{service_marker} {uuid}")
                if is_target_service:
                    is_target = True
                    found_target = True
        
        # Mostrar datos adicionales del anuncio
        if adv_data.manufacturer_data:
            print(f"   Fabricante: {list(adv_data.manufacturer_data.keys())}")
        
        print()
    
    # Resumen
    print("=" * 70)
    if found_target:
        print("✅ ¡DISPOSITIVO OBJETIVO ENCONTRADO!")
        print(f"\nPuedes conectarte usando:")
        print(f"  python test_ble_input.py ble")
    else:
        print("⚠️  DISPOSITIVO OBJETIVO NO ENCONTRADO")
        print(f"\n🔍 Buscábamos: '{TARGET_DEVICE_NAME}'")
        print(f"🔍 UUID servicio: {TARGET_SERVICE_UUID}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que el ESP32 muestre 'BLE: Servicio iniciado' en Serial Monitor")
        print("   2. Reinicia el ESP32 (botón RESET)")
        print("   3. Vuelve a cargar el firmware")
        print("   4. Verifica que el nombre en el código ESP32 sea exactamente 'SNES-Controller'")
        print("   5. Acerca más el ESP32 a este dispositivo")
    print("=" * 70)


async def continuous_scan():
    """Modo de escaneo continuo"""
    print("🔄 MODO ESCANEO CONTINUO")
    print("Presiona Ctrl+C para detener\n")
    
    try:
        scan_count = 1
        while True:
            print(f"\n{'='*70}")
            print(f"Escaneo #{scan_count}")
            print(f"{'='*70}\n")
            
            devices = await BleakScanner.discover(timeout=5.0)
            
            for device in devices:
                name = device.name or "(sin nombre)"
                if TARGET_DEVICE_NAME.lower() in name.lower():
                    print(f"🎯 ENCONTRADO: {name} ({device.address})")
            
            scan_count += 1
            await asyncio.sleep(1)  # Pausa entre escaneos
    
    except KeyboardInterrupt:
        print("\n\n✋ Escaneo detenido por el usuario")


def main():
    """Punto de entrada principal"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print("Uso: python scan_ble_devices.py [modo]")
            print("\nModos:")
            print("  (ninguno)    - Escaneo único de 15 segundos (default)")
            print("  continuous   - Escaneo continuo hasta Ctrl+C")
            print("  quick        - Escaneo rápido de 5 segundos")
            print("\nEjemplos:")
            print("  python scan_ble_devices.py")
            print("  python scan_ble_devices.py continuous")
            print("  python scan_ble_devices.py quick")
            return
        
        elif sys.argv[1] == 'continuous':
            asyncio.run(continuous_scan())
            return
        
        elif sys.argv[1] == 'quick':
            asyncio.run(scan_devices(duration=5))
            return
    
    # Modo default: escaneo único
    asyncio.run(scan_devices(duration=15))


if __name__ == "__main__":
    main()
