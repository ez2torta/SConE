# Mapeo de Botones SNES - Diagrama de Referencia

## 🎮 Controlador SNES (12 botones)

```
        [L]                                    [R]
        
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║    [SELECT]  [START]                          ║
    ║                                               ║
    ║       ┌───┐                    (Y)            ║
    ║       │ ↑ │              (X)        (A)       ║
    ║   ┌───┼───┼───┐                               ║
    ║   │ ← │   │ → │               (B)             ║
    ║   └───┼───┼───┘                               ║
    ║       │ ↓ │                                   ║
    ║       └───┘                                   ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
```

## 📊 Protocolo Serial → SNES

### Entrada: uint32_t (4 bytes, little-endian)

```
  Byte 3      Byte 2      Byte 1      Byte 0
┌─────────┬─────────┬─────────┬─────────┐
│15 ··· 8│ 7 ··· 0│15 ··· 8│ 7 ··· 0│
└─────────┴─────────┴─────────┴─────────┘

Bits utilizados por SNES (12 botones):
─────────────────────────────────────────
bit 0  → B (botón derecho inferior)
bit 1  → Y (botón izquierdo superior)  
bit 2  → X/SELECT (compartido)*
bit 3  → START
bit 4  → (no usado)
bit 5  → (no usado)
bit 6  → L (hombro izquierdo)
bit 7  → R (hombro derecho)
bit 8  → D-Pad UP
bit 9  → D-Pad DOWN
bit 10 → D-Pad LEFT
bit 11 → D-Pad RIGHT
bit 12 → A (botón derecho superior)
bit 13 → (no usado)
bit 14 → (no usado)
bit 15 → (no usado)
```

## 🔄 Orden de Envío SNES (Protocolo)

El SNES lee los botones en este orden específico (12 clocks):

```
Clock  │ Botón    │ Bit interno │ Descripción
───────┼──────────┼─────────────┼────────────────────
  1    │ B        │ 0           │ Botón B (inferior derecha)
  2    │ Y        │ 1           │ Botón Y (superior izquierda)
  3    │ SELECT   │ 2           │ Botón Select
  4    │ START    │ 3           │ Botón Start
  5    │ UP       │ 4           │ D-Pad arriba
  6    │ DOWN     │ 5           │ D-Pad abajo
  7    │ LEFT     │ 6           │ D-Pad izquierda
  8    │ RIGHT    │ 7           │ D-Pad derecha
  9    │ A        │ 8           │ Botón A (superior derecha)
 10    │ X        │ 9           │ Botón X (superior centro)
 11    │ L        │ 10          │ Hombro izquierdo
 12    │ R        │ 11          │ Hombro derecho
 13-16 │ (unused) │ -           │ No usados (siempre HIGH)
```

## 📝 Ejemplos de Comandos

### Formato: `0xAABBCCDD` (hexadecimal)

| Combinación | Valor uint32_t | Bytes (LE) | Descripción |
|-------------|---------------|------------|-------------|
| Nada | `0x00000000` | `00 00 00 00` | Sin botones |
| B solo | `0x00000001` | `01 00 00 00` | Botón B |
| Y solo | `0x00000002` | `02 00 00 00` | Botón Y |
| A solo | `0x00001000` | `00 10 00 00` | Botón A |
| X solo | `0x00000004` | `04 00 00 00` | Botón X |
| SELECT | `0x00000004` | `04 00 00 00` | Select |
| START | `0x00000008` | `08 00 00 00` | Start |
| L | `0x00000040` | `40 00 00 00` | Hombro L |
| R | `0x00000080` | `80 00 00 00` | Hombro R |
| UP | `0x00000100` | `00 01 00 00` | Arriba |
| DOWN | `0x00000200` | `00 02 00 00` | Abajo |
| LEFT | `0x00000400` | `00 04 00 00` | Izquierda |
| RIGHT | `0x00000800` | `00 08 00 00` | Derecha |
| A + B | `0x00001001` | `01 10 00 00` | A y B juntos |
| START + SELECT | `0x0000000C` | `0C 00 00 00` | Start y Select |
| UP + A | `0x00001100` | `00 11 00 00` | Arriba + A (salto) |
| L + R | `0x000000C0` | `C0 00 00 00` | Ambos hombros |

### Calculadora de Bits

Para crear tu propio comando:

```python
# Ejemplo: Presionar A + B + UP
comando = 0
comando |= (1 << 0)   # B       → bit 0
comando |= (1 << 12)  # A       → bit 12
comando |= (1 << 8)   # UP      → bit 8

# Resultado: 0x00001101 = 0x1101
# Bytes: 01 11 00 00
```

```cpp
// Ejemplo en C++
uint32_t comando = 0;
comando |= (1 << 0);   // B
comando |= (1 << 12);  // A
comando |= (1 << 8);   // UP
// comando = 0x00001101
```

## 🔌 Conexión Física

```
ESP32                          SNES Console
─────                          ────────────
GPIO 25 ────────────────────→ LATCH (pin 3)
GPIO 26 ────────────────────→ CLOCK (pin 2)  
GPIO 27 ────────────────────→ DATA  (pin 4)
GND     ────────────────────→ GND   (pin 1)
                               +5V   (pin 5) [no conectar]
```

### Conector SNES (vista frontal del puerto de la consola)

```
  ╭─────────────╮
  │ ⚫ ⚫ │ ⚫ ⚫ │
  │  1  2 │ 3  4 │
  │      ═╪═     │
  │       5      │
  ╰──────────────╯

Pin 1: GND
Pin 2: CLOCK
Pin 3: LATCH
Pin 4: DATA
Pin 5: +5V (no usar, puede dañar el ESP32)
```

## ⚠️ Notas Importantes

1. **Voltaje:** El ESP32 es de 3.3V, pero el SNES acepta señales de 3.3V en los pines de datos
2. **Level Shifter:** Opcional pero recomendado para mayor compatibilidad
3. **Lógica:** LOW = presionado, HIGH = no presionado
4. **Little-Endian:** El byte menos significativo va primero
5. **Timing:** El ESP32 es lo suficientemente rápido para el protocolo SNES

## 🧪 Probar con Monitor Serie

1. Abre el Monitor Serie en Arduino IDE (115200 baud)
2. Escribe comandos en hexadecimal y envía
3. El ESP32 mostrará qué botones detecta

## 📚 Referencias

- Especificación completa: `README_ESP32.md`
- Script de prueba Python: `test_snes_serial.py`
- Código fuente: `snes_esp32.ino`
