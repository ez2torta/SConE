#!/usr/bin/env python3
"""
Xbox 360 -> Serial Bridge

- Captura inputs desde un control Xbox 360 (USB) usando pygame
- Expone una API HTTP local para enviar inputs independientes
- Envía el bitmask de botones al ESP32/Arduino vía Serial (115200)

Requisitos:
  pip install pygame pyserial aiohttp

Uso:
  python x360_to_serial_bridge.py --port /dev/tty.usbserial-XXXX --http 8080

API HTTP:
  POST /send-buttons     {"buttons": 12345}
  POST /send-keys        {"keys": ["RIGHT","A"], "holdMs": 150}
  POST /sequence         {"sequence": [["RIGHT"], ["A"]], "frameMs": 16}
  GET  /status           -> estado del bridge

Notas:
- En macOS puede ser necesario permitir el control del teclado/joystick en Privacidad
- Asegúrate de tener el driver del mando Xbox 360 instalado si es necesario
"""

import asyncio
import argparse
import sys
import os
from typing import List, Optional

import serial
from serial import Serial

from test_ble_input import BUTTONS

try:
    import pygame
    from pygame.locals import (
        JOYAXISMOTION,
        JOYBUTTONDOWN,
        JOYBUTTONUP,
    )
except ImportError:
    pygame = None

try:
    from aiohttp import web
except ImportError:
    web = None

# Añadir examples al path para importar utilidades existentes
sys.path.insert(0, os.path.dirname(__file__))


X360_ANALOG_DEADZONE = 0.3  # umbral para sticks
POLL_INTERVAL = 0.01        # segundos


