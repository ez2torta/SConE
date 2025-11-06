#!/usr/bin/env python3
"""
Script de prueba para enviar comandos al SNES Controller Emulator (ESP32)

Este script envía comandos de prueba al ESP32 para simular diferentes
combinaciones de botones del SNES.

Uso:
    python test_snes_serial.py /dev/ttyUSB0

En Windows:
    python test_snes_serial.py COM3
"""

import serial
import struct
import time
import sys

# Definir bits de botones según el protocolo
BUTTON_B      = 0   # bit 0
BUTTON_Y      = 1   # bit 1
BUTTON_SELECT = 2   # bit 2
BUTTON_START  = 3   # bit 3
BUTTON_L      = 6   # bit 6
BUTTON_R      = 7   # bit 7
DPAD_UP       = 8   # bit 8
DPAD_DOWN     = 9   # bit 9
DPAD_LEFT     = 10  # bit 10
DPAD_RIGHT    = 11  # bit 11
BUTTON_A      = 12  # bit 12
BUTTON_X      = 2   # bit 2 (compartido con select en este mapeo)

def send_buttons(ser, button_bits):
    """
    Envía un comando de botones al ESP32
    
    Args:
        ser: Objeto serial
        button_bits: Lista de números de bit a activar (0-15)
    """
    buttons = 0
    for bit in button_bits:
        buttons |= (1 << bit)
    
    # Empaquetar como little-endian uint32
    data = struct.pack('<I', buttons)
    ser.write(data)
    
    # Mostrar qué se envió
    button_names = {
        0: 'B', 1: 'Y', 2: 'SELECT/X', 3: 'START',
        6: 'L', 7: 'R',
        8: 'UP', 9: 'DOWN', 10: 'LEFT', 11: 'RIGHT',
        12: 'A'
    }
    
    pressed = [button_names.get(bit, f'bit{bit}') for bit in button_bits]
    print(f"Enviado: 0x{buttons:08X} - Botones: {', '.join(pressed) if pressed else 'ninguno'}")

def test_sequence(port):
    """
    Ejecuta una secuencia de prueba de botones
    
    Args:
        port: Puerto serial (ej: /dev/ttyUSB0 o COM3)
    """
    print(f"Conectando a {port} a 115200 baudios...")
    
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)  # Esperar reset del ESP32
        
        # Leer y mostrar mensaje de inicio
        while ser.in_waiting:
            print(ser.readline().decode('utf-8', errors='ignore').strip())
        
        print("\n=== Iniciando secuencia de prueba ===\n")
        
        # Test 1: Sin botones presionados
        print("Test 1: Estado neutro")
        send_buttons(ser, [])
        time.sleep(1)
        
        # Test 2: Botones individuales
        print("\nTest 2: Botones de acción individuales")
        for button, name in [(BUTTON_A, 'A'), (BUTTON_B, 'B'), 
                              (BUTTON_X, 'X'), (BUTTON_Y, 'Y')]:
            print(f"  Presionando {name}...")
            send_buttons(ser, [button])
            time.sleep(0.5)
            send_buttons(ser, [])  # Soltar
            time.sleep(0.3)
        
        # Test 3: D-Pad
        print("\nTest 3: D-Pad (direccionales)")
        for direction, name in [(DPAD_UP, 'UP'), (DPAD_DOWN, 'DOWN'),
                                (DPAD_LEFT, 'LEFT'), (DPAD_RIGHT, 'RIGHT')]:
            print(f"  Presionando {name}...")
            send_buttons(ser, [direction])
            time.sleep(0.5)
            send_buttons(ser, [])  # Soltar
            time.sleep(0.3)
        
        # Test 4: Start y Select
        print("\nTest 4: Botones de sistema")
        print("  Presionando SELECT...")
        send_buttons(ser, [BUTTON_SELECT])
        time.sleep(0.5)
        send_buttons(ser, [])
        time.sleep(0.3)
        
        print("  Presionando START...")
        send_buttons(ser, [BUTTON_START])
        time.sleep(0.5)
        send_buttons(ser, [])
        time.sleep(0.3)
        
        # Test 5: Shoulder buttons
        print("\nTest 5: Botones L y R")
        print("  Presionando L...")
        send_buttons(ser, [BUTTON_L])
        time.sleep(0.5)
        send_buttons(ser, [])
        time.sleep(0.3)
        
        print("  Presionando R...")
        send_buttons(ser, [BUTTON_R])
        time.sleep(0.5)
        send_buttons(ser, [])
        time.sleep(0.3)
        
        # Test 6: Combinaciones
        print("\nTest 6: Combinaciones de botones")
        print("  A + B (combo clásico)...")
        send_buttons(ser, [BUTTON_A, BUTTON_B])
        time.sleep(0.5)
        send_buttons(ser, [])
        time.sleep(0.3)
        
        print("  UP + A (salto hacia arriba)...")
        send_buttons(ser, [DPAD_UP, BUTTON_A])
        time.sleep(0.5)
        send_buttons(ser, [])
        time.sleep(0.3)
        
        print("  L + R (combo de hombros)...")
        send_buttons(ser, [BUTTON_L, BUTTON_R])
        time.sleep(0.5)
        send_buttons(ser, [])
        time.sleep(0.3)
        
        # Test 7: Konami Code (solo para diversión)
        print("\nTest 7: Konami Code! ⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️🅱️🅰️")
        konami = [
            ([DPAD_UP], "⬆️  UP"),
            ([DPAD_UP], "⬆️  UP"),
            ([DPAD_DOWN], "⬇️  DOWN"),
            ([DPAD_DOWN], "⬇️  DOWN"),
            ([DPAD_LEFT], "⬅️  LEFT"),
            ([DPAD_RIGHT], "➡️  RIGHT"),
            ([DPAD_LEFT], "⬅️  LEFT"),
            ([DPAD_RIGHT], "➡️  RIGHT"),
            ([BUTTON_B], "🅱️  B"),
            ([BUTTON_A], "🅰️  A"),
        ]
        
        for buttons, name in konami:
            print(f"  {name}")
            send_buttons(ser, buttons)
            time.sleep(0.3)
            send_buttons(ser, [])
            time.sleep(0.2)
        
        # Finalizar
        print("\n=== Prueba completada ===")
        print("Estado final: todos los botones soltados")
        send_buttons(ser, [])
        
        ser.close()
        print(f"\nConexión cerrada con {port}")
        
    except serial.SerialException as e:
        print(f"Error: No se pudo conectar a {port}")
        print(f"Detalles: {e}")
        print("\nPuertos disponibles:")
        try:
            from serial.tools import list_ports
            ports = list_ports.comports()
            for port in ports:
                print(f"  - {port.device}: {port.description}")
        except:
            print("  (no se pudo listar puertos)")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario")
        send_buttons(ser, [])  # Liberar botones
        ser.close()
        sys.exit(0)

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_snes_serial.py <puerto>")
        print("\nEjemplos:")
        print("  Linux/Mac: python test_snes_serial.py /dev/ttyUSB0")
        print("  Windows:   python test_snes_serial.py COM3")
        print("\nPuertos disponibles:")
        try:
            from serial.tools import list_ports
            ports = list_ports.comports()
            for port in ports:
                print(f"  - {port.device}: {port.description}")
        except:
            print("  (instala pyserial: pip install pyserial)")
        sys.exit(1)
    
    port = sys.argv[1]
    test_sequence(port)

if __name__ == "__main__":
    main()
