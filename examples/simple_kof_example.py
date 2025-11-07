#!/usr/bin/env python3
"""
Ejemplo simple de uso del KOF Sequence Engine
Muestra cómo ejecutar secuencias desde JSON de manera programática
"""

import asyncio
from pathlib import Path

from kof_sequence_engine import SequenceEngine
from test_ble_input import SNESControllerBLE


async def ejemplo_basico():
    """Ejemplo básico: ejecutar algunos ataques"""
    print("\n" + "="*70)
    print("EJEMPLO 1: Ataques Básicos")
    print("="*70)
    
    # Conectar controlador
    controller = SNESControllerBLE()
    await controller.connect()
    
    # Crear motor
    config_file = Path(__file__).parent / 'kof_sequences.json'
    engine = SequenceEngine(config_file, controller)
    
    # Ejecutar ataques básicos
    print("\n🥊 Ejecutando ataques básicos...")
    await engine.execute_sequence('st_A', category='basic_attacks')
    await asyncio.sleep(0.5)
    
    await engine.execute_sequence('cr_B', category='basic_attacks')
    await asyncio.sleep(0.5)
    
    await engine.execute_sequence('cl_C', category='basic_attacks')
    
    # Desconectar
    await controller.disconnect()
    print("\n✅ Ejemplo completado!\n")


async def ejemplo_combos():
    """Ejemplo: ejecutar combos completos"""
    print("\n" + "="*70)
    print("EJEMPLO 2: Combos")
    print("="*70)
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    config_file = Path(__file__).parent / 'kof_sequences.json'
    engine = SequenceEngine(config_file, controller)
    
    # Ejecutar combos
    print("\n💥 Ejecutando combos...")
    
    print("\n--- Combo 1: cr.B > cr.A > QCF+A ---")
    await engine.execute_combo('cr_B_cr_A_QCF_A')
    await asyncio.sleep(1)
    
    print("\n--- Combo 2: cl.C > QCF+C ---")
    await engine.execute_combo('cl_C_QCF_C')
    await asyncio.sleep(1)
    
    print("\n--- Combo 3: j.D > cl.C > DP+A ---")
    await engine.execute_combo('j_D_cl_C_DP_A')
    
    await controller.disconnect()
    print("\n✅ Combos completados!\n")


async def ejemplo_movimiento():
    """Ejemplo: secuencias de movimiento"""
    print("\n" + "="*70)
    print("EJEMPLO 3: Movimiento")
    print("="*70)
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    config_file = Path(__file__).parent / 'kof_sequences.json'
    engine = SequenceEngine(config_file, controller)
    
    # Movimientos
    print("\n🏃 Ejecutando movimientos...")
    
    print("\n--- Caminar adelante (30 frames) ---")
    await engine.execute_sequence('walk_forward', category='movement', 
                                  params={'duration': 30})
    
    print("\n--- Dash forward ---")
    await engine.execute_sequence('dash_forward', category='movement')
    await asyncio.sleep(0.3)
    
    print("\n--- Backdash ---")
    await engine.execute_sequence('backdash', category='movement')
    await asyncio.sleep(0.3)
    
    print("\n--- Hop forward ---")
    await engine.execute_sequence('hop_forward', category='movement')
    
    await controller.disconnect()
    print("\n✅ Movimientos completados!\n")


async def ejemplo_drill():
    """Ejemplo: drill de entrenamiento con loops"""
    print("\n" + "="*70)
    print("EJEMPLO 4: Training Drill")
    print("="*70)
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    config_file = Path(__file__).parent / 'kof_sequences.json'
    engine = SequenceEngine(config_file, controller)
    
    # Ejecutar drill
    print("\n🎯 Ejecutando drill de neutral game (3 repeticiones)...")
    await engine.execute_drill('neutral_game_loop', loops=3)
    
    await controller.disconnect()
    print("\n✅ Drill completado!\n")