class SerialSender:
    def __init__(self, port: str, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.serial: Optional[Serial] = None
        self.last_sent: int = 0
        self.connected = False

    def connect(self):
        self.serial = serial.Serial(self.port, self.baud, timeout=0)
        self.connected = True
        print(f"✅ Conectado a Serial: {self.port} @ {self.baud}")

    def send(self, buttons: int):
        if not self.serial:
            return
        # Evitar spam si no cambia el estado
        if buttons == self.last_sent:
            return
        # Enviar como 4 bytes little-endian
        payload = buttons.to_bytes(4, byteorder='little')
        self.serial.write(payload)
        self.last_sent = buttons

    def close(self):
        if self.serial:
            self.serial.close()
            self.connected = False


class X360Mapper:
    """Mapea eventos de Xbox 360 a bitmask SNES"""

    def __init__(self):
        # Estado actual de botones/direcciones SNES
        self.state = 0

    def set_flag(self, flag: int, enabled: bool):
        if enabled:
            self.state |= flag
        else:
            self.state &= ~flag

    def handle_axis(self, axis: int, value: float):
        # Ejes típicos Xbox 360:
        # 0: LX (-1 izquierda, +1 derecha)
        # 1: LY (-1 arriba, +1 abajo)
        # 2: RX
        # 3: RY
        # 4: LT (0 a 1)
        # 5: RT (0 a 1)
        if axis == 0:  # LX
            # derecha
            self.set_flag(BUTTONS['RIGHT'], value > X360_ANALOG_DEADZONE)
            # izquierda
            self.set_flag(BUTTONS['LEFT'], value < -X360_ANALOG_DEADZONE)
        elif axis == 1:  # LY (nota: arriba es negativo)
            self.set_flag(BUTTONS['UP'], value < -X360_ANALOG_DEADZONE)
            self.set_flag(BUTTONS['DOWN'], value > X360_ANALOG_DEADZONE)
        # ignoramos otros ejes por ahora

    def handle_button(self, button: int, pressed: bool):
        # Mapeo común de botones Xbox 360:
        # A=0, B=1, X=2, Y=3, LB=4, RB=5,
        # BACK=6, START=7, GUIDE=8, LSTICK=9, RSTICK=10
        if button == 0:  # A
            self.set_flag(BUTTONS['A'], pressed)
        elif button == 1:  # B
            self.set_flag(BUTTONS['B'], pressed)
        elif button == 2:  # X -> mapear a C
            # mapear X a botón C si corresponde en tu firmware
            self.set_flag(BUTTONS['X'], pressed)
        elif button == 3:  # Y -> mapear a D
            self.set_flag(BUTTONS['Y'], pressed)
        elif button == 4:  # LB -> L
            self.set_flag(BUTTONS['L'], pressed)
        elif button == 5:  # RB -> R
            self.set_flag(BUTTONS['R'], pressed)
        elif button == 6:  # BACK -> SELECT
            self.set_flag(BUTTONS['SELECT'], pressed)
        elif button == 7:  # START
            self.set_flag(BUTTONS['START'], pressed)
        # Sticks click, GUIDE ignorados

    def get_state(self) -> int:
        return self.state

    def set_keys(self, keys: List[str]):
        # Construir bitmask desde lista de nombres
        value = 0
        for k in keys:
            v = BUTTONS.get(k.upper())
            if v:
                value |= v
        self.state = value
        return value


class BridgeApp:
    def __init__(self, serial_port: str, http_port: Optional[int] = None):
        self.serial_sender = SerialSender(serial_port)
        self.http_port = http_port
        self.mapper = X360Mapper()
        self.running = True
        self.joystick_ready = False

    async def start(self):
        # Conectar serial
        self.serial_sender.connect()
        
        # Iniciar pygame joystick
        if pygame:
            pygame.init()
            pygame.joystick.init()
            if pygame.joystick.get_count() == 0:
                print("⚠️  No se detectó control Xbox 360 conectado")
            else:
                js = pygame.joystick.Joystick(0)
                js.init()
                self.joystick_ready = True
                name = js.get_name()
                axes = js.get_numaxes()
                buttons = js.get_numbuttons()
                print(
                    f"✅ Joystick listo: {name} "
                    f"({axes} ejes, {buttons} botones)"
                )
        else:
            print("⚠️  pygame no disponible. Instala con: pip install pygame")
        
        # Crear tareas
        tasks = []
        tasks.append(asyncio.create_task(self.joystick_loop()))
        if self.http_port and web:
            tasks.append(asyncio.create_task(self.http_server()))
            print(f"✅ HTTP listo en http://127.0.0.1:{self.http_port}")
        elif self.http_port and not web:
            print("⚠️  aiohttp no disponible. Instala: pip install aiohttp")
        
        # Esperar tareas
        await asyncio.gather(*tasks)

    async def joystick_loop(self):
        """Captura eventos del joystick y los envía por serial"""
        while self.running:
            if self.joystick_ready:
                for event in pygame.event.get():
                    if event.type == JOYAXISMOTION:
                        self.mapper.handle_axis(event.axis, event.value)
                    elif event.type == JOYBUTTONDOWN:
                        self.mapper.handle_button(event.button, True)
                    elif event.type == JOYBUTTONUP:
                        self.mapper.handle_button(event.button, False)
                
                # Enviar estado actual
                self.serial_sender.send(self.mapper.get_state())
            
            await asyncio.sleep(POLL_INTERVAL)

    async def http_server(self):
        """Servidor HTTP para mandar inputs independientes"""
        app = web.Application()
        
        async def status(_request):
            return web.json_response({
                "serial": {
                    "port": self.serial_sender.port,
                    "baud": self.serial_sender.baud,
                    "connected": self.serial_sender.connected
                },
                "joystick": {
                    "enabled": self.joystick_ready
                },
                "state": self.mapper.get_state()
            })
        
        async def send_buttons(request):
            data = await request.json()
            buttons = int(data.get('buttons', 0))
            hold_ms = int(data.get('holdMs', 0))
            
            self.serial_sender.send(buttons)
            if hold_ms > 0:
                await asyncio.sleep(hold_ms / 1000.0)
                self.serial_sender.send(0)
            return web.json_response({"ok": True})
        
        async def send_keys(request):
            data = await request.json()
            keys = data.get('keys', [])
            hold_ms = int(data.get('holdMs', 0))
            val = self.mapper.set_keys(keys)
            self.serial_sender.send(val)
            if hold_ms > 0:
                await asyncio.sleep(hold_ms / 1000.0)
                self.serial_sender.send(0)
            return web.json_response({"ok": True, "value": val})
        
        async def send_sequence(request):
            data = await request.json()
            # 'sequence' es lista de pasos; cada paso es lista de keys
            sequence = data.get('sequence', [])
            frame_ms = float(data.get('frameMs', 16.67))
            
            for step in sequence:
                keys = step if isinstance(step, list) else [step]
                val = self.mapper.set_keys(keys)
                self.serial_sender.send(val)
                await asyncio.sleep(frame_ms / 1000.0)
            # soltar
            self.serial_sender.send(0)
            return web.json_response({"ok": True})
        
        app.add_routes([
            web.get('/status', status),
            web.post('/send-buttons', send_buttons),
            web.post('/send-keys', send_keys),
            web.post('/sequence', send_sequence),
        ])
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', self.http_port)
        await site.start()
        
        # Mantener vivo
        while self.running:
            await asyncio.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Xbox 360 -> Serial bridge")
    parser.add_argument(
        '--port', required=True,
        help='Puerto serial (ej: /dev/tty.usbserial-XXXX)'
    )
    parser.add_argument('--baud', type=int, default=115200, help='Baudios')
    parser.add_argument(
        '--http', type=int, default=None,
        help='Puerto HTTP para API (opcional)'
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    app = BridgeApp(serial_port=args.port, http_port=args.http)
    try:
        await app.start()
    except KeyboardInterrupt:
        print("\n⚠️  Bridge detenido por usuario")
    finally:
        app.serial_sender.close()


if __name__ == '__main__':
    print("\n💡 Dependencias: pip install pygame pyserial aiohttp")
    print("💡 Usa --http 8080 para habilitar la API HTTP de control paralelo")
    asyncio.run(main())
