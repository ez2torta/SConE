#!/usr/bin/env python3
"""
KOF Sequence Validator & Generator
Valida el archivo JSON y genera nuevas secuencias desde markdown
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


class SequenceValidator:
    """Validador de secuencias JSON"""
    
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load(self) -> bool:
        """Cargar y validar configuración"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except FileNotFoundError:
            self.errors.append(f"Archivo no encontrado: {self.config_file}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Error JSON: {e}")
            return False
    
    def validate_metadata(self) -> bool:
        """Validar sección metadata"""
        if 'metadata' not in self.config:
            self.errors.append("Falta sección 'metadata'")
            return False
        
        meta = self.config['metadata']
        required = ['game', 'fps', 'version']
        
        for field in required:
            if field not in meta:
                self.errors.append(f"Falta campo metadata.{field}")
        
        if 'fps' in meta and not isinstance(meta['fps'], int):
            self.errors.append("metadata.fps debe ser entero")
        
        return len(self.errors) == 0
    
    def validate_sequence(self, name: str, data: Dict[str, Any], category: str) -> bool:
        """Validar una secuencia individual"""
        valid = True
        
        # Validar campos requeridos
        if 'frames' not in data and 'sequence' not in data:
            self.errors.append(f"{category}.{name}: Debe tener 'frames' o 'sequence'")
            valid = False
        
        # Validar frames
        if 'frames' in data:
            if not isinstance(data['frames'], list):
                self.errors.append(f"{category}.{name}: 'frames' debe ser lista")
                valid = False
            else:
                for i, frame in enumerate(data['frames']):
                    if 'input' not in frame:
                        self.errors.append(f"{category}.{name}.frames[{i}]: Falta 'input'")
                        valid = False
                    if 'hold' not in frame:
                        self.warnings.append(f"{category}.{name}.frames[{i}]: Falta 'hold', asumiendo 1")
        
        # Validar sequence (referencias)
        if 'sequence' in data:
            if not isinstance(data['sequence'], list):
                self.errors.append(f"{category}.{name}: 'sequence' debe ser lista")
                valid = False
            else:
                for i, step in enumerate(data['sequence']):
                    if 'ref' not in step and 'input' not in step and 'wait' not in step:
                        self.errors.append(
                            f"{category}.{name}.sequence[{i}]: Debe tener 'ref', 'input' o 'wait'"
                        )
                        valid = False
        
        # Validar total_frames si existe
        if 'total_frames' in data:
            if not isinstance(data['total_frames'], int):
                self.errors.append(f"{category}.{name}: 'total_frames' debe ser entero")
                valid = False
        
        # Validar difficulty
        if 'difficulty' in data:
            diff = data['difficulty']
            if not isinstance(diff, int) or diff < 1 or diff > 5:
                self.errors.append(f"{category}.{name}: 'difficulty' debe ser 1-5")
                valid = False
        
        return valid
    
    def validate_all(self) -> bool:
        """Validar todas las secuencias"""
        if not self.validate_metadata():
            return False
        
        categories = [
            'basic_attacks', 'special_motions', 'movement',
            'aerial_attacks', 'combos', 'advanced_sequences', 'training_drills'
        ]
        
        for category in categories:
            if category not in self.config:
                self.warnings.append(f"Categoría '{category}' no encontrada")
                continue
            
            cat_data = self.config[category]
            if not isinstance(cat_data, dict):
                self.errors.append(f"'{category}' debe ser diccionario")
                continue
            
            for name, data in cat_data.items():
                self.validate_sequence(name, data, category)
        
        return len(self.errors) == 0
    
    def print_report(self):
        """Imprimir reporte de validación"""
        print("\n" + "="*70)
        print("REPORTE DE VALIDACIÓN")
        print("="*70)
        
        if self.errors:
            print(f"\n❌ Errores ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  Advertencias ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ Validación exitosa - sin errores ni advertencias")
        elif not self.errors:
            print("\n✅ Validación exitosa - solo advertencias")
        else:
            print(f"\n❌ Validación fallida - {len(self.errors)} errores")
        
        print()
    
    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas del archivo"""
        stats = {
            'total_sequences': 0,
            'basic_attacks': 0,
            'special_motions': 0,
            'movement': 0,
            'aerial_attacks': 0,
            'combos': 0,
            'advanced_sequences': 0,
            'training_drills': 0,
        }
        
        for category in stats.keys():
            if category == 'total_sequences':
                continue
            if category in self.config:
                count = len(self.config[category])
                stats[category] = count
                stats['total_sequences'] += count
        
        return stats
    
    def print_stats(self):
        """Imprimir estadísticas"""
        stats = self.get_stats()
        
        print("\n📊 Estadísticas:")
        print(f"   Total secuencias: {stats['total_sequences']}")
        print(f"   • Ataques básicos: {stats['basic_attacks']}")
        print(f"   • Movimientos especiales: {stats['special_motions']}")
        print(f"   • Movimiento: {stats['movement']}")
        print(f"   • Ataques aéreos: {stats['aerial_attacks']}")
        print(f"   • Combos: {stats['combos']}")
        print(f"   • Secuencias avanzadas: {stats['advanced_sequences']}")
        print(f"   • Drills de entrenamiento: {stats['training_drills']}")
        print()


class SequenceGenerator:
    """Generador de secuencias desde notación compacta"""
    
    @staticmethod
    def parse_compact_notation(notation: str) -> List[Dict[str, Any]]:
        """
        Parsear notación compacta a frames
        
        Ejemplo: "[5×3][5+A][5×5]" -> 
        [
            {"input": "5", "hold": 3},
            {"input": "5+A", "hold": 1},
            {"input": "5", "hold": 5}
        ]
        """
        import re
        frames = []
        
        # Pattern: [input×frames] o [input]
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, notation)
        
        for match in matches:
            if '×' in match:
                input_part, hold_part = match.split('×')
                frames.append({
                    "input": input_part.strip(),
                    "hold": int(hold_part.strip())
                })
            else:
                frames.append({
                    "input": match.strip(),
                    "hold": 1
                })
        
        return frames
    
    @staticmethod
    def generate_from_markdown_line(line: str) -> Dict[str, Any]:
        """
        Generar secuencia desde una línea de markdown
        
        Ejemplo:
        **Secuencia compacta**: `[5×3][5+A][5×5]`
        """
        import re
        
        # Buscar patrón de secuencia compacta
        pattern = r'\*\*Secuencia compacta\*\*:\s*`(.+)`'
        match = re.search(pattern, line)
        
        if match:
            notation = match.group(1)
            frames = SequenceGenerator.parse_compact_notation(notation)
            
            # Calcular total de frames
            total = sum(f['hold'] for f in frames)
            
            return {
                "frames": frames,
                "total_frames": total
            }
        
        return None
    
    @staticmethod
    def create_sequence_template(name: str, category: str, difficulty: int = 1) -> Dict[str, Any]:
        """Crear plantilla de secuencia"""
        return {
            "name": name,
            "category": category,
            "difficulty": difficulty,
            "frames": [
                {"input": "5", "hold": 3, "comment": "preparación"},
                {"input": "5+A", "hold": 1, "comment": "ejecutar"},
                {"input": "5", "hold": 5, "comment": "recovery"}
            ],
            "total_frames": 9,
            "properties": []
        }


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("KOF Sequence Validator & Generator")
    print("="*70)
    
    config_file = Path(__file__).parent / 'kof_sequences.json'
    
    # Menú
    print("\n1. Validar archivo JSON")
    print("2. Mostrar estadísticas")
    print("3. Generar plantilla de secuencia")
    print("4. Parsear notación compacta")
    
    choice = input("\nSelecciona una opción: ").strip()
    
    if choice == '1':
        validator = SequenceValidator(config_file)
        if validator.load():
            validator.validate_all()
            validator.print_report()
            validator.print_stats()
    
    elif choice == '2':
        validator = SequenceValidator(config_file)
        if validator.load():
            validator.print_stats()
    
    elif choice == '3':
        name = input("Nombre de la secuencia: ").strip()
        category = input("Categoría (basic_attacks, combos, etc.): ").strip()
        difficulty = input("Dificultad (1-5): ").strip()
        
        template = SequenceGenerator.create_sequence_template(
            name, category, int(difficulty) if difficulty else 1
        )
        
        print("\n📝 Plantilla generada:")
        print(json.dumps({name: template}, indent=2))
    
    elif choice == '4':
        notation = input("Notación compacta (ej: [5×3][5+A][5×5]): ").strip()
        frames = SequenceGenerator.parse_compact_notation(notation)
        
        print("\n📝 Frames generados:")
        print(json.dumps(frames, indent=2))
        
        total = sum(f['hold'] for f in frames)
        print(f"\nTotal frames: {total}")
    
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    main()
