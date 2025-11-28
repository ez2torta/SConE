#!/usr/bin/env python3
"""
Xbox 360 Sequence Recorder (Serial Output)

Objetivo: Basado en `test_serial_input.py` para salida por Serial, pero
la entrada proviene de un control de Xbox 360. Permite:
- Grabar secuencias (bitmask por frame @ ~60 FPS)
- Guardar/abrir secuencias en JSON
- Reproducir secuencias por Serial al ESP32/Arduino

Dependencias:
  pip install pygame pyserial

Uso rápido:
    python x360_sequence_recorder.py \
        --port /dev/tty.usbserial-XXXX \
        --record seq.json
    python x360_sequence_recorder.py \
        --port /dev/tty.usbserial-XXXX \
        --play seq.json
    # Debug y reproducción invertida (P2)
    python x360_sequence_recorder.py \
        --port /dev/tty.usbserial-XXXX \
        --record seq.json --debug
    python x360_sequence_recorder.py \
        --port /dev/tty.usbserial-XXXX \
        --play seq.json --invert-x
"""

import json
import time
import argparse
import os
import sys
from pathlib import Path
from typing import List

# Añadir examples al path para importar utilidades existentes
sys.path.insert(0, os.path.dirname(__file__))
from test_ble_input import SNESControllerSerial, BUTTONS

try:
    import pygame
    # no usamos constantes de eventos, hacemos polling por frame
except ImportError:
    pygame = None

FRAME_RATE = 60.0
FRAME_DURATION = 1.0 / FRAME_RATE
DEFAULT_DEADZONE = 0.3


class X360Mapper:
    def __init__(
        self,
        deadzone: float = DEFAULT_DEADZONE,
        mapping: dict | None = None,
    ):
        self.state = 0
        self.deadzone = deadzone
        self.mapping = mapping or {}

    def set_flag(self, flag: int, enabled: bool):
        if enabled:
            self.state |= flag
        else:
            self.state &= ~flag

    def handle_axis(self, axis: int, value: float):
        # 0: LX, 1: LY (negativo es arriba)
        if axis == 0:
            self.set_flag(BUTTONS['RIGHT'], value > self.deadzone)
            self.set_flag(BUTTONS['LEFT'], value < -self.deadzone)
        elif axis == 1:
            self.set_flag(BUTTONS['UP'], value < -self.deadzone)
            self.set_flag(BUTTONS['DOWN'], value > self.deadzone)

    def handle_button(self, button: int, pressed: bool):
        # If a custom mapping exists, use it; else default xbox360 indices
        m = self.mapping.get('buttons', {})
        
        def idx(name: str):
            return m.get(name, None)

        def set_by(name: str, default_idx: int):
            target = idx(name)
            if target is None:
                target = default_idx
            if button == target:
                self.set_flag(BUTTONS[name], pressed)
        set_by('A', 0)
        set_by('B', 1)
        set_by('X', 2)
        set_by('Y', 3)
        set_by('L', 4)
        set_by('R', 5)
        set_by('SELECT', 6)
        set_by('START', 7)

    def get_state(self) -> int:
        return self.state


