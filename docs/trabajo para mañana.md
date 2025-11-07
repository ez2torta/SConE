# 🎮 KOF XV - Sistema de Aprendizaje por Visión y Reacción

## 📋 Objetivo Principal

Implementar un sistema que aprenda automáticamente grabando clips de video de 1 segundo alrededor de cada input (antes, durante y después) para:

1. **Detectar visualmente** lo que sucede en pantalla
2. **Medir latencia de reacción** - tiempo entre estímulo visual y respuesta
3. **Ajustar dinámicamente** el timing de reacción (parámetro configurable)
4. **Entrenar progresivamente** comenzando con movimientos básicos

---

## 🎯 Fase Inicial: Movimientos Básicos

### Prioridad Fase 1
- ✅ Light Punch (A)
- ✅ Light Kick (B)
- ✅ Strong Punch (C)
- ✅ Strong Kick (D)
- ✅ Crouch Light Kick (cr.B)

---

## 🕹️ Sistema de Notación KOF

### Direcciones (Numpad Notation)
```
 7  8  9     ↖  ↑  ↗
 4  5  6  =  ←  N  →
 1  2  3     ↙  ↓  ↘
```

| Número | Dirección | Alias |
|--------|-----------|-------|
| 5 | Neutral | N, neutral |
| 6 | Forward | f, → |
| 4 | Back | b, ← |
| 2 | Down | d, ↓ |
| 8 | Up | u, ↑ |
| 7 | Up-Back | ub, ↖ |
| 9 | Up-Forward | uf, ↗ |
| 1 | Down-Back | db, ↙ |
| 3 | Down-Forward | df, ↘ |

### Botones
| Botón | Función | Alias |
|-------|---------|-------|
| A | Light Punch | LP |
| B | Light Kick | LK |
| C | Strong Punch | HP, SP |
| D | Strong Kick | HK, SK |
| AB | Evasive Roll | Roll |
| CD | Blowback Attack | Blowback |

### Prefijos de Posición
| Prefijo | Significado | Ejemplo |
|---------|-------------|---------|
| `st.` | Standing (lejos) | `st.A` |
| `cl.` | Close standing | `cl.C` |
| `cr.` | Crouching | `cr.B` |
| `j.` | Jumping | `j.D` |
| `Far` | Standing far | `Far D` |

---

## ⚡ Movimientos Básicos (60 FPS)

### 1. Ataques Normales de Pie

#### Light Punch (st.A)
```
Frame 1-3:   5 (neutral, preparación)
Frame 4:     5+A (presionar A)
Frame 5-8:   5 (mantener neutral, animación)
Frame 9+:    5 (recovery)
```
**Secuencia compacta**: `[5×3][5+A][5×5]`

#### Light Kick (st.B)
```
Frame 1-3:   5 (neutral)
Frame 4:     5+B (presionar B)
Frame 5-9:   5 (animación)
Frame 10+:   5 (recovery)
```
**Secuencia compacta**: `[5×3][5+B][5×6]`

#### Strong Punch (st.C)
```
Frame 1-4:   5 (neutral)
Frame 5:     5+C (presionar C)
Frame 6-12:  5 (animación)
Frame 13+:   5 (recovery)
```
**Secuencia compacta**: `[5×4][5+C][5×8]`

#### Strong Kick (st.D)
```
Frame 1-4:   5 (neutral)
Frame 5:     5+D (presionar D)
Frame 6-14:  5 (animación)
Frame 15+:   5 (recovery)
```
**Secuencia compacta**: `[5×4][5+D][5×10]`

---

### 2. Ataques Agachados (Crouching)

#### Crouch Light Kick (cr.B) - **¡IMPORTANTE!**
```
Frame 1-2:   2 (mantener down)
Frame 3:     2+B (down + B)
Frame 4-7:   2 (mantener down durante hit)
Frame 8+:    5 (soltar, recovery)
```
**Secuencia compacta**: `[2×2][2+B][2×4][5×2]`

**⚠️ Nota**: Este es el poke más importante en KOF - rápido, cancela y pega bajo.

