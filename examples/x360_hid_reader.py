#!/usr/bin/env python3
"""
Xbox 360 HID Reader (macOS)

Reads raw HID input reports from USB HID devices using hidapi.
Useful for diagnosing controller mappings without pygame.

Dependencies:
  pip install hid
  # On macOS, you may need: brew install hidapi

Usage:
  python examples/x360_hid_reader.py
  python examples/x360_hid_reader.py --vendor 0x045e --product 0x028e

Notes:
- Xbox 360 controllers may use third-party drivers. Vendor/Product IDs vary.
- Prints raw report bytes; you can parse axes/buttons later as needed.
"""

import argparse
import binascii
import time
from typing import Optional

try:
    import hid  # pyhidapi
except Exception:
    hid = None


def list_devices():
    for d in hid.enumerate():
        vendor = d['vendor_id']
        product = d['product_id']
        msg = (
            f"- {d['manufacturer_string']} {d['product_string']} "
            f"vid=0x{vendor:04x} pid=0x{product:04x} "
            f"path={d['path'].decode()}"
        )
        print(msg)


def open_device(vendor_id: Optional[int], product_id: Optional[int]):
    if vendor_id and product_id:
        try:
            return hid.Device(vendor_id, product_id)
        except Exception:
            pass
    # Fallback: open first gamepad/joystick-like device
    for d in hid.enumerate():
        name = (d.get('product_string') or '').lower()
        if 'xbox' in name or 'controller' in name or 'gamepad' in name:
            try:
                return hid.Device(d['vendor_id'], d['product_id'])
            except Exception:
                continue
    # else open first device
    for d in hid.enumerate():
        try:
            return hid.Device(d['vendor_id'], d['product_id'])
        except Exception:
            continue
    return None


def main():
    parser = argparse.ArgumentParser(description='HID reader for controllers')
    parser.add_argument(
        '--vendor', type=lambda x: int(x, 16),
        help='Vendor ID hex (e.g., 0x045e)'
    )
    parser.add_argument(
        '--product', type=lambda x: int(x, 16),
        help='Product ID hex (e.g., 0x028e)'
    )
    parser.add_argument('--list', action='store_true', help='List HID devices')
    args = parser.parse_args()

    if hid is None:
        print('❌ hidapi no disponible. Instala:')
        print('   pip install hid')
        print('   brew install hidapi')
        return 2

    if args.list:
        list_devices()
        return 0

    dev = open_device(args.vendor, args.product)
    if not dev:
        print('❌ No se pudo abrir un dispositivo HID')
        return 2

    print('✅ Leyendo reportes HID. Ctrl+C para salir.')
    dev.nonblocking = True
    try:
        while True:
            data = dev.read(64)
            if data:
                hexstr = binascii.hexlify(bytes(data)).decode()
                print(f"Report: {hexstr}")
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        dev.close()
    return 0


if __name__ == '__main__':
    main()
