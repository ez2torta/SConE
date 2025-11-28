#!/usr/bin/env python3
"""HID-based SNES Recorder para Brook / Xbox360.

Funciones:
  - Calibrar (genera mapeo JSON de botones/ejes)
  - Grabar secuencia de bitmask SNES y enviarla por Serial
  - Reproducir secuencia previamente grabada
"""
import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))
from test_ble_input import SNESControllerSerial, BUTTONS  # noqa: E402

try:
    import hid
except Exception:  # pragma: no cover
    hid = None  # type: ignore

FRAME_RATE = 60.0
FRAME_DT = 1.0 / FRAME_RATE
AXIS_THRESHOLD_DEFAULT = 20
STABLE_SECONDS = 1.5
TARGETS = ['RIGHT', 'LEFT', 'UP', 'DOWN', 'A', 'B', 'X', 'Y', 'L', 'R', 'SELECT', 'START']


def open_device(vendor: Optional[int], product: Optional[int]):
    if not hid:
        return None
    if vendor and product:
        try:
            return hid.Device(vendor, product)
        except Exception:
            pass
    for d in hid.enumerate():
        name = (d.get('product_string') or '').lower()
        if any(k in name for k in ['brook', 'xbox', 'controller']):
            try:
                return hid.Device(d['vendor_id'], d['product_id'])
            except Exception:
                continue
    return None


def read_report(dev) -> Optional[bytes]:
    data = dev.read(64)
    if data:
        return bytes(data)
    return None


def diff_bytes(a: bytes, b: bytes) -> List[int]:
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def calibrate(
    mapping_path: Path,
    vendor: int,
    product: int,
    axis_threshold: int,
    cal_debug: bool = False,
) -> int:
    if not hid:
        print('❌ hidapi no disponible')
        return 2
    dev = open_device(vendor, product)
    if not dev:
        print('❌ No se pudo abrir HID')
        return 2
    dev.nonblocking = True
    print('✅ Dispositivo abierto. Capturando baseline...')
    baseline = None
    t0 = time.time()
    while time.time() - t0 < 0.5:
        rpt = read_report(dev)
        if rpt:
            baseline = rpt
        time.sleep(0.01)
    if baseline is None:
        print('❌ Sin reportes iniciales')
        dev.close()
        return 2

    digital_map: List[Dict] = []
    axis_map: Dict[str, Dict] = {}

    for target in TARGETS:
        print(f'👉 Mantén: {target} ({STABLE_SECONDS}s)')
        stable_byte = None
        stable_since = 0.0
        last = baseline
        confirmed = False
        idle_start = time.time()
        while not confirmed:
            rpt = read_report(dev)
            if not rpt:
                time.sleep(0.005)
                if time.time() - idle_start > 15:
                    print(f'⚠️ Timeout {target}')
                    break
                continue
            changed = diff_bytes(last, rpt)
            last = rpt
            candidate = None
            bit_val = 0
            for idx in changed:
                bit_val = (baseline[idx] ^ rpt[idx]) & 0xFF
                delta = abs(rpt[idx] - baseline[idx])
                if delta >= axis_threshold or bit_val != 0:
                    candidate = idx
                    break
            if cal_debug:
                preview = ' '.join(f'{i}:{baseline[i]:02x}->{rpt[i]:02x}' for i in changed[:6])
                delta_show = abs(rpt[candidate] - baseline[candidate]) if candidate is not None else 0
                msg = f'\r{target} cand={candidate} ch={changed[:6]} d={delta_show} bits=0x{bit_val:02x} {preview:40}'
                sys.stdout.write(msg[:79])
                sys.stdout.flush()
            if candidate is not None:
                if stable_byte != candidate:
                    stable_byte = candidate
                    stable_since = time.time()
                else:
                    if time.time() - stable_since >= STABLE_SECONDS:
                        base_val = baseline[candidate]
                        new_val = rpt[candidate]
                        if target in ['RIGHT', 'LEFT', 'UP', 'DOWN'] and abs(new_val - base_val) >= axis_threshold:
                            axis_name = 'H' if target in ['LEFT', 'RIGHT'] else 'V'
                            if axis_name not in axis_map:
                                axis_map[axis_name] = {
                                    'name': axis_name,
                                    'byte': candidate,
                                    'center': base_val,
                                }
                            print(f'\n✅ {target} eje byte {candidate}')
                        else:
                            bit_found = None
                            for bit in range(8):
                                if (base_val ^ new_val) & (1 << bit):
                                    bit_found = bit
                                    break
                            if bit_found is None:
                                bit_found = 0
                            digital_map.append({
                                'name': target,
                                'byte': candidate,
                                'bit': bit_found,
                            })
                            print(f'\n✅ {target} byte {candidate} bit {bit_found}')
                        confirmed = True
            else:
                if cal_debug:
                    sys.stdout.write(f'\r{target} sin cambios'.ljust(40))
                    sys.stdout.flush()
            if time.time() - idle_start > 15:
                print(f'⚠️ Timeout {target}')
                break
        time.sleep(0.3)

    mapping = {'digital': digital_map, 'axes': list(axis_map.values())}
    mapping_path.write_text(json.dumps(mapping, indent=2))
    print(f'💾 Mapeo guardado en {mapping_path}')
    dev.close()
    return 0


def load_mapping(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f'Mapping no encontrado: {path}')
    return json.loads(path.read_text())


