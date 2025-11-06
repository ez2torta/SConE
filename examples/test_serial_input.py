#!/usr/bin/env python3
"""
Script de prueba para SNES Controller Emulator (ESP32)

Este script envía comandos de botones al ESP32 vía USB Serial
que luego los transmite al SNES. Útil para testing y debugging.

Protocolo: uint32_t (4 bytes, little-endian)
Baudrate: 115200
"""

import serial
import struct
import time
import sys

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

def send_buttons(ser, button_mask):
    """
    Envía un mask de botones al ESP32/SNES
    
    Args:
        ser: Objeto serial
        button_mask: uint32_t con los bits de botones activos
    """
    data = struct.pack('<I', button_mask)
    ser.write(data)
    ser.flush()

def test_sequence(ser):
    """Ejecuta una secuencia de prueba para botones SNES"""
    print("=== Iniciando secuencia de prueba SNES ===\n")
    
    # Test 1: Botones de acción
    print("Test 1: Botones de acción")
    action_buttons = ['B', 'Y', 'A', 'X']
    for name in action_buttons:
        print(f"  Presionando {name}...")
        send_buttons(ser, BUTTONS[name])
        time.sleep(0.4)
        send_buttons(ser, 0)  # Soltar
        time.sleep(0.2)
    
    # Test 2: D-Pad
    print("\nTest 2: D-Pad (direccionales)")
    dpad_sequence = ['UP', 'RIGHT', 'DOWN', 'LEFT']
    for direction in dpad_sequence:
        print(f"  D-Pad {direction}")
        send_buttons(ser, BUTTONS[direction])
        time.sleep(0.4)
        send_buttons(ser, 0)
        time.sleep(0.2)
    
    # Test 3: Botones de hombro
    print("\nTest 3: Botones de hombro")
    for name in ['L', 'R']:
        print(f"  Presionando {name}...")
        send_buttons(ser, BUTTONS[name])
        time.sleep(0.4)
        send_buttons(ser, 0)
        time.sleep(0.2)
    
    # Test 4: Botones de sistema
    print("\nTest 4: Botones de sistema")
    for name in ['SELECT', 'START']:
        print(f"  Presionando {name}...")
        send_buttons(ser, BUTTONS[name])
        time.sleep(0.4)
        send_buttons(ser, 0)
        time.sleep(0.2)
    
    # Test 5: Combos comunes
    print("\nTest 5: Combinaciones comunes")
    
    print("  A + B (combo clásico)")
    combo = BUTTONS['A'] | BUTTONS['B']
    send_buttons(ser, combo)
    time.sleep(0.5)
    send_buttons(ser, 0)
    time.sleep(0.3)
    
    print("  UP + A (salto hacia arriba)")
    combo = BUTTONS['UP'] | BUTTONS['A']
    send_buttons(ser, combo)
    time.sleep(0.5)
    send_buttons(ser, 0)
    time.sleep(0.3)
    
    print("  L + R (combo de hombros)")
    combo = BUTTONS['L'] | BUTTONS['R']
    send_buttons(ser, combo)
    time.sleep(0.5)
    send_buttons(ser, 0)
    time.sleep(0.3)
    
    print("  START + SELECT (pausa/reset)")
    combo = BUTTONS['START'] | BUTTONS['SELECT']
    send_buttons(ser, combo)
    time.sleep(0.5)
    send_buttons(ser, 0)
    
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
        send_buttons(ser, BUTTONS[button])
        time.sleep(0.3)
        send_buttons(ser, 0)
        time.sleep(0.2)
    
    print("\n=== Test completado! ===")

def interactive_mode(ser):
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
                send_buttons(ser, 0)
                continue
            
            button_names = user_input.split()
            mask = 0
            
            for name in button_names:
                if name in BUTTONS:
                    mask |= BUTTONS[name]
                else:
                    print(f"Botón desconocido: {name}")
            
            send_buttons(ser, mask)
            print(f"Enviado: 0x{mask:04X}")
            
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    finally:
        # Soltar todos los botones al salir
        send_buttons(ser, 0)

def continuous_spam(ser, rate_hz=60):
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
            send_buttons(ser, BUTTONS['A'])
            time.sleep(delay / 2)
            send_buttons(ser, 0)
            time.sleep(delay / 2)
            count += 1
            
            if count % rate_hz == 0:  # Cada segundo
                elapsed = time.time() - start_time
                actual_rate = count / elapsed
                print(f"Enviados: {count} ciclos, Rate actual: {actual_rate:.1f} Hz")
    
    except KeyboardInterrupt:
        print("\nDetenido")
    finally:
        send_buttons(ser, 0)

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
    mode = sys.argv[2] if len(sys.argv) > 2 else 'test'
    
    try:
        print(f"SNES Controller Emulator - Conectando a {port}...")
        ser = serial.Serial(port, 115200, timeout=1)
        print("✅ Conectado!\n")
        
        # Dar tiempo al ESP32 para inicializar
        time.sleep(2)
        
        # Leer mensajes de inicio del ESP32
        while ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"ESP32: {line}")
        
        print()  # Línea en blanco
        
        if mode == 'test':
            test_sequence(ser)
        elif mode == 'interactive':
            interactive_mode(ser)
        elif mode in ['turbo', 'spam']:
            continuous_spam(ser)
        else:
            print(f"❌ Modo desconocido: {mode}")
            print("Modos disponibles: test, interactive, turbo")
            ser.close()
            sys.exit(1)
        
        ser.close()
        print("\n✅ Conexión cerrada")
        
    except serial.SerialException as e:
        print(f"❌ Error al abrir puerto serial: {e}")
        print("\nVerifica que:")
        print("  - El ESP32 está conectado")
        print("  - El puerto es correcto")
        print("  - Tienes permisos (Linux: sudo usermod -a -G dialout $USER)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()