#### Crouch Light Punch (cr.A)
```
Frame 1-2:   2 (mantener down)
Frame 3:     2+A (down + A)
Frame 4-6:   2 (mantener down)
Frame 7+:    5 (recovery)
```
**Secuencia compacta**: `[2×2][2+A][2×4][5×2]`

#### Crouch Strong Punch (cr.C)
```
Frame 1-3:   2 (mantener down)
Frame 4:     2+C (down + C)
Frame 5-11:  2 (mantener down, animación)
Frame 12+:   5 (recovery)
```
**Secuencia compacta**: `[2×3][2+C][2×8][5×2]`

#### Crouch Strong Kick (cr.D) - **SWEEP**
```
Frame 1-4:   2 (mantener down)
Frame 5:     2+D (down + D)
Frame 6-16:  2 (mantener down, animación sweep)
Frame 17+:   5 (recovery)
```
**Secuencia compacta**: `[2×4][2+D][2×12][5×3]`

**⚠️ Nota**: Sweep - derriba, unsafe si bloqueado.

---

### 3. Ataques Aéreos (Jumping)

#### Jump Light Punch (j.A)
```
Frame 1-3:   5 (neutral)
Frame 4-6:   8 (press up, prejump)
Frame 7-25:  8 (airborne, subiendo)
Frame 26:    8+A (presionar A en el aire)
Frame 27-30: 8 (animación hit)
Frame 31-45: 8 (cayendo)
Frame 46+:   5 (aterrizar)
```
**Secuencia compacta**: `[5×3][8×3][8×18][8+A][8×4][8×15][5×3]`

#### Jump Strong Kick (j.D) - **JUMP-IN**
```
Frame 1-3:   5
Frame 4-6:   8 (prejump)
Frame 7-28:  8 (subiendo)
Frame 29:    8+D (press D en el aire)
Frame 30-35: 8 (animación)
Frame 36-45: 8 (cayendo)
Frame 46+:   5 (aterrizar)
```
**Secuencia compacta**: `[5×3][8×3][8×21][8+D][8×6][8×10][5×3]`

---

### 4. Ataques Cercanos (Close)

#### Close Strong Punch (cl.C) - **¡CANCELABLE!**
```
Frame 1-2:   5 (neutral, muy cerca del oponente)
Frame 3:     5+C (presionar C)
Frame 4-8:   5 (animación, active frames)
Frame 9+:    5 (recovery - puede cancelar en special)
```
**Secuencia compacta**: `[5×2][5+C][5×6]`

**⚠️ Nota**: Este es el confirm principal - rápido y cancela en specials/supers.

---

### 5. Movimiento

#### Walk Forward (Caminar Adelante)
```
Frame 1+:    6 (mantener forward continuamente)
```
**Secuencia compacta**: `[6×N]` donde N = frames que quieres caminar

#### Walk Backward (Caminar Atrás)
```
Frame 1+:    4 (mantener back continuamente)
```
**Secuencia compacta**: `[4×N]`

#### Dash Forward (ff / 66)
```
Frame 1-3:   5 (neutral)
Frame 4:     6 (tap forward)
Frame 5:     5 (release)
Frame 6:     6 (tap forward again, rápido!)
Frame 7-20:  6 (dash animation)
Frame 21+:   5 (recovery)
```
**Secuencia compacta**: `[5×3][6][5][6][6×14][5×3]`

**Timing crítico**: El segundo 6 debe estar en ~2-3 frames del primero.

#### Backdash (bb / 44)
```
Frame 1-3:   5
Frame 4:     4 (tap back)
Frame 5:     5 (release)
Frame 6:     4 (tap back again)
Frame 7-25:  4 (backdash - invulnerable frames 7-15)
Frame 26+:   5 (recovery)
```
**Secuencia compacta**: `[5×3][4][5][4][4×19][5×3]`

**⚠️ Nota**: Frames 7-15 tienen invencibilidad!

---

### 6. Saltos y Hops