def build_bitmask(report: bytes, mapping: Dict, axis_threshold: int) -> int:
    state = 0
    for axis_desc in mapping.get('axes', []):
        byte_idx = axis_desc['byte']
        center = axis_desc.get('center', 128)
        val = report[byte_idx]
        if axis_desc.get('name') == 'H':
            if val > center + axis_threshold:
                state |= BUTTONS['RIGHT']
            elif val < center - axis_threshold:
                state |= BUTTONS['LEFT']
        elif axis_desc.get('name') == 'V':
            if val < center - axis_threshold:
                state |= BUTTONS['UP']
            elif val > center + axis_threshold:
                state |= BUTTONS['DOWN']
    for d in mapping.get('digital', []):
        b = d['byte']
        bit = d['bit']
        if b < len(report) and (report[b] & (1 << bit)):
            name = d['name']
            if name in BUTTONS:
                state |= BUTTONS[name]
    return state


def record_sequence(
    port: str,
    mapping_path: Path,
    outfile: Path,
    vendor: Optional[int],
    product: Optional[int],
    axis_threshold: int,
    debug: bool = False,
) -> int:
    if not hid:
        print('❌ hidapi no disponible')
        return 2
    mapping = load_mapping(mapping_path)
    dev = open_device(vendor, product)
    if not dev:
        print('❌ No se pudo abrir HID para grabar')
        return 2
    dev.nonblocking = True
    controller = SNESControllerSerial(port)
    print('🎬 Grabación. START+SELECT para terminar')
    frames: List[int] = []
    start = time.time()
    stop_hold = 0.0
    try:
        while True:
            rpt = read_report(dev)
            if rpt:
                state = build_bitmask(rpt, mapping, axis_threshold)
                if debug:
                    raw = ' '.join(f'{b:02x}' for b in rpt[:8])
                    msg = (
                        f'\rframe={len(frames):04d} state=0x{state:08x} '
                        f'raw={raw}'
                    )
                    sys.stdout.write(msg[:79])
                    sys.stdout.flush()
                frames.append(state)
                controller.send_buttons(state)
                if (
                    (state & BUTTONS.get('START', 0)) and
                    (state & BUTTONS.get('SELECT', 0))
                ):
                    if stop_hold == 0.0:
                        stop_hold = time.time()
                    elif time.time() - stop_hold >= 0.5:
                        print('\n⏹️  Stop')
                        break
                else:
                    stop_hold = 0.0
            time.sleep(FRAME_DT)
    finally:
        controller.send_buttons(0)
        controller.close()
        dev.close()
    duration = time.time() - start
    data = {
        'fps': FRAME_RATE,
        'frames': frames,
        'duration_sec': round(duration, 3),
        'count': len(frames),
    }
    outfile.write_text(json.dumps(data, indent=2))
    print(f'💾 Secuencia guardada en {outfile} ({len(frames)} frames)')
    return 0


def play_sequence(port: str, infile: Path) -> int:
    if not infile.exists():
        print('❌ Secuencia no existe')
        return 2
    data = json.loads(infile.read_text())
    frames = data.get('frames', [])
    fps = float(data.get('fps', FRAME_RATE))
    dt = 1.0 / fps
    controller = SNESControllerSerial(port)
    print(f'▶️ Reproduciendo {len(frames)} frames a {fps} FPS')
    try:
        for b in frames:
            controller.send_buttons(int(b))
            time.sleep(dt)
    finally:
        controller.send_buttons(0)
        controller.close()
    print('✅ Reproducción completa')
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description='HID SNES Recorder')
    parser.add_argument('--vendor', type=lambda x: int(x, 16), help='Vendor hex')
    parser.add_argument('--product', type=lambda x: int(x, 16), help='Product hex')
    parser.add_argument('--calibrate', type=str, help='Generar mapeo JSON')
    parser.add_argument('--cal-debug', action='store_true', help='Debug calibración')
    parser.add_argument('--axis-threshold', type=int, default=AXIS_THRESHOLD_DEFAULT, help='Umbral eje')
    parser.add_argument('--record', type=str, help='Grabar secuencia JSON')
    parser.add_argument('--rec-debug', action='store_true', help='Debug grabación')
    parser.add_argument('--play', type=str, help='Reproducir secuencia JSON')
    parser.add_argument('--mapping', type=str, help='Ruta mapeo JSON')
    parser.add_argument('--port', type=str, help='Puerto serial')
    args = parser.parse_args()

    if args.calibrate:
        if not args.vendor or not args.product:
            print('❌ Requiere --vendor y --product')
            sys.exit(2)
        rc = calibrate(
            Path(args.calibrate), args.vendor, args.product,
            axis_threshold=args.axis_threshold, cal_debug=args.cal_debug
        )
        sys.exit(rc)
    if args.record:
        if not args.port or not args.mapping:
            print('❌ Requiere --port y --mapping')
            sys.exit(2)
        rc = record_sequence(
            args.port, Path(args.mapping), Path(args.record),
            args.vendor, args.product,
            axis_threshold=args.axis_threshold, debug=args.rec_debug
        )
        sys.exit(rc)
    if args.play:
        if not args.port:
            print('❌ Requiere --port')
            sys.exit(2)
        rc = play_sequence(args.port, Path(args.play))
        sys.exit(rc)
    print('❌ Usa --calibrate, --record o --play')
    sys.exit(2)


if __name__ == '__main__':
    main()