async def ejemplo_secuencias_avanzadas():
    """Ejemplo: secuencias avanzadas del training"""
    print("\n" + "="*70)
    print("EJEMPLO 5: Secuencias Avanzadas")
    print("="*70)
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    config_file = Path(__file__).parent / 'kof_sequences.json'
    engine = SequenceEngine(config_file, controller)
    
    print("\n🔥 Ejecutando secuencias avanzadas...")
    
    print("\n--- Walk Forward > Command Grab ---")
    await engine.execute_sequence('walk_forward_grab', category='advanced_sequences')
    await asyncio.sleep(1)
    
    print("\n--- Hop Forward > Attack ---")
    await engine.execute_sequence('hop_forward_attack', category='advanced_sequences')
    await asyncio.sleep(1)
    
    print("\n--- Hyper Hop Forward > Attack ---")
    await engine.execute_sequence('hyper_hop_forward_attack', category='advanced_sequences')
    
    await controller.disconnect()
    print("\n✅ Secuencias avanzadas completadas!\n")


async def ejemplo_personalizado():
    """Ejemplo: crear y ejecutar secuencia personalizada"""
    print("\n" + "="*70)
    print("EJEMPLO 6: Secuencia Personalizada")
    print("="*70)
    
    controller = SNESControllerBLE()
    await controller.connect()
    
    config_file = Path(__file__).parent / 'kof_sequences.json'
    engine = SequenceEngine(config_file, controller)
    
    print("\n🎨 Ejecutando presión personalizada...")
    
    # Combinar movimientos manualmente
    print("\n1. Hop forward")
    await engine.execute_sequence('hop_forward', category='movement')
    
    print("\n2. cr.B (bajo)")
    await engine.execute_sequence('cr_B', category='basic_attacks')
    
    print("\n3. cr.B (confirmación)")
    await engine.execute_sequence('cr_B', category='basic_attacks')
    
    print("\n4. cl.C (cerca)")
    await engine.execute_sequence('cl_C', category='basic_attacks')
    
    print("\n5. QCF+A (special)")
    await engine.execute_sequence('QCF', category='special_motions')
    
    await controller.disconnect()
    print("\n✅ Presión personalizada completada!\n")


async def main():
    """Menú de ejemplos"""
    print("\n" + "="*70)
    print("KOF Sequence Engine - Ejemplos de Uso")
    print("="*70)
    print("\nSelecciona un ejemplo:")
    print("  1. Ataques básicos")
    print("  2. Combos")
    print("  3. Movimiento")
    print("  4. Training drill (3 loops)")
    print("  5. Secuencias avanzadas")
    print("  6. Secuencia personalizada")
    print("  0. Ejecutar todos los ejemplos")
    
    try:
        choice = input("\nOpción: ").strip()
        
        if choice == '1':
            await ejemplo_basico()
        elif choice == '2':
            await ejemplo_combos()
        elif choice == '3':
            await ejemplo_movimiento()
        elif choice == '4':
            await ejemplo_drill()
        elif choice == '5':
            await ejemplo_secuencias_avanzadas()
        elif choice == '6':
            await ejemplo_personalizado()
        elif choice == '0':
            print("\n🚀 Ejecutando todos los ejemplos...\n")
            await ejemplo_basico()
            await asyncio.sleep(2)
            await ejemplo_combos()
            await asyncio.sleep(2)
            await ejemplo_movimiento()
            await asyncio.sleep(2)
            await ejemplo_secuencias_avanzadas()
            print("\n✅ ¡Todos los ejemplos completados!")
        else:
            print("❌ Opción inválida")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n💡 Estos ejemplos muestran cómo usar el motor de secuencias")
    print("💡 Lee KOF_SEQUENCE_ENGINE.md para documentación completa")
    print("💡 Edita kof_sequences.json para añadir tus propias secuencias\n")
    
    asyncio.run(main())