#### Normal Jump (8)
```
Frame 1-3:   5
Frame 4-6:   8 (press and HOLD up, prejump)
Frame 7-40:  8 (airborne)
Frame 41+:   5 (landing)
```
**Secuencia compacta**: `[5×3][8×3][8×34][5×5]`

#### Hop (rápido tap 8)
```
Frame 1-2:   5
Frame 3:     8 (TAP up - no mantener!)
Frame 4:     5 (release immediately)
Frame 5-25:  8 (airborne - más bajo y rápido que jump)
Frame 26+:   5 (landing)
```
**Secuencia compacta**: `[5×2][8][5][8×21][5×3]`

**⚠️ Nota**: Hop es crítico para pressure - más rápido y bajo que jump normal.

#### Hyper Jump (28 o 2~8)
```
Frame 1-2:   5
Frame 3-4:   2 (press down)
Frame 5:     8 (quickly press up)
Frame 6-8:   8 (prejump - más rápido)
Frame 9-38:  8 (airborne - más alto y rápido)
Frame 39+:   5 (landing)
```
**Secuencia compacta**: `[5×2][2×2][8×3][8×30][5×3]`

---

### 7. Comandos Especiales

#### Blowback Attack (CD)
```
Frame 1-4:   5
Frame 5:     5+CD (press C+D simultáneamente)
Frame 6-15:  5 (animación - golpe launcher)
Frame 16+:   5 (recovery)
```
**Secuencia compacta**: `[5×4][5+CD][5×10]`

**⚠️ Nota**: Launcher - si pega en counter hit, permite juggle.

#### Evasive Roll Forward (AB)
```
Frame 1-3:   5
Frame 4:     5+AB (press A+B)
Frame 5-24:  6 (rolling forward - invencible frames 5-18)
Frame 25+:   5 (recovery - vulnerable!)
```
**Secuencia compacta**: `[5×3][5+AB][6×20][5×5]`

#### Evasive Roll Backward (4+AB)
```
Frame 1-3:   5
Frame 4:     4+AB (back + A+B)
Frame 5-24:  4 (rolling backward - invencible frames 5-18)
Frame 25+:   5 (recovery)
```
**Secuencia compacta**: `[5×3][4+AB][4×20][5×5]`

**⚠️ Nota**: Frames 5-18 invencibles, 25+ vulnerable - cuidado!

---

## 🔥 Motions de Especiales (Special Moves)

### Quarter Circle Forward (QCF / 236)
```
Frame 1-3:   5 (neutral)
Frame 4:     2 (down)
Frame 5:     3 (down-forward)
Frame 6:     6+P/K (forward + botón)
Frame 7+:    Depende del special
```
**Secuencia compacta**: `[5×3][2][3][6+P/K]`

**Ejemplo - Fireball**: `[5×3][2][3][6+A]`

### Quarter Circle Back (QCB / 214)
```
Frame 1-3:   5
Frame 4:     2 (down)
Frame 5:     1 (down-back)
Frame 6:     4+P/K (back + botón)
```
**Secuencia compacta**: `[5×3][2][1][4+P/K]`

### Dragon Punch (DP / 623)
```
Frame 1-3:   5
Frame 4:     6 (forward)
Frame 5:     2 (down)
Frame 6:     3+P/K (down-forward + botón)
```
**Secuencia compacta**: `[5×3][6][2][3+P/K]`

**⚠️ Nota**: DP tiene invencibilidad al inicio - reversal importante!

### Half Circle Forward (HCF / 41236)
```
Frame 1-2:   5
Frame 3:     4 (back)
Frame 4:     1 (down-back)
Frame 5:     2 (down)
Frame 6:     3 (down-forward)
Frame 7:     6+P/K (forward + botón)
```
**Secuencia compacta**: `[5×2][4][1][2][3][6+P/K]`

### Half Circle Back (HCB / 63214)
```
Frame 1-2:   5
Frame 3:     6 (forward)
Frame 4:     3 (down-forward)
Frame 5:     2 (down)
Frame 6:     1 (down-back)
Frame 7:     4+P/K (back + botón)
```
**Secuencia compacta**: `[5×2][6][3][2][1][4+P/K]`

