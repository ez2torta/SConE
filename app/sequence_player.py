"""
Módulo de pruebas para ejecutar secuencias de inputs frame by frame.

Permite reproducir secuencias de botones con timing preciso basado en frames.
"""

import time
import json
import sys
from pathlib import Path
from typing import Optional

# Agregar el directorio padre al path si se ejecuta como script
if __name__ == "__main__" and __package__ is None:
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

# Imports que funcionan tanto como módulo como script
try:
    from .controllers.serial_controller import SNESController, SNESButton
    from .sequences import (
        InputSequence,
        create_hadouken_sequence,
        create_shoryuken_sequence,
        create_konami_code_sequence,
        create_basic_combo_sequence,
        create_jump_sequence,
        create_flashkick_sequence,
        create_button_test_sequence,
    )
except ImportError:
    from app.controllers.serial_controller import SNESController, SNESButton
    from app.sequences import (
        InputSequence,
        create_hadouken_sequence,
        create_shoryuken_sequence,
        create_konami_code_sequence,
        create_basic_combo_sequence,
        create_jump_sequence,
        create_flashkick_sequence,
        create_button_test_sequence,
    )


class SequencePlayer:
    """Reproductor de secuencias de inputs con timing preciso."""

    def __init__(self, controller: SNESController, fps: int = 60,
                 invert_x_axis: bool = False):
        """
        Inicializa el reproductor.

        Args:
            controller: Instancia del controlador SNES
            fps: Frames por segundo (típicamente 60 para SNES)
            invert_x_axis: Si True, invierte LEFT/RIGHT (para player 2)
        """
        self.controller = controller
        self.fps = fps
        self.frame_time = 1.0 / fps  # Tiempo por frame en segundos
        self.invert_x_axis = invert_x_axis

    def _invert_buttons(self, buttons):
        """
        Invierte los botones del eje X si invert_x_axis está activo.

        Args:
            buttons: Lista de SNESButton

        Returns:
            Lista de SNESButton con direcciones invertidas si aplica
        """
        if not self.invert_x_axis:
            return buttons

        inverted = []
        for button in buttons:
            if button == SNESButton.LEFT:
                inverted.append(SNESButton.RIGHT)
            elif button == SNESButton.RIGHT:
                inverted.append(SNESButton.LEFT)
            else:
                inverted.append(button)
        return inverted

    def play_sequence(self, sequence: InputSequence,
                      start_frame: int = 0) -> None:
        """
        Reproduce una secuencia completa.

        Args:
            sequence: La secuencia a reproducir
            start_frame: Frame desde donde empezar (para debugging)
        """
        print(f"🎮 Reproduciendo secuencia: {sequence.name}")
        if sequence.description:
            print(f"📝 {sequence.description}")
        if self.invert_x_axis:
            print("🔄 Modo Player 2 (eje X invertido)")

        total_frames = sequence.get_total_frames()
        duration = total_frames / self.fps
        print(f"📼 Total frames: {total_frames} ({duration:.2f}s)")

        for frame in range(start_frame, total_frames):
            buttons = sequence.get_frame_buttons(frame)

            if buttons:
                # Invertir direcciones si es necesario
                buttons = self._invert_buttons(buttons)
                self.controller.press_buttons(buttons)
                button_names = [b.name for b in buttons]
                print(f"Frame {frame:3d}: {button_names}")
            else:
                self.controller.release_all()
                print(f"Frame {frame:3d}: [RELEASE]")

            time.sleep(self.frame_time)

        # Asegurar que se suelten todos los botones al final
        self.controller.release_all()
        print("✅ Secuencia completada")

    def play_frame_by_frame(self, sequence: InputSequence,
                            start_frame: int = 0) -> None:
        """
        Modo interactivo: reproduce frame por frame esperando
        input del usuario.
        """
        print(f"🎮 Modo Frame-by-Frame: {sequence.name}")
        if self.invert_x_axis:
            print("🔄 Modo Player 2 (eje X invertido)")
        print("Presiona Enter para avanzar al siguiente frame, 'q' para salir")

        total_frames = sequence.get_total_frames()

        for frame in range(start_frame, total_frames):
            buttons = sequence.get_frame_buttons(frame)

            if buttons:
                # Invertir direcciones si es necesario
                buttons = self._invert_buttons(buttons)
                button_names = [b.name for b in buttons]
                print(f"Frame {frame:3d}: {button_names}")
            else:
                print(f"Frame {frame:3d}: [RELEASE]")

            # Esperar input del usuario
            user_input = input("> ").strip().lower()
            if user_input == 'q':
                break

            # Enviar los botones
            if buttons:
                self.controller.press_buttons(buttons)
            else:
                self.controller.release_all()

        self.controller.release_all()
        print("✅ Reproducción frame-by-frame completada")

    def save_sequence(self, sequence: InputSequence, filename: str) -> None:
        """Guarda una secuencia en un archivo JSON."""
        data = sequence.to_dict()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Secuencia guardada en {filename}")

    def load_sequence(self, filename: str) -> InputSequence:
        """Carga una secuencia desde un archivo JSON."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sequence = InputSequence.from_dict(data)
        print(f"📂 Secuencia cargada: {sequence.name}")
        return sequence


def test_basic_sequences():
    """Prueba básica con secuencias predefinidas."""
    print("🧪 Iniciando pruebas de secuencias...")

    try:
        controller = SNESController()
        player = SequencePlayer(controller)

        # Probar secuencias predefinidas
        sequences = [
            create_button_test_sequence(),
            create_flashkick_sequence(),
            create_shoryuken_sequence(),
            create_konami_code_sequence(),
            create_basic_combo_sequence(),
            create_jump_sequence()
        ]

        for seq in sequences:
            print(f"\n{'='*50}")
            player.play_sequence(seq)
            time.sleep(1)  # Pausa entre secuencias

        controller.close()

    except (OSError, ValueError, RuntimeError) as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()


def interactive_sequence_test():
    """Modo interactivo para probar secuencias."""
    print("🎯 Modo Interactivo de Secuencias")
    print("Comandos:")
    print("  hadouken    - Hadouken combo")
    print("  shoryuken   - Shoryuken combo")
    print("  konami      - Código Konami")
    print("  combo       - Combo básico")
    print("  jump        - Salto")
    print("  custom      - Crear secuencia personalizada")
    print("  load <file> - Cargar secuencia desde archivo")
    print("  save <file> - Guardar última secuencia")
    print("  frame       - Modo frame-by-frame")
    print("  p2          - Toggle Player 2 mode (invierte eje X)")
    print("  quit        - Salir")

    controller = None
    player = None
    last_sequence = None
    invert_x = False

    try:
        controller = SNESController()
        player = SequencePlayer(controller, invert_x_axis=invert_x)

        while True:
            cmd = input("\n> ").strip().lower().split()

            if not cmd:
                continue

            command = cmd[0]

            if command == 'quit':
                break
            elif command == 'p2':
                invert_x = not invert_x
                player = SequencePlayer(controller, invert_x_axis=invert_x)
                mode = "Player 2 🔄" if invert_x else "Player 1 ➡️"
                print(f"✅ Modo cambiado a: {mode}")
            elif command == 'hadouken':
                seq = create_hadouken_sequence()
                player.play_sequence(seq)
                last_sequence = seq
            elif command == 'shoryuken':
                seq = create_shoryuken_sequence()
                player.play_sequence(seq)
                last_sequence = seq
            elif command == 'konami':
                seq = create_konami_code_sequence()
                player.play_sequence(seq)
                last_sequence = seq
            elif command == 'combo':
                seq = create_basic_combo_sequence()
                player.play_sequence(seq)
                last_sequence = seq
            elif command == 'jump':
                seq = create_jump_sequence()
                player.play_sequence(seq)
                last_sequence = seq
            elif command == 'frame':
                if last_sequence:
                    player.play_frame_by_frame(last_sequence)
                else:
                    print("❌ No hay secuencia cargada. Ejecuta una primero.")
            elif command == 'save' and len(cmd) > 1:
                if last_sequence:
                    player.save_sequence(last_sequence, cmd[1])
                else:
                    print("❌ No hay secuencia para guardar.")
            elif command == 'load' and len(cmd) > 1:
                try:
                    seq = player.load_sequence(cmd[1])
                    player.play_sequence(seq)
                    last_sequence = seq
                except FileNotFoundError:
                    print(f"❌ Archivo no encontrado: {cmd[1]}")
                except (OSError, ValueError, RuntimeError) as e:
                    print(f"❌ Error cargando secuencia: {e}")
            elif command == 'custom':
                seq = create_custom_sequence()
                if seq:
                    player.play_sequence(seq)
                    last_sequence = seq
            else:
                print("❌ Comando desconocido")

    except KeyboardInterrupt:
        print("\n👋 Interrumpido por usuario")
    except (OSError, ValueError, RuntimeError) as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if controller:
            controller.close()


def create_custom_sequence() -> Optional[InputSequence]:
    """Crea una secuencia personalizada de manera interactiva."""
    print("🎨 Creando secuencia personalizada")
    name = input("Nombre de la secuencia: ").strip()
    if not name:
        return None

    description = input("Descripción (opcional): ").strip()

    seq = InputSequence(name, description)

    print("Agrega frames (formato: frame botón [duración])")
    print("Ejemplos:")
    print("  0 A 2      - Frame 0: A por 2 frames")
    print("  3 UP A 1   - Frame 3: UP+A por 1 frame")
    print("  done       - Terminar")

    while True:
        line = input("Frame> ").strip()
        if line.lower() == 'done':
            break

        parts = line.split()
        if len(parts) < 2:
            print("❌ Formato inválido. Usa: frame botón [duración]")
            continue

        try:
            frame = int(parts[0])
            duration = int(parts[-1]) if len(parts) > 2 else 1
            button_names = parts[1:-1] if len(parts) > 2 else parts[1:]

            buttons = []
            for btn_name in button_names:
                try:
                    button = SNESButton[btn_name.upper()]
                    buttons.append(button)
                except KeyError:
                    print(f"❌ Botón desconocido: {btn_name}")
                    buttons = []
                    break

            if buttons:
                seq.add_frame(frame, buttons, duration)
                print(f"✅ Agregado: Frame {frame}, {button_names}, "
                      f"duración {duration}")

        except ValueError as e:
            print(f"❌ Error: {e}")

    if seq.frames:
        return seq
    else:
        print("❌ No se agregaron frames")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_sequence_test()
    else:
        test_basic_sequences()
