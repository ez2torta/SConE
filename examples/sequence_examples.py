#!/usr/bin/env python3
"""
Ejemplo de uso de los módulos de secuencias de SNES.

Este script demuestra cómo crear y reproducir secuencias de inputs
frame by frame usando los módulos sequences.py y sequence_player.py.
"""

from app.controllers.serial_controller import SNESController, SNESButton
from app.sequences import (
    InputSequence, create_hadouken_sequence, create_shoryuken_sequence,
    create_konami_code_sequence, create_basic_combo_sequence,
    create_jump_sequence
)
from app.sequence_player import SequencePlayer


def ejemplo_basico():
    """Ejemplo básico de creación y reproducción de secuencia."""
    print("🎮 Ejemplo Básico de Secuencias SNES")
    print("=" * 50)

    # Crear una secuencia simple
    seq = InputSequence("Mi Secuencia", "Una secuencia de ejemplo")

    # Agregar algunos inputs
    seq.add_button_press(0, SNESButton.A, 3)    # A por 3 frames
    seq.add_button_press(5, SNESButton.B, 2)    # B por 2 frames
    seq.add_combo(10, [SNESButton.UP, SNESButton.A], 4)  # UP + A por 4 frames

    print(f"Secuencia creada: {seq.name}")
    print(f"Frames totales: {seq.get_total_frames()}")
    print(f"Frames: {len(seq.frames)}")

    # Mostrar qué botones en cada frame
    for frame in range(seq.get_total_frames()):
        buttons = seq.get_frame_buttons(frame)
        if buttons:
            names = [b.name for b in buttons]
            print(f"Frame {frame}: {names}")

    print()


def ejemplo_hadouken():
    """Ejemplo usando la secuencia predefinida de Hadouken."""
    print("🔥 Ejemplo: Hadouken Sequence")
    print("=" * 30)

    # Crear la secuencia de Hadouken
    hadouken = create_hadouken_sequence()

    print(f"Nombre: {hadouken.name}")
    print(f"Descripción: {hadouken.description}")
    print(f"Frames totales: {hadouken.get_total_frames()}")

    # Mostrar la secuencia frame por frame
    print("\nSecuencia frame por frame:")
    for frame in range(hadouken.get_total_frames()):
        buttons = hadouken.get_frame_buttons(frame)
        if buttons:
            names = [b.name for b in buttons]
            print(f"Frame {frame:2d}: {names}")

    print()


def ejemplo_con_controlador():
    """Ejemplo reproduciendo secuencias con el controlador real."""
    print("🎯 Ejemplo con Controlador Real")
    print("=" * 35)

    try:
        # Crear controlador
        controller = SNESController()
        print("✅ Controlador conectado")

        # Crear reproductor
        player = SequencePlayer(controller, fps=60)

        # Crear una secuencia simple
        seq = InputSequence("Test Sequence", "Secuencia de prueba")
        seq.add_button_press(0, SNESButton.A, 2)
        seq.add_button_press(5, SNESButton.B, 2)
        seq.add_button_press(10, SNESButton.START, 1)

        # Reproducir la secuencia
        player.play_sequence(seq)

        # Cerrar controlador
        controller.close()
        print("✅ Controlador cerrado")

    except (OSError, ValueError, RuntimeError) as e:
        print(f"❌ Error: {e}")
        print("Nota: Asegúrate de que el ESP32 esté conectado")


def ejemplo_guardar_cargar():
    """Ejemplo de guardar y cargar secuencias en JSON."""
    print("💾 Ejemplo: Guardar/Cargar Secuencias")
    print("=" * 40)

    # Crear una secuencia personalizada
    seq = InputSequence("Mi Combo", "Un combo personalizado")
    seq.add_button_press(0, SNESButton.X, 3)
    seq.add_button_press(4, SNESButton.Y, 2)
    seq.add_combo(7, [SNESButton.LEFT, SNESButton.A], 5)

    # Guardar en JSON
    filename = "mi_combo.json"
    player = SequencePlayer(None)  # Sin controlador para solo guardar
    player.save_sequence(seq, filename)

    # Cargar desde JSON
    loaded_seq = player.load_sequence(filename)

    print(f"Secuencia cargada: {loaded_seq.name}")
    print(f"Descripción: {loaded_seq.description}")
    print(f"Frames: {len(loaded_seq.frames)}")

    # Mostrar contenido
    data = loaded_seq.to_dict()
    print(f"Contenido JSON: {data}")


def ejemplo_secuencias_predefinidas():
    """Mostrar todas las secuencias predefinidas."""
    print("📚 Secuencias Predefinidas Disponibles")
    print("=" * 45)

    sequences = [
        ("Hadouken", create_hadouken_sequence()),
        ("Shoryuken", create_shoryuken_sequence()),
        ("Konami Code", create_konami_code_sequence()),
        ("Basic Combo", create_basic_combo_sequence()),
        ("Jump", create_jump_sequence())
    ]

    for name, seq in sequences:
        print(f"\n{name}:")
        print(f"  Descripción: {seq.description}")
        print(f"  Frames totales: {seq.get_total_frames()}")
        print(f"  Número de inputs: {len(seq.frames)}")

        # Mostrar primeros 5 frames
        print("  Primeros frames:")
        for frame in range(min(5, seq.get_total_frames())):
            buttons = seq.get_frame_buttons(frame)
            if buttons:
                names = [b.name for b in buttons]
                print(f"    Frame {frame}: {names}")


def main():
    """Función principal con menú de ejemplos."""
    print("🎮 SNES Sequence Examples")
    print("=" * 25)
    print("1. Ejemplo Básico")
    print("2. Hadouken Sequence")
    print("3. Con Controlador Real")
    print("4. Guardar/Cargar JSON")
    print("5. Secuencias Predefinidas")
    print("6. Todos los ejemplos")

    choice = input("\nElige un ejemplo (1-6): ").strip()

    examples = {
        '1': ejemplo_basico,
        '2': ejemplo_hadouken,
        '3': ejemplo_con_controlador,
        '4': ejemplo_guardar_cargar,
        '5': ejemplo_secuencias_predefinidas,
        '6': lambda: [
            ejemplo_basico(),
            ejemplo_hadouken(),
            ejemplo_secuencias_predefinidas(),
            ejemplo_guardar_cargar()
        ]
    }

    if choice in examples:
        examples[choice]()
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    main()