def record_sequence(
    port: str,
    outfile: Path,
    debug: bool = False,
    raw_debug: bool = False,
    deadzone: float = DEFAULT_DEADZONE,
    release_each_frame: bool = False,
):
    if not pygame:
        print("❌ pygame no disponible. Instala con: pip install pygame")
        return 2

    # Inicializar pygame; evita que linters marquen miembro faltante
    if hasattr(pygame, 'init'):
        pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("❌ No se detectó un control Xbox 360 conectado por USB")
        return 2

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"✅ Joystick: {js.get_name()} listo")
    axes = js.get_numaxes()
    buttons = js.get_numbuttons()
    hats = js.get_numhats()
    print(f"   Axes: {axes}, Buttons: {buttons}, Hats: {hats}")

    # Load optional mapping file passed via env var or defaults
    mapping_path = os.environ.get('X360_MAPPING')
    mapping = {}
    if mapping_path and Path(mapping_path).exists():
        try:
            mapping_text = Path(mapping_path).read_text(encoding='utf-8')
            mapping = json.loads(mapping_text)
            print(f"🔧 Usando mapeo de {mapping_path}")
        except (OSError, json.JSONDecodeError) as e:
            print(f"⚠️ No se pudo leer mapeo {mapping_path}: {e}")

    # Validación de mapeo: detectar índices duplicados y advertir
    def validate_mapping(map_obj: dict):
        warnings = []
        # Botones duplicados
        btns = map_obj.get('buttons', {})
        inv_btn = {}
        for name, idx in btns.items():
            inv_btn.setdefault(idx, []).append(name)
        for idx, names in inv_btn.items():
            if len(names) > 1:
                msg = (
                    f"Botón índice {idx} asignado a múltiples: "
                    f"{', '.join(names)}"
                )
                warnings.append(msg)
        # Ejes inconsistentes: LEFT/RIGHT o UP/DOWN con distintos ejes
        axes = map_obj.get('axes', {})
        lr_axis = [axes.get('LEFT'), axes.get('RIGHT')]
        ud_axis = [axes.get('UP'), axes.get('DOWN')]
        if None not in lr_axis and lr_axis[0] != lr_axis[1]:
            warnings.append(
                "LEFT y RIGHT usan ejes distintos; se espera el mismo eje"
            )
        if None not in ud_axis and ud_axis[0] != ud_axis[1]:
            warnings.append(
                "UP y DOWN usan ejes distintos; se espera el mismo eje"
            )
        # Hats: si se usa hat, idealmente un único índice
        hats = map_obj.get('hats', {})
        hat_indices = list({v for v in hats.values()})
        if len(hat_indices) > 1:
            warnings.append(
                "HAT directions usan múltiples índices; se sugiere uno"
            )
        if warnings:
            print("⚠️ Advertencias de mapeo:")
            for w in warnings:
                print(f"   - {w}")
        return warnings

    if mapping:
        validate_mapping(mapping)
    mapper = X360Mapper(deadzone=deadzone, mapping=mapping)
    controller = SNESControllerSerial(port)

    print("\n🎬 Grabación iniciada. Controles:")
    print("  Mantener START+SELECT ~0.5s para finalizar y guardar")
    print("  Mantén ~60 FPS (se muestrea cada 16.7ms)")

    frames: List[int] = []
    running = True
    start_time = time.time()

    stop_held_since: float = 0.0
    try:
        while running:
            loop_start = time.time()

            # Actualiza el estado interno de pygame para lecturas de joystick
            # Necesario en macOS para que get_axis/get_button reflejen cambios.
            pygame.event.pump()

            # POLLING: leer estado completo cada frame (más estable)
            # Reset direcciones
            mapper.set_flag(BUTTONS['LEFT'], False)
            mapper.set_flag(BUTTONS['RIGHT'], False)
            mapper.set_flag(BUTTONS['UP'], False)
            mapper.set_flag(BUTTONS['DOWN'], False)

            # Axes via mapping (prefer calibrated indices)
            axes_map = mapper.mapping.get('axes', {})
            used_axes = False
            
            def read_axis(idx: int) -> float:
                if 0 <= idx < js.get_numaxes():
                    return js.get_axis(idx)
                return 0.0
            if axes_map:
                # LEFT/RIGHT may share same axis; similarly UP/DOWN
                if 'LEFT' in axes_map or 'RIGHT' in axes_map:
                    ax = axes_map.get('LEFT', axes_map.get('RIGHT', 0))
                    v = read_axis(ax)
                    mapper.set_flag(BUTTONS['LEFT'], v < -mapper.deadzone)
                    mapper.set_flag(BUTTONS['RIGHT'], v > mapper.deadzone)
                    used_axes = True
                if 'UP' in axes_map or 'DOWN' in axes_map:
                    ay = axes_map.get('UP', axes_map.get('DOWN', 1))
                    v = read_axis(ay)
                    mapper.set_flag(BUTTONS['UP'], v < -mapper.deadzone)
                    mapper.set_flag(BUTTONS['DOWN'], v > mapper.deadzone)
                    used_axes = True
            else:
                # Fallback to LX=0, LY=1 if available
                if js.get_numaxes() >= 2:
                    lx = js.get_axis(0)
                    ly = js.get_axis(1)
                    mapper.handle_axis(0, lx)
                    mapper.handle_axis(1, ly)
                    used_axes = True

            # Hat (POV) via mapping (overrides axes if present changes)
            hats_map = mapper.mapping.get('hats', {})
            
            def read_hat(idx: int):
                if 0 <= idx < js.get_numhats():
                    return js.get_hat(idx)
                return (0, 0)
            if hats_map:
                # If hat indices provided, read and apply
                # Use the same hat index for all directions if only one present
                idx_hat = None
                for k in ('LEFT', 'RIGHT', 'UP', 'DOWN'):
                    if k in hats_map:
                        idx_hat = hats_map[k]
                        break
                if idx_hat is not None:
                    hx, hy = read_hat(idx_hat)
                    if hx < 0:
                        mapper.set_flag(BUTTONS['LEFT'], True)
                    elif hx > 0:
                        mapper.set_flag(BUTTONS['RIGHT'], True)
                    if hy > 0:
                        mapper.set_flag(BUTTONS['UP'], True)
                    elif hy < 0:
                        mapper.set_flag(BUTTONS['DOWN'], True)
            else:
                if js.get_numhats() > 0 and not used_axes:
                    hat_x, hat_y = js.get_hat(0)
                    if hat_x < 0:
                        mapper.set_flag(BUTTONS['LEFT'], True)
                    elif hat_x > 0:
                        mapper.set_flag(BUTTONS['RIGHT'], True)
                    if hat_y > 0:
                        mapper.set_flag(BUTTONS['UP'], True)
                    elif hat_y < 0:
                        mapper.set_flag(BUTTONS['DOWN'], True)

            # Buttons
            for b in range(js.get_numbuttons()):
                mapper.handle_button(b, js.get_button(b) == 1)

            # condición de salida: START + BACK
            # pygame no da combinación directa, usamos estado actual
            # si ambos bits están activos salimos
            state = mapper.get_state()
            if raw_debug:
                axes_vals = [js.get_axis(i) for i in range(js.get_numaxes())]
                btn_vals = [
                    js.get_button(i) for i in range(js.get_numbuttons())
                ]
                hat_vals = [js.get_hat(i) for i in range(js.get_numhats())]
                fmt_axes = ["%.2f" % a for a in axes_vals]
                sys.stdout.write(
                    f"\rAX:{fmt_axes} BTN:{btn_vals} HAT:{hat_vals}"
                )
                sys.stdout.flush()
            if debug:
                lr = ('L' if (state & BUTTONS['LEFT']) else '-') + (
                    'R' if (state & BUTTONS['RIGHT']) else '-'
                )
                ud = ('U' if (state & BUTTONS['UP']) else '-') + (
                    'D' if (state & BUTTONS['DOWN']) else '-'
                )
                abxy = ''.join([
                    'A' if (state & BUTTONS['A']) else '-',
                    'B' if (state & BUTTONS['B']) else '-',
                    'X' if (state & BUTTONS['X']) else '-',
                    'Y' if (state & BUTTONS['Y']) else '-',
                ])
                lr_btn = ''.join([
                    'L' if (state & BUTTONS['L']) else '-',
                    'R' if (state & BUTTONS['R']) else '-',
                ])
                if not raw_debug:
                    sys.stdout.write(
                        f"\r[LR:{lr} UD:{ud}] [ABXY:{abxy}] [LRbtn:{lr_btn}] "
                    )
                    sys.stdout.flush()
            frames.append(state)

            # enviar al serial - bitmask por frame (como test_serial_input)
            controller.send_buttons(state)
            if release_each_frame:
                controller.send_buttons(0)

            # START + SELECT sostenido por 0.5s para terminar
            if (state & BUTTONS['START']) and (state & BUTTONS['SELECT']):
                if stop_held_since == 0.0:
                    stop_held_since = time.time()
                elif time.time() - stop_held_since >= 0.5:
                    print("\n⏹️  Stop por START+SELECT (0.5s)")
                    running = False
            else:
                stop_held_since = 0.0

            # esperar al siguiente frame
            elapsed = time.time() - loop_start
            delay = max(0.0, FRAME_DURATION - elapsed)
            time.sleep(delay)
    finally:
        controller.close()
        pygame.joystick.quit()

    duration = time.time() - start_time
    data = {
        "fps": FRAME_RATE,
        "frames": frames,
        "duration_sec": round(duration, 3),
        "count": len(frames),
    }
    outfile.write_text(json.dumps(data, indent=2))
    print(
        f"\n💾 Secuencia guardada en {outfile} "
        f"({len(frames)} frames, {duration:.2f}s)"
    )
    return 0