### HCB,F (Command Grab Motion / 632146)
```
Frame 1-2:   5
Frame 3:     6 (forward)
Frame 4:     3 (down-forward)
Frame 5:     2 (down)
Frame 6:     1 (down-back)
Frame 7:     4 (back)
Frame 8:     6+P/K (forward + botón)
```
**Secuencia compacta**: `[5×2][6][3][2][1][4][6+P/K]`

**⚠️ Nota**: Común en command grabs - NO bloqueables!

---

## 🎯 Combos Básicos de Ejemplo (Frame-Perfect)

### Combo 1: cr.B > cr.A > QCF+A
```
[2×2][2+B][2×4][5]           // cr.B (8 frames total)
[2][2+A][2×3][5]             // cr.A (5 frames)
[2][3][6+A]                  // QCF+A (3 frames motion)
```
**Total**: ~16 frames de input

### Combo 2: cl.C > QCF+C
```
[5×2][5+C][5×3]              // cl.C (6 frames)
[2][3][6+C]                  // QCF+C (3 frames)
```
**Total**: ~9 frames de input

### Combo 3: j.D > cl.C > DP+A
```
// Jump in
[5×3][8×3][8×21][8+D][8×6][8×10][5×3]   // j.D
// Land y cancel
[5][5+C][5×2]                           // cl.C
[6][2][3+A]                             // DP+A
```

---

## 🎯 Secuencias de Entrenamiento Avanzadas

### Secuencia 1: Walk Forward > Command Grab (HCB,F+P)
```
// Caminar hacia el oponente
[6×30]                       // Walk forward 30 frames (~0.5s)
// Command grab motion
[6][3][2][1][4][6+A]        // HCB,F+A (6 frames motion)
```
**Total**: ~36 frames
**Uso**: Aproximarse y agarrar - no bloqueable!

### Secuencia 2: Run (Dash) > Attack
```
// Iniciar dash
[5×2][6][5][6][6×8]         // ff - dash forward (14 frames)
// Attack durante el run
[6+C]                        // Strong Punch mientras corre
[6×5]                        // Continuar corriendo (5 frames)
[5×3]                        // Recovery
```
**Total**: ~24 frames
**Uso**: Presión rápida con ataque durante dash

**Variante - Run > Throw**:
```
[5×2][6][5][6][6×8]         // Dash forward
[6+CD]                       // Throw durante run (C+D)
```

### Secuencia 3: Normal Jump > Attack
```
// Jump hacia adelante
[5×3][9×3]                   // Prejump forward (UF)
[9×18]                       // Subiendo
[9+D]                        // j.D en el apex
[9×6]                        // Animación de ataque
[9×12]                       // Cayendo
[5×3]                        // Aterrizar
```
**Total**: ~45 frames
**Uso**: Jump-in estándar con timing óptimo

**Variante - Jump Backward**:
```
[5×3][7×3]                   // Prejump UB (backward)
[7×18][7+A]                  // j.A mientras sube
[7×6][7×12][5×3]            // Animación + aterrizar
```

### Secuencia 4: Hop > Attack
```
// Hop hacia adelante (tap rápido)
[5×2][9][5]                  // Tap UF - NO mantener
[9×12]                       // Hop - más bajo y rápido
[9+C]                        // j.C en hop
[9×4]                        // Hit activo
[9×6]                        // Cayendo
[5×2]                        // Aterrizar
```
**Total**: ~27 frames
**Uso**: Presión rápida - más difícil de anti-air

**Variante - Hop Backward > Attack**:
```
[5×2][7][5]                  // Tap UB (backward hop)
[7×12][7+B]                  // j.B durante hop
[7×4][7×6][5×2]             // Hit + aterrizar
```

### Secuencia 5: Hyper Jump > Attack (Forward)
```
// Hyper jump adelante
[5×2][2×2]                   // Down charge
[9][9×2]                     // Quickly to UF (held)
[9×20]                       // Hyper jump - más alto
[9+D]                        // j.D en el aire
[9×7]                        // Hit activo
[9×9]                        // Cayendo
[5×3]                        // Aterrizar
```
**Total**: ~44 frames
**Uso**: Jump-in más rápido y alto - evita anti-airs

