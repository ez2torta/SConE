"""
Módulo para definir y manejar secuencias de inputs frame by frame para SNES.

Una secuencia es una lista de frames, donde cada frame especifica qué botones
deben estar presionados en ese frame exacto.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from .controllers.serial_controller import SNESButton


@dataclass
class FrameInput:
    """Representa el estado de botones en un frame específico."""

    frame: int
    buttons: List[SNESButton]
    duration_frames: int = 1  # Cuántos frames mantener este input

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame": self.frame,
            "buttons": [btn.name for btn in self.buttons],
            "duration_frames": self.duration_frames,
        }


class InputSequence:
    """Clase para definir secuencias de inputs frame by frame."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.frames: List[FrameInput] = []

    def add_frame(
        self, frame: int, buttons: List[SNESButton], duration_frames: int = 1
    ) -> "InputSequence":
        """Agrega un frame con botones específicos."""
        self.frames.append(FrameInput(frame, buttons, duration_frames))
        return self

    def add_button_press(
        self, start_frame: int, button: SNESButton, duration_frames: int = 1
    ) -> "InputSequence":
        """Agrega un botón presionado por una duración específica."""
        return self.add_frame(start_frame, [button], duration_frames)

    def add_combo(
        self, start_frame: int, buttons: List[SNESButton], duration_frames: int = 1
    ) -> "InputSequence":
        """Agrega una combinación de botones."""
        return self.add_frame(start_frame, buttons, duration_frames)

    def get_total_frames(self) -> int:
        """Obtiene el número total de frames de la secuencia."""
        if not self.frames:
            return 0
        last_frame = max(f.frame + f.duration_frames for f in self.frames)
        return last_frame

    def get_frame_buttons(self, frame: int) -> List[SNESButton]:
        """Obtiene qué botones deben estar presionados en un frame."""
        buttons = []
        for f in self.frames:
            if f.frame <= frame < f.frame + f.duration_frames:
                buttons.extend(f.buttons)
        return list(set(buttons))  # Remover duplicados

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "total_frames": self.get_total_frames(),
            "frames": [f.to_dict() for f in self.frames],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InputSequence":
        """Crea una secuencia desde un diccionario."""
        seq = cls(data["name"], data.get("description", ""))
        for frame_data in data["frames"]:
            buttons = [SNESButton[btn] for btn in frame_data["buttons"]]
            seq.add_frame(
                frame_data["frame"], buttons, frame_data.get("duration_frames", 1)
            )
        return seq


def create_button_test_sequence() -> InputSequence:
    """
    Crea una secuencia de prueba que presiona cada botón uno por uno.
    presionar abajo 2 segundos, adelante 2 segundos, luego presionar X por 10 frames.
    finalmente probar los otros 2 (salto para atras con Y)
    luego salto para adelante con B (pero salto pequeño)
    y luego abajo con A
    """
    seq = InputSequence("Button Test", "Test sequence pressing each button")
    seq.add_button_press(0, SNESButton.DOWN, 120)  # Abajo por 2 segundos
    seq.add_button_press(120, SNESButton.RIGHT, 120)  # Adelante por 2 segundos

    seq.add_button_press(240, SNESButton.X, 5)  # X por 10 frames
    seq.add_combo(245, [], 5)  # X por 10 frames
    seq.add_combo(250, [SNESButton.RIGHT, SNESButton.B], 20)  # X por 10 frames
    seq.add_button_press(255, SNESButton.Y, 10)  # Y por 10 frames
    seq.add_combo(265, [SNESButton.UP, SNESButton.LEFT], 5)  # Salto atrás
    seq.add_button_press(270, SNESButton.B, 5)  # B por 5 frames
    seq.add_button_press(275, SNESButton.A, 10)  # Abajo con A
    return seq


