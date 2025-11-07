#!/usr/bin/env python3
"""
KOF Sequence Engine - Motor de ejecución de secuencias frame-perfect
Interpreta archivos JSON con definiciones de movimientos y los ejecuta
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Importar las clases de control del SNES
sys.path.insert(0, os.path.dirname(__file__))
from test_ble_input import SNESControllerBLE, SNESControllerSerial, BUTTONS


class SequenceEngine:
    """Motor que ejecuta secuencias de movimientos desde JSON"""
    
    def __init__(self, config_file: str, controller: Union[SNESControllerBLE, SNESControllerSerial]):
        """
        Inicializar el motor de secuencias
        
        Args:
            config_file: Ruta al archivo JSON de configuración
            controller: Instancia del controlador (BLE o Serial)
        """
        self.config_file = Path(config_file)
        self.controller = controller
        self.config: Dict[str, Any] = {}
        self.button_map: Dict[str, int] = {}
        self.fps: int = 60
        self.frame_duration: float = 1.0 / 60.0
        
        self._load_config()
        self._build_button_map()
    
    def _load_config(self):
        """Cargar configuración desde JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.fps = self.config.get('metadata', {}).get('fps', 60)
            self.frame_duration = 1.0 / self.fps
            
            print(f"✅ Configuración cargada: {self.config['metadata']['game']}")
            print(f"   FPS: {self.fps}, Frame duration: {self.frame_duration:.4f}s")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ No se encontró el archivo: {self.config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Error al parsear JSON: {e}")
    
    def _build_button_map(self):
        """Construir mapeo de nombres de botones a valores"""
        mapping = self.config.get('button_mapping', {})
        
        # Mapear direcciones numéricas
        direction_map = {
            '5': 0,  # Neutral
            '6': BUTTONS['RIGHT'],
            '4': BUTTONS['LEFT'],
            '2': BUTTONS['DOWN'],
            '8': BUTTONS['UP'],
            '7': BUTTONS['UP'] | BUTTONS['LEFT'],    # UP-LEFT
            '9': BUTTONS['UP'] | BUTTONS['RIGHT'],   # UP-RIGHT
            '1': BUTTONS['DOWN'] | BUTTONS['LEFT'],  # DOWN-LEFT
            '3': BUTTONS['DOWN'] | BUTTONS['RIGHT'], # DOWN-RIGHT
        }
        
        # Mapear botones
        button_map_basic = {
            'A': BUTTONS['A'],
            'B': BUTTONS['B'],
            'C': BUTTONS['C'],  # Usamos X como C
            'D': BUTTONS['D'],  # Usamos Y como D
            'AB': BUTTONS['A'] | BUTTONS['B'],
            'CD': BUTTONS['X'] | BUTTONS['Y'],
            'SELECT': BUTTONS['SELECT'],
            'START': BUTTONS['START'],
        }
        
        self.button_map = {**direction_map, **button_map_basic}
        
        print(f"✅ Mapeados {len(self.button_map)} inputs")
    
    def _parse_input(self, input_str: str) -> int:
        """
        Parsear string de input a valor de botones
        
        Args:
            input_str: String tipo "5", "2+B", "6+C", etc.
        
        Returns:
            Valor combinado de botones
        """
        parts = input_str.split('+')
        result = 0
        
        for part in parts:
            part = part.strip()
            if part in self.button_map:
                result |= self.button_map[part]
            elif '{button}' in part:
                # Placeholder - será reemplazado después
                continue
            else:
                print(f"⚠️  Input desconocido: {part}")
        
        return result
    
    async def _execute_frame(self, frame: Dict[str, Any], context: Dict[str, Any] = None):
        """
        Ejecutar un frame individual
        
        Args:
            frame: Diccionario con 'input' y 'hold'
            context: Contexto de ejecución (para reemplazo de parámetros)
        """
        input_str = frame['input']
        hold_frames = frame.get('hold', 1)
        comment = frame.get('comment', '')
        
        # Resolver parámetros dinámicos
        if context:
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                input_str = input_str.replace(placeholder, str(value))
                if isinstance(hold_frames, str):
                    hold_frames = hold_frames.replace(placeholder, str(value))
        
        # Convertir hold a int si es string
        if isinstance(hold_frames, str):
            try:
                hold_frames = int(hold_frames)
            except ValueError:
                print(f"⚠️  No se pudo convertir hold '{hold_frames}' a int, usando 1")
                hold_frames = 1
        
        # Parsear input
        button_value = self._parse_input(input_str)
        
        # Calcular duración
        duration = hold_frames * self.frame_duration
        
        # Debug info
        if comment:
            print(f"   [{hold_frames}f] {input_str}: {comment}")
        else:
            print(f"   [{hold_frames}f] {input_str}")
        
        # Enviar comando
        if isinstance(self.controller, SNESControllerBLE):
            await self.controller.send_buttons_async(button_value)
            await asyncio.sleep(duration)
        else:
            self.controller.send_buttons(button_value)
            import time
            time.sleep(duration)
    
    def _resolve_reference(self, ref: str) -> Dict[str, Any]:
        """
        Resolver una referencia tipo 'basic_attacks.cr_B'
        
        Args:
            ref: String de referencia
        
        Returns:
            Diccionario de la secuencia referenciada
        """
        parts = ref.split('.')
        current = self.config
        
        for part in parts:
            if part in current:
                current = current[part]
            else:
                raise ValueError(f"❌ Referencia no encontrada: {ref}")
        
        return current
    
    async def execute_sequence(self, sequence_name: str, category: str = None, 
                              params: Dict[str, Any] = None, verbose: bool = True):
        """
        Ejecutar una secuencia por nombre
        
        Args:
            sequence_name: Nombre de la secuencia (ej: 'cr_B', 'QCF', 'walk_forward_grab')
            category: Categoría opcional (ej: 'basic_attacks', 'combos')
            params: Parámetros opcionales para la secuencia
            verbose: Mostrar información detallada
        """
        # Buscar la secuencia en las categorías
        sequence_data = None
        found_category = category
        
        if category:
            # Buscar en categoría específica
            if category in self.config and sequence_name in self.config[category]:
                sequence_data = self.config[category][sequence_name]
        else:
            # Buscar en todas las categorías
            for cat in self.config:
                if isinstance(self.config[cat], dict) and sequence_name in self.config[cat]:
                    sequence_data = self.config[cat][sequence_name]
                    found_category = cat
                    break
        
        if not sequence_data:
            raise ValueError(f"❌ Secuencia no encontrada: {sequence_name}")
        
        if verbose:
            name = sequence_data.get('name', sequence_name)
            difficulty = '⭐' * sequence_data.get('difficulty', 1)
            print(f"\n🎮 Ejecutando: {name} [{found_category}] {difficulty}")
            if 'description' in sequence_data:
                print(f"   {sequence_data['description']}")
        
        # Preparar contexto de parámetros
        context = {}
        if params:
            context.update(params)
        
        # Aplicar parámetros por defecto
        if 'parameters' in sequence_data:
            for param_name, param_info in sequence_data['parameters'].items():
                if param_name not in context:
                    context[param_name] = param_info.get('default')
        
        # Ejecutar frames o secuencia de referencias
        if 'frames' in sequence_data:
            # Ejecución directa de frames
            for frame in sequence_data['frames']:
                await self._execute_frame(frame, context)
        
        elif 'sequence' in sequence_data:
            # Ejecución de secuencia de referencias
            for step in sequence_data['sequence']:
                if 'ref' in step:
                    # Referencia a otra secuencia
                    ref_data = self._resolve_reference(step['ref'])
                    
                    # Construir contexto para la referencia
                    ref_context = dict(context)
                    if 'params' in step:
                        ref_context.update(step['params'])
                    if 'button' in step:
                        ref_context['button'] = step['button']
                    
                    # Ejecutar frames de la referencia
                    if 'frames' in ref_data:
                        for frame in ref_data['frames']:
                            await self._execute_frame(frame, ref_context)
                
                elif 'input' in step:
                    # Frame directo
                    await self._execute_frame(step, context)
                
                elif 'wait' in step:
                    # Espera
                    wait_frames = step['wait']
                    wait_duration = wait_frames * self.frame_duration
                    comment = step.get('comment', '')
                    if verbose:
                        print(f"   ⏸️  Esperar {wait_frames}f{' - ' + comment if comment else ''}")
                    await asyncio.sleep(wait_duration)
        
        if verbose:
            total = sequence_data.get('total_frames', '?')
            print(f"✅ Completado ({total} frames)\n")
    
    async def execute_combo(self, combo_name: str, verbose: bool = True):
        """Ejecutar un combo por nombre"""
        await self.execute_sequence(combo_name, category='combos', verbose=verbose)
    
    async def execute_drill(self, drill_name: str, loops: int = 1, verbose: bool = True):
        """
        Ejecutar un drill de entrenamiento
        
        Args:
            drill_name: Nombre del drill
            loops: Número de veces a repetir (-1 para infinito)
            verbose: Mostrar información
        """
        drill_data = self.config.get('training_drills', {}).get(drill_name)
        if not drill_data:
            raise ValueError(f"❌ Drill no encontrado: {drill_name}")
        
        if verbose:
            print(f"\n🎯 Iniciando drill: {drill_data['name']}")
            print(f"   {drill_data['description']}")
            if loops == -1:
                print(f"   ♾️  Modo loop infinito (Ctrl+C para detener)")
            else:
                print(f"   🔄 {loops} repeticiones\n")
        
        loop_count = 0
        try:
            while loops == -1 or loop_count < loops:
                if loops != 1:
                    print(f"--- Loop {loop_count + 1}/{loops if loops != -1 else '∞'} ---")
                
                await self.execute_sequence(drill_name, category='training_drills', verbose=verbose)
                
                loop_count += 1
                
                if loops == -1 and verbose:
                    print(f"⏳ Esperando antes del siguiente loop...")
                    await asyncio.sleep(1.0)
        
        except KeyboardInterrupt:
            if verbose:
                print(f"\n⚠️  Drill interrumpido después de {loop_count} loops")
    
    def list_sequences(self, category: str = None, filter_difficulty: int = None):
        """
        Listar secuencias disponibles
        
        Args:
            category: Filtrar por categoría
            filter_difficulty: Filtrar por dificultad máxima
        """
        print("\n📋 Secuencias Disponibles:\n")
        
        categories = [category] if category else [
            'basic_attacks', 'special_motions', 'movement', 
            'aerial_attacks', 'combos', 'advanced_sequences', 'training_drills'
        ]
        
        for cat in categories:
            if cat not in self.config:
                continue
            
            cat_data = self.config[cat]
            if not isinstance(cat_data, dict):
                continue
            
            # Filtrar por dificultad
            filtered = {}
            for name, data in cat_data.items():
                if isinstance(data, dict):
                    difficulty = data.get('difficulty', 1)
                    if filter_difficulty is None or difficulty <= filter_difficulty:
                        filtered[name] = data
            
            if not filtered:
                continue
            
            print(f"  [{cat.upper()}]")
            for name, data in filtered.items():
                difficulty = '⭐' * data.get('difficulty', 1)
                desc = data.get('name', name)
                frames = data.get('total_frames', '?')
                print(f"    • {name:25} - {desc:35} {difficulty:10} ({frames}f)")
            print()


async def main():
    """Función principal de demostración"""
    print("\n" + "="*70)
    print("KOF XV Sequence Engine - Motor de Ejecución Frame-Perfect")
    print("="*70)
    
    # Cargar configuración
    config_file = Path(__file__).parent / 'kof_sequences.json'
    
    # Conectar controlador BLE
    print("\n🔌 Conectando al controlador BLE...")
    controller = SNESControllerBLE()
    
    try:
        await controller.connect()
    except Exception as e:
        print(f"❌ Error al conectar BLE: {e}")
        print("\n💡 Asegúrate de que el ESP32 esté encendido y en rango")
        return
    
    # Crear motor
    engine = SequenceEngine(config_file, controller)
    
    # Menú interactivo
    while True:
        print("\n" + "="*70)
        print("MENÚ PRINCIPAL")
        print("="*70)
        print("  1. Listar todas las secuencias")
        print("  2. Ejecutar ataque básico")
        print("  3. Ejecutar movimiento especial")
        print("  4. Ejecutar combo")
        print("  5. Ejecutar secuencia avanzada")
        print("  6. Ejecutar drill de entrenamiento")
        print("  7. Demo: Combos básicos")
        print("  8. Demo: Neutral game")
        print("  0. Salir")
        
        try:
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == '0':
                print("\n👋 Saliendo...")
                break
            
            elif choice == '1':
                difficulty = input("Filtrar por dificultad máxima (1-5, Enter para todas): ").strip()
                filter_diff = int(difficulty) if difficulty else None
                engine.list_sequences(filter_difficulty=filter_diff)
            
            elif choice == '2':
                print("\nAtaques básicos disponibles:")
                engine.list_sequences(category='basic_attacks')
                attack = input("Nombre del ataque (ej: cr_B, st_A): ").strip()
                await engine.execute_sequence(attack, category='basic_attacks')
            
            elif choice == '3':
                print("\nMovimientos disponibles:")
                engine.list_sequences(category='movement')
                move = input("Nombre del movimiento: ").strip()
                await engine.execute_sequence(move, category='movement')
            
            elif choice == '4':
                print("\nCombos disponibles:")
                engine.list_sequences(category='combos')
                combo = input("Nombre del combo: ").strip()
                await engine.execute_combo(combo)
            
            elif choice == '5':
                print("\nSecuencias avanzadas:")
                engine.list_sequences(category='advanced_sequences')
                seq = input("Nombre de la secuencia: ").strip()
                await engine.execute_sequence(seq, category='advanced_sequences')
            
            elif choice == '6':
                print("\nDrills de entrenamiento:")
                engine.list_sequences(category='training_drills')
                drill = input("Nombre del drill: ").strip()
                loops = input("Número de repeticiones (-1 para infinito): ").strip()
                loops = int(loops) if loops else 1
                await engine.execute_drill(drill, loops=loops)
            
            elif choice == '7':
                print("\n🎮 Ejecutando demo de combos básicos...")
                await engine.execute_combo('cr_B_cr_A_QCF_A')
                await asyncio.sleep(1)
                await engine.execute_combo('cl_C_QCF_C')
                await asyncio.sleep(1)
                await engine.execute_combo('j_D_cl_C_DP_A')
            
            elif choice == '8':
                print("\n🎮 Ejecutando demo de neutral game...")
                await engine.execute_drill('neutral_game_loop', loops=3)
            
            else:
                print("❌ Opción inválida")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Operación cancelada")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Desconectar
    print("\n🔌 Desconectando controlador...")
    await controller.disconnect()
    print("✅ Desconectado\n")


if __name__ == "__main__":
    print("\n💡 Sistema de ejecución basado en configuración JSON")
    print("💡 Edita 'kof_sequences.json' para añadir nuevas secuencias")
    print("💡 Usa referencias para reutilizar movimientos\n")
    
    asyncio.run(main())
