# 🔌 Pinout y Conexiones SNES

## Conector del Controlador SNES

### Vista Frontal del Puerto de la Consola

```
        ╭───────────────────╮
        │                   │
        │  ⚫      ⚫      ⚫ │
        │   1      2      3 │
        │                   │
        │      ⚫      ⚫    │
        │       4      5    │
        │                   │
        │       ┌────┐      │
        │       │    │      │
        ╰───────┴────┴──────╯
```

### Numeración de Pines (vista frontal)

```
         1 = GND
         2 = CLOCK
         3 = LATCH
         4 = DATA
         5 = +5V
```

## 📊 Tabla de Conexiones

| Pin SNES | Señal | Descripción | Color Cable Típico | ESP32 GPIO |
|----------|-------|-------------|--------------------|------------|
| 1 | GND | Tierra/Masa | Blanco/Negro | GND |
| 2 | CLOCK | Reloj del protocolo | Amarillo | GPIO 26 |
| 3 | LATCH | Sincronización | Naranja | GPIO 25 |
| 4 | DATA | Datos seriales | Rojo | GPIO 27 |
| 5 | +5V | Alimentación | - | **NO CONECTAR** |

> ⚠️ **IMPORTANTE:** NO conectar el pin 5 (+5V) del SNES al ESP32. El ESP32 funciona a 3.3V y conectar 5V directamente puede dañarlo.

## 🔧 Diagrama de Conexión ESP32 ↔ SNES

```
    ESP32                          SNES Console
    ─────                          ────────────
                                      ┌─────┐
   GPIO 25 ──────────────────────→ 3 │LATCH│
                                      └─────┘
   GPIO 26 ──────────────────────→ 2 │CLOCK│
                                      └─────┘
   GPIO 27 ──────────────────────→ 4 │DATA │
                                      └─────┘
   GND     ──────────────────────→ 1 │ GND │
                                      └─────┘
                                      
                                   5 │ +5V │ ← NO CONECTAR
                                      └─────┘
```

## 🎮 Cable del Controlador SNES

Si estás usando un cable de controlador SNES existente:

### Colores de Cable Estándar

| Pin | Color Común | Alternativo |
|-----|-------------|-------------|
| 1 - GND | Blanco | Negro |
| 2 - CLOCK | Amarillo | Azul |
| 3 - LATCH | Naranja | Rojo |
| 4 - DATA | Rojo | Verde |
| 5 - +5V | No conectado | - |

> **Nota:** Los colores pueden variar según el fabricante. Usa un multímetro para verificar las conexiones si no estás seguro.

## 🔬 Protocolo de Comunicación

### Timing del Protocolo SNES

```
LATCH  ┐     ┌───────────────────────────────
       └─────┘

CLOCK  ────┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─
           └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └
           1   2   3   4   5   6   7   8   9 ...

DATA   ────B───Y───S───S───U───D───L───R───A───X───L───R───1───1───1───1
           │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
           1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16

Leyenda:
  B = Button B        U = Up          A = Button A
  Y = Button Y        D = Down        X = Button X
  S = Select          L = Left        L = L Button
  S = Start           R = Right       R = R Button
  1 = No usado (siempre HIGH)
```

### Características del Protocolo

- **Velocidad:** ~16 μs por bit
- **Duración LATCH:** 12 μs HIGH, 6 μs LOW
- **Duración CLOCK:** 6 μs HIGH, 6 μs LOW
- **Total:** 16 pulsos de clock
- **Botones útiles:** 12 (clocks 1-12)
- **Frecuencia:** ~60 Hz (una lectura cada 16.67 ms)

### Lógica de Señales

| Estado | Nivel | Voltaje |
|--------|-------|---------|
| Botón PRESIONADO | LOW | ~0V |
| Botón NO PRESIONADO | HIGH | ~3.3V (ESP32) o 5V (original) |

## 🛠️ Herramientas Recomendadas

### Para Conectar al SNES:

1. **Cable de extensión SNES** (cortar y pelar)
2. **Dupont cables hembra** (para conectar al ESP32)
3. **Multímetro** (para verificar conexiones)
4. **Soldador** (opcional, para conexiones permanentes)

### Para Probar Conexiones:

```bash
# Verificar continuidad
Multímetro en modo "continuidad" (🔊)

# Medir voltajes (con SNES encendido)
Pin 1 (GND): 0V
Pin 5 (+5V): ~5V
Pins 2,3,4: ~5V en reposo (con pull-up del SNES)
```

## ⚡ Consideraciones de Voltaje

### ¿Por qué 3.3V del ESP32 funciona?

El SNES usa pull-ups internos a 5V en sus pines, pero:
- **Umbral HIGH:** >2.0V (3.3V es suficiente ✅)
- **Umbral LOW:** <0.8V (ESP32 manda ~0V ✅)

Por lo tanto, el ESP32 a 3.3V es compatible sin level shifter en la mayoría de casos.

### Level Shifter (opcional)

Si quieres ser 100% seguro o tienes problemas:

```
ESP32 3.3V ←→ Level Shifter ←→ SNES 5V
  GPIO 25         →              LATCH
  GPIO 26         →              CLOCK
  GPIO 27         →              DATA
  GND             =              GND
```

Usa un level shifter bidireccional como:
- TXS0108E (8 canales)
- BSS138 (MOSFET, por canal)
- 74LVC245 (unidireccional, pero suficiente aquí)

## 🔍 Solución de Problemas de Conexión

| Problema | Posible Causa | Solución |
|----------|---------------|----------|
| SNES no detecta controlador | Cable desconectado | Verificar continuidad con multímetro |
| Botones aleatorios | Pines cruzados | Revisar mapeo de pines |
| No hay respuesta | GND no conectado | Asegurar tierra común |
| Comportamiento errático | Interferencia | Usar cables cortos (<30cm) |
| Solo algunos botones | Error en código | Verificar mapeo en software |

## 📏 Longitud de Cables

- **Recomendado:** 10-30 cm
- **Máximo probado:** 1-2 metros
- **Con resistencias pull-up:** hasta 3 metros

Para cables largos (>1m), considera añadir:
- Resistencias pull-up de 4.7kΩ en CLOCK y LATCH
- Cable blindado para reducir interferencias

## 🧪 Test de Conexiones

Script simple para probar las conexiones en Arduino IDE:

```cpp
void setup() {
  Serial.begin(115200);
  pinMode(25, INPUT);  // LATCH
  pinMode(26, INPUT);  // CLOCK
  pinMode(27, OUTPUT); // DATA
  Serial.println("Test de pines SNES");
}

void loop() {
  Serial.print("LATCH: ");
  Serial.print(digitalRead(25));
  Serial.print(" CLOCK: ");
  Serial.println(digitalRead(26));
  delay(100);
}
```

**Resultado esperado:** 
- Sin SNES: LATCH y CLOCK pueden ser cualquier valor
- Con SNES: Deberías ver cambios cuando enciendas la consola

## 📚 Referencias

- [SNES Controller Protocol](http://www.gamefaqs.com/snes/916396-super-nintendo/faqs/5395)
- [Pinouts.ru - SNES](https://pinouts.ru/Game/SNESControllerPinout)
- [ESP32 GPIO Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)

---

**¿Listo para conectar?** Sigue la [Guía de Inicio Rápido](INICIO_RAPIDO_ESP32.md) 🚀