# Secuencias predefinidas comunes
def create_hadouken_sequence() -> InputSequence:
    """Secuencia de Hadouken (Street Fighter): ↓ ↘ → + Puño"""
    seq = InputSequence("Hadouken", "Hadouken fireball combo")
    seq.add_button_press(0, SNESButton.DOWN, 2)  # ↓
    seq.add_button_press(2, SNESButton.RIGHT, 1)  # ↓↘
    seq.add_combo(3, [SNESButton.DOWN, SNESButton.RIGHT], 1)  # ↘
    seq.add_combo(4, [SNESButton.RIGHT, SNESButton.Y], 2)  # → + Puño
    return seq


def create_shoryuken_sequence() -> InputSequence:
    """Secuencia de Shoryuken: → ↓ ↘ + Puño"""
    seq = InputSequence("Shoryuken", "Shoryuken uppercut combo")
    seq.add_button_press(0, SNESButton.RIGHT, 1)  # →
    seq.add_button_press(1, SNESButton.DOWN, 1)  # →↓
    seq.add_combo(2, [SNESButton.RIGHT, SNESButton.DOWN], 1)  # ↘
    seq.add_combo(3, [SNESButton.RIGHT, SNESButton.Y], 3)  # → + Puño
    return seq


def create_walk_sequence() -> InputSequence:
    """Secuencia de caminar hacia la derecha por 30 frames."""
    seq = InputSequence("Walk Right", "Walk to the right for 30 frames")
    seq.add_button_press(0, SNESButton.RIGHT, 30)
    return seq


def create_walk_back_sequence() -> InputSequence:
    """Secuencia de caminar hacia la izquierda por 30 frames."""
    seq = InputSequence("Walk Left", "Walk to the left for 30 frames")
    seq.add_button_press(0, SNESButton.LEFT, 30)
    return seq


def create_run_sequence() -> InputSequence:
    """Secuencia de correr hacia la derecha por 20 frames."""
    seq = InputSequence("Run Right", "Run to the right for 20 frames")
    seq.add_button_press(0, SNESButton.RIGHT, 20)
    seq.add_button_press(0, SNESButton.B, 20)  # Mantener botón de correr
    return seq


def create_flashkick_sequence() -> InputSequence:
    """Secuencia de Shoryuken: carga abajo-atras (30 frames), luego arriba + B"""
    seq = InputSequence("Flashkick", "Down charge move")
    seq.add_combo(0, [SNESButton.LEFT, SNESButton.DOWN], 30)  # carga abajo atras
    seq.add_combo(30, [SNESButton.UP, SNESButton.B], 3)  # arriba + B
    return seq


def create_konami_code_sequence() -> InputSequence:
    """Código Konami: ↑↑↓↓←→←→ B A"""
    seq = InputSequence("Konami Code", "The legendary Konami code")
    seq.add_button_press(0, SNESButton.UP, 1)
    seq.add_button_press(2, SNESButton.UP, 1)
    seq.add_button_press(4, SNESButton.DOWN, 1)
    seq.add_button_press(6, SNESButton.DOWN, 1)
    seq.add_button_press(8, SNESButton.LEFT, 1)
    seq.add_button_press(10, SNESButton.RIGHT, 1)
    seq.add_button_press(12, SNESButton.LEFT, 1)
    seq.add_button_press(14, SNESButton.RIGHT, 1)
    seq.add_button_press(16, SNESButton.B, 1)
    seq.add_button_press(18, SNESButton.A, 1)
    return seq


def create_basic_combo_sequence() -> InputSequence:
    """Combo básico: A B A B"""
    seq = InputSequence("Basic Combo", "Simple alternating attack combo")
    seq.add_button_press(0, SNESButton.A, 2)
    seq.add_button_press(3, SNESButton.B, 2)
    seq.add_button_press(6, SNESButton.A, 2)
    seq.add_button_press(9, SNESButton.B, 2)
    return seq


def create_jump_sequence() -> InputSequence:
    """Salto: ↑ + A"""
    seq = InputSequence("Jump", "Jump with attack")
    seq.add_combo(0, [SNESButton.UP, SNESButton.A], 5)
    return seq