def play_sequence(
    port: str,
    infile: Path,
    invert_x: bool = False,
    release_each_frame: bool = False,
):
    if not infile.exists():
        print(f"❌ No existe el archivo: {infile}")
        return 2
    data = json.loads(infile.read_text())
    frames: List[int] = data.get("frames", [])
    fps = float(data.get("fps", FRAME_RATE))
    frame_dt = 1.0 / fps

    controller = SNESControllerSerial(port)
    print(f"▶️  Reproduciendo {len(frames)} frames a {fps} FPS")
    if invert_x:
        print("🔁 Invertir eje X: LEFT/RIGHT intercambiados (modo P2)")

    try:
        for buttons in frames:
            b = int(buttons)
            if invert_x:
                left = bool(b & BUTTONS['LEFT'])
                right = bool(b & BUTTONS['RIGHT'])
                b &= ~BUTTONS['LEFT']
                b &= ~BUTTONS['RIGHT']
                if left:
                    b |= BUTTONS['RIGHT']
                if right:
                    b |= BUTTONS['LEFT']
            controller.send_buttons(b)
            if release_each_frame:
                controller.send_buttons(0)
            time.sleep(frame_dt)
    finally:
        controller.send_buttons(0)
        controller.close()
    print("✅ Reproducción completa")
    return 0


