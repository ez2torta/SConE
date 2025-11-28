#!/usr/bin/env python3
"""
Script de prueba para demostrar el modo Player 2 (eje X invertido)
"""

from app.controllers.serial_controller import SNESController
from app.sequence_player import SequencePlayer
from app.sequences import create_hadouken_sequence
import time

print("=" * 60)
print("Demo: Player 1 vs Player 2 Mode")
print("=" * 60)

controller = SNESController()

# Crear hadouken
hadouken = create_hadouken_sequence()

# Modo Player 1 (normal)
print("\n🎮 PLAYER 1 - Hadouken normal (↓ ↘ → + Punch)")
player1 = SequencePlayer(controller, invert_x_axis=False)
player1.play_sequence(hadouken)
time.sleep(1)

# Modo Player 2 (invertido)
print("\n🎮 PLAYER 2 - Hadouken invertido (↓ ↙ ← + Punch)")
player2 = SequencePlayer(controller, invert_x_axis=True)
player2.play_sequence(hadouken)

controller.close()
print("\n✅ Demo completada")