**Variante - Hyper Jump Backward > Attack**:
```
[5×2][2×2]                   // Down charge
[7][7×2]                     // Quickly to UB (held)
[7×20][7+C]                  // Hyper jump backward + j.C
[7×7][7×9][5×3]             // Hit + recovery
```

### Secuencia 6: Hyper Hop > Attack (Forward)
```
// Hyper hop adelante (tap rápido)
[5×2][2×2]                   // Down
[9][5]                       // Quick tap UF - soltar!
[9×10]                       // Hyper hop - bajo y rápido
[9+B]                        // j.B temprano
[9×3]                        // Hit activo
[9×5]                        // Cayendo
[5×2]                        // Aterrizar
```
**Total**: ~23 frames
**Uso**: Presión extremadamente rápida - difícil de reaccionar

**Variante - Hyper Hop Backward > Attack**:
```
[5×2][2×2]                   // Down charge
[7][5]                       // Quick tap UB
[7×10][7+A]                  // Hyper hop back + j.A
[7×3][7×5][5×2]             // Hit + aterrizar
```

### Secuencia 7: Reset Training Mode > Wait
```
// Presionar botón de reset (depende del juego)
// En KOF XV típicamente: Select/Back
[5+SELECT]             // Reset simultáneo
[5×60]                       // Esperar 1 segundo (60 frames @ 60fps)
```
**Total**: 61 frames
**Uso**: Resetear posiciones entre repeticiones de training

**Variante - Reset con confirmación**:
```
[5+SELECT+START]             // Primer press para abrir menu
[5×10]                       // Esperar menu
[5+A]                        // Confirmar reset
[5×60]                       // Esperar reset completo
```

---

## 📊 Tabla Resumen de Secuencias Avanzadas

| Secuencia | Frames Totales | Dificultad | Uso Principal |
|-----------|----------------|------------|---------------|
| Walk > Grab | ~36 | ⭐⭐ | Command throw setup |
| Run > Attack | ~24 | ⭐⭐ | Presión rápida |
| Jump > Attack | ~45 | ⭐ | Jump-in básico |
| Hop > Attack | ~27 | ⭐⭐⭐ | Presión aérea rápida |
| Hyper Jump > Attack | ~44 | ⭐⭐⭐⭐ | Evasión + presión |
| Hyper Hop > Attack | ~23 | ⭐⭐⭐⭐⭐ | Presión extrema |
| Reset > Wait | 61 | ⭐ | Training reset |

---

## 🎮 Secuencias Combinadas para Entrenamiento

### Drill 1: Neutral Game Loop
```
1. [5×30]                    // Neutral stance
2. [6×20]                    // Walk forward
3. [4×20]                    // Walk back
4. [5×2][6][5][6][6×12]     // Dash forward
5. [5×2][4][5][4][4×20]     // Backdash
6. [5+SELECT+START][5×60]   // Reset
```
**Total ciclo**: ~181 frames (~3 segundos)

### Drill 2: Jump Pattern Practice
```
1. [5×3][9×3][9×18][9+D][9×6][9×12][5×3]     // Jump forward D
2. [5×10]                                     // Pausa
3. [5×2][9][5][9×12][9+C][9×4][9×6][5×2]    // Hop forward C
4. [5×10]                                     // Pausa
5. [5×2][2×2][9][9×2][9×20][9+D][9×7][9×9][5×3]  // Hyper jump D
6. [5+SELECT+START][5×60]                     // Reset
```
**Total ciclo**: ~184 frames

### Drill 3: Approach Pattern
```
1. [6×30]                                     // Walk forward
2. [5×2][6][5][6][6×8][6+C][6×5][5×3]       // Run > Attack
3. [5×5]                                      // Pausa
4. [6][3][2][1][4][6+A]                      // Command grab
5. [5×20]                                     // Recovery
6. [5+SELECT+START][5×60]                     // Reset
```
**Total ciclo**: ~142 frames