def calibrate_mapping(outfile: Path):
    if not pygame:
        print("❌ pygame no disponible. Instala con: pip install pygame")
        return 2
    if hasattr(pygame, 'init'):
        pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("❌ No se detectó un control Xbox 360 conectado por USB")
        return 2
    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"✅ Joystick: {js.get_name()} listo")
    print("\nCalibración interactiva: Presiona cuando se te indique.")
    mapping = {"axes": {}, "buttons": {}, "hats": {}}

    def wait_for_change(prompt: str):
        print(prompt)
        base_axes = [js.get_axis(i) for i in range(js.get_numaxes())]
        base_btns = [js.get_button(i) for i in range(js.get_numbuttons())]
        base_hats = [js.get_hat(i) for i in range(js.get_numhats())]
        detected = None
        stable_since = 0.0
        while True:
            pygame.event.pump()
            time.sleep(0.01)
            kind = None
            idx = -1
            val = None
            # Check axes (large movement from baseline)
            for i in range(js.get_numaxes()):
                v = js.get_axis(i)
                if abs(v - base_axes[i]) > 0.5:
                    kind, idx, val = 'axis', i, v
                    break
            # Check buttons (pressed vs baseline)
            if kind is None:
                for i in range(js.get_numbuttons()):
                    v = js.get_button(i)
                    if v != base_btns[i]:
                        kind, idx, val = 'button', i, v
                        break
            # Check hats (changed tuple)
            if kind is None:
                for i in range(js.get_numhats()):
                    v = js.get_hat(i)
                    if v != base_hats[i]:
                        kind, idx, val = 'hat', i, v
                        break

            # Show live feedback
            if kind is not None:
                msg = (
                    f"\rDetectado: {kind}#{idx} valor={val} | "
                    "mantén 2s para confirmar"
                )
                sys.stdout.write(msg)
                sys.stdout.flush()
                # Initialize or check stability
                if detected is None or detected != (kind, idx):
                    detected = (kind, idx)
                    stable_since = time.time()
                else:
                    if time.time() - stable_since >= 2.0:
                        print("\n✅ Confirmado")
                        return (kind, idx, val)
            else:
                # No change detected; reset feedback line
                sys.stdout.write("\rEsperando entrada…                  ")
                sys.stdout.flush()

    # Directions
    kind, idx, _ = wait_for_change("➡️  Presiona DERECHA (Right)")
    if kind == 'axis':
        mapping['axes']['RIGHT'] = idx
    elif kind == 'hat':
        mapping['hats']['RIGHT'] = idx
    kind, idx, _ = wait_for_change("⬅️  Presiona IZQUIERDA (Left)")
    if kind == 'axis':
        mapping['axes']['LEFT'] = idx
    elif kind == 'hat':
        mapping['hats']['LEFT'] = idx
    kind, idx, _ = wait_for_change("⬆️  Presiona ARRIBA (Up)")
    if kind == 'axis':
        mapping['axes']['UP'] = idx
    elif kind == 'hat':
        mapping['hats']['UP'] = idx
    kind, idx, _ = wait_for_change("⬇️  Presiona ABAJO (Down)")
    if kind == 'axis':
        mapping['axes']['DOWN'] = idx
    elif kind == 'hat':
        mapping['hats']['DOWN'] = idx

    # Buttons
    for name, prompt in [
        ('A', "🅰️  Presiona A"),
        ('B', "🅱️  Presiona B"),
        ('X', "❎  Presiona X"),
        ('Y', "🟨  Presiona Y"),
        ('L', "👈  Presiona LB"),
        ('R', "👉  Presiona RB"),
        ('SELECT', "⏪  Presiona SELECT/BACK"),
        ('START', "⏩  Presiona START"),
    ]:
        kind, idx, _ = wait_for_change(prompt)
        if kind == 'button':
            mapping['buttons'][name] = idx
        else:
            print(f"⚠️ {name} detectado como {kind}, se espera botón.")

    outfile.write_text(json.dumps(mapping, indent=2))
    print(f"✅ Mapeo guardado en {outfile}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Xbox360 Sequence Recorder (Serial)"
    )
    parser.add_argument(
        '--port', required=True,
        help='Puerto serial (ej: /dev/tty.usbserial-XXXX)'
    )
    parser.add_argument(
        '--record', type=str,
        help='Ruta de salida JSON para grabar'
    )
    parser.add_argument('--play', type=str, help='Ruta JSON para reproducir')
    parser.add_argument(
        '--debug', action='store_true',
        help='Mostrar estado por frame'
    )
    parser.add_argument(
        '--raw-debug', action='store_true',
        help='Muestra valores crudos de axes/buttons/hats por frame'
    )
    parser.add_argument(
        '--invert-x', action='store_true',
        help='Invertir LEFT/RIGHT al reproducir'
    )
    parser.add_argument(
        '--deadzone', type=float, default=DEFAULT_DEADZONE,
        help='Umbral de deadzone para ejes (por defecto 0.3)'
    )
    parser.add_argument(
        '--release-each-frame', action='store_true',
        help='Envía 0 tras cada frame para evitar estados pegados en Serial'
    )
    parser.add_argument(
        '--calibrate', type=str,
        help='Genera un archivo JSON de mapeo interactivo'
    )
    parser.add_argument(
        '--mapping', type=str,
        help='Ruta a archivo JSON de mapeo para usar en grabación/reproducción'
    )
    args = parser.parse_args()

    if args.record and args.play:
        print("❌ Usa solo una opción: --record o --play")
        sys.exit(2)

    # Calibración independiente
    if args.calibrate:
        rc = calibrate_mapping(Path(args.calibrate))
        sys.exit(rc)

    if args.record:
        outfile = Path(args.record)
        # Allow explicit mapping file override
        if args.mapping:
            os.environ['X360_MAPPING'] = args.mapping
        rc = record_sequence(
            args.port,
            outfile,
            debug=args.debug,
            raw_debug=args.raw_debug,
            deadzone=args.deadzone,
            release_each_frame=args.release_each_frame,
        )
        sys.exit(rc)
    elif args.play:
        infile = Path(args.play)
        if args.mapping:
            os.environ['X360_MAPPING'] = args.mapping
        rc = play_sequence(
            args.port,
            infile,
            invert_x=args.invert_x,
            release_each_frame=args.release_each_frame,
        )
        sys.exit(rc)
    else:
        print("❌ Debes especificar --record o --play")
        sys.exit(2)


if __name__ == '__main__':
    if not pygame:
        print("\n💡 Instala dependencias: pip install pygame pyserial")
    main()