---

## 🎮 Prioridad de Botones (Button Priority)

Cuando se presionan múltiples botones simultáneamente:

```
MaxMode/QuickMode > Roll > Blowback > D > C > Taunt > B > A
```

**Excepción en crouch**: `cr.C > cr.D`

### Ejemplos de Prioridad:
- `CD` presionados juntos → Blowback (CD)
- `AC` presionados juntos → Strong Punch (C)
- `ABCD` sin meter → Roll (AB)
- `2+CD` (crouch) → Crouch Strong Punch (cr.C)

---

## ⚙️ Configuración del Sistema de Aprendizaje

### Parámetros Ajustables

```python
REACTION_LATENCY = 12  # frames (ajustable 0-30)
VIDEO_BUFFER_BEFORE = 30  # frames antes del input (0.5s @ 60fps)
VIDEO_BUFFER_AFTER = 30   # frames después del input (0.5s)
LEARNING_RATE = 0.01      # qué tan rápido ajusta timing
```

### Pipeline de Aprendizaje

1. **Captura de Video**
   - Grabar 30 frames ANTES del input
   - Grabar frame exacto del input
   - Grabar 30 frames DESPUÉS del input
   - Total: ~1 segundo de clip @ 60 FPS

2. **Análisis Visual**
   - Detectar estado del personaje (standing, crouch, jump, etc)
   - Detectar estado del oponente
   - Detectar distancia entre personajes
   - Detectar frames de animación

3. **Medición de Reacción**
   - Medir tiempo desde estímulo visual → input
   - Comparar con REACTION_LATENCY configurado
   - Ajustar si es necesario

4. **Entrenamiento**
   - Asociar estado visual con input óptimo
   - Aprender timing de cancels
   - Aprender confirms

---

## 📊 Fase de Implementación

### Fase 1: Fundamentos (ACTUAL)
- [x] Definir sistema de notación
- [x] Mapear inputs básicos a frames
- [ ] Implementar captura de video
- [ ] Implementar detección de estados básicos

### Fase 2: Movimientos Básicos
- [ ] Entrenar en Light Punch/Kick
- [ ] Entrenar en Strong Punch/Kick
- [ ] Entrenar en cr.B (prioritario)
- [ ] Medir latencia de reacción

### Fase 3: Movimientos Especiales
- [ ] Entrenar QCF/QCB motions
- [ ] Entrenar DP motion
- [ ] Entrenar HCF/HCB motions

### Fase 4: Combos
- [ ] Entrenar cancels básicos
- [ ] Entrenar confirms
- [ ] Optimizar timing

---

## 🔍 Notas Técnicas Importantes

### Timing Windows
- **Normal Cancel**: 4-6 frames
- **Special Cancel**: 8-12 frames
- **Super Cancel**: hasta 20 frames
- **Buffer Window**: 3-5 frames para siguiente input

### Frame Data Básico (Promedio)
- **Light Normals**: 4-5 frames startup
- **Heavy Normals**: 6-8 frames startup
- **Specials**: 8-15 frames startup
- **Supers**: 1-5 frames startup (invencibles)

### Distancias
- **Close Range**: cl. normals activos (< 0.5 character width)
- **Mid Range**: st. normals activos (0.5-2 character widths)
- **Far Range**: specials/zoning (> 2 character widths)

---

## 🎯 Targets de Optimización

1. **Reacción óptima**: 8-12 frames (humano promedio: 15-20)
2. **Precisión de motion**: 95%+ en QCF/QCB
3. **Confirm rate**: 80%+ en hit confirms
4. **Anti-air timing**: 90%+ en reacción a jumps

---

## 📝 Leyenda de Notación Compacta

- `[5×N]` = Mantener neutral por N frames
- `[2+B]` = Presionar down + B simultáneamente
- `[6×14]` = Mantener forward por 14 frames
- `5` solo = Un frame de neutral
- `8+A` = Presionar up + A en el mismo frame

