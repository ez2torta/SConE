/*
 * SNES Controller Emulator for ESP32
 * Adaptado para recibir comandos via Serial (uint32_t)
 * 
 * Protocolo: Envía 4 bytes (little-endian) que forman un uint32_t
 * donde cada bit representa un botón del SNES
 */

#include "pins_esp32.h"

// Variables globales
volatile uint32_t buttonState = 0; // Estado de los botones (bit=1 -> botón presionado)
volatile bool useSerial = true;    // Si true, usa Serial; si false, usa pines físicos

void initPins();
void sendButtonBit(uint32_t buttons, uint8_t bitPosition);

void setup() {
    Serial.begin(115200); // Alta velocidad para ESP32
    Serial.setTimeout(1); // Timeout mínimo para lectura rápida
    
    initPins();
    
    Serial.println("SNES Controller Emulator - ESP32");
    Serial.println("Esperando datos uint32_t (4 bytes little-endian)");
    Serial.println("Mapeo de bits:");
    Serial.println("  bit 0  = B      bit 8  = D-Up");
    Serial.println("  bit 1  = Y      bit 9  = D-Down");
    Serial.println("  bit 2  = Select bit 10 = D-Left");
    Serial.println("  bit 3  = Start  bit 11 = D-Right");
    Serial.println("  bit 4  = (n/a)  bit 12 = A");
    Serial.println("  bit 5  = (n/a)  bit 13 = X");
    Serial.println("  bit 6  = L      bit 14 = (n/a)");
    Serial.println("  bit 7  = R      bit 15 = (n/a)");
}

void loop() {
    // Leer datos del Serial si están disponibles
    if (Serial.available() >= 4) {
        uint8_t bytes[4];
        Serial.readBytes(bytes, 4);
        
        // Convertir de little-endian a uint32_t
        buttonState = ((uint32_t)bytes[0]) |
                      ((uint32_t)bytes[1] << 8) |
                      ((uint32_t)bytes[2] << 16) |
                      ((uint32_t)bytes[3] << 24);
    }
    
    // Esperar a que LATCH se ponga en HIGH
    if (digitalRead(LATCH_PIN) != HIGH) {
        return;
    }
    
    uint32_t buttons;
    
    if (useSerial) {
        // Usar el estado recibido por Serial
        // Mapear del protocolo genérico al orden SNES
        buttons = mapSerialToSNES(buttonState);
    } else {
        // Leer pines físicos (modo original)
        buttons = readPhysicalButtons();
    }
    
    // Esperar a que LATCH baje
    while (digitalRead(LATCH_PIN) == HIGH);
    
    // Enviar 12 bits de datos según el protocolo SNES
    // Orden: B, Y, Select, Start, Up, Down, Left, Right, A, X, L, R
    
    // Clock 1 - B
    sendButtonBit(buttons, SNES_B);
    waitForClockCycle();
    
    // Clock 2 - Y
    sendButtonBit(buttons, SNES_Y);
    waitForClockCycle();
    
    // Clock 3 - Select
    sendButtonBit(buttons, SNES_SELECT);
    waitForClockCycle();
    
    // Clock 4 - Start
    sendButtonBit(buttons, SNES_START);
    waitForClockCycle();
    
    // Clock 5 - Up
    sendButtonBit(buttons, SNES_UP);
    waitForClockCycle();
    
    // Clock 6 - Down
    sendButtonBit(buttons, SNES_DOWN);
    waitForClockCycle();
    
    // Clock 7 - Left
    sendButtonBit(buttons, SNES_LEFT);
    waitForClockCycle();
    
    // Clock 8 - Right
    sendButtonBit(buttons, SNES_RIGHT);
    waitForClockCycle();
    
    // Clock 9 - A
    sendButtonBit(buttons, SNES_A);
    waitForClockCycle();
    
    // Clock 10 - X
    sendButtonBit(buttons, SNES_X);
    waitForClockCycle();
    
    // Clock 11 - L
    sendButtonBit(buttons, SNES_L);
    waitForClockCycle();
    
    // Clock 12 - R
    sendButtonBit(buttons, SNES_R);
    waitForClockCycle();
    
    // Clocks 13-16 - No usados, enviar botón no presionado (HIGH)
    digitalWrite(DATA_PIN, HIGH);
}

void initPins() {
    // Pines de protocolo SNES
    pinMode(LATCH_PIN, INPUT);
    pinMode(CLOCK_PIN, INPUT);
    pinMode(DATA_PIN, OUTPUT);
    digitalWrite(DATA_PIN, HIGH); // Estado por defecto: no presionado
    
    // Pines de botones (solo si se usan físicamente)
    pinMode(BUTTON_B, INPUT_PULLUP);
    pinMode(BUTTON_Y, INPUT_PULLUP);
    pinMode(BUTTON_SELECT, INPUT_PULLUP);
    pinMode(BUTTON_START, INPUT_PULLUP);
    pinMode(BUTTON_A, INPUT_PULLUP);
    pinMode(BUTTON_X, INPUT_PULLUP);
    pinMode(BUTTON_L, INPUT_PULLUP);
    pinMode(BUTTON_R, INPUT_PULLUP);
    pinMode(PAD_UP, INPUT_PULLUP);
    pinMode(PAD_DOWN, INPUT_PULLUP);
    pinMode(PAD_LEFT, INPUT_PULLUP);
    pinMode(PAD_RIGHT, INPUT_PULLUP);
}

void waitForClockCycle() {
    // Esperar a que el clock vaya a LOW y luego a HIGH
    while (digitalRead(CLOCK_PIN) == HIGH);
    while (digitalRead(CLOCK_PIN) == LOW);
}

void sendButtonBit(uint32_t buttons, uint8_t bitPosition) {
    // SNES: LOW = presionado, HIGH = no presionado
    // buttonState: bit=1 -> presionado, bit=0 -> no presionado
    // Entonces invertimos: si el bit está en 1, enviamos LOW
    bool pressed = (buttons >> bitPosition) & 1;
    digitalWrite(DATA_PIN, pressed ? LOW : HIGH);
}

uint32_t mapSerialToSNES(uint32_t serialData) {
    /*
     * Mapeo del protocolo genérico al orden SNES interno:
     * 
     * El SNES tiene 12 botones:
     *   - 4 direccionales: Up, Down, Left, Right
     *   - 6 de acción: A, B, X, Y, L, R
     *   - 2 auxiliares: Select, Start
     * 
     * Protocolo de entrada (serialData - basado en el estándar del addon):
     *   bit 0  = B1/A       -> SNES_B (bit 0)
     *   bit 1  = B2/B       -> SNES_Y (bit 1)  
     *   bit 2  = B3/X       -> SNES_X (bit 9) y SNES_SELECT (bit 2)*
     *   bit 3  = B4/Y       -> SNES_START (bit 3)
     *   bit 4  = L1/LB      -> (no usado, podría ser L alternativo)
     *   bit 5  = R1/RB      -> (no usado, podría ser R alternativo)
     *   bit 6  = L2/LT      -> SNES_L (bit 10)
     *   bit 7  = R2/RT      -> SNES_R (bit 11)
     *   bit 8  = D-Up       -> SNES_UP (bit 4)
     *   bit 9  = D-Down     -> SNES_DOWN (bit 5)
     *   bit 10 = D-Left     -> SNES_LEFT (bit 6)
     *   bit 11 = D-Right    -> SNES_RIGHT (bit 7)
     *   bit 12 = S1/Back    -> SNES_A (bit 8)
     *   bit 13 = S2/Start   -> (no usado)
     *   bit 14 = L3         -> (no usado)
     *   bit 15 = R3         -> (no usado)
     * 
     * *Nota: bit 2 se mapea tanto a X como a SELECT porque el SNES
     *  tradicionalmente usa SELECT en juegos, pero X es común en mapeos modernos
     */
    
    uint32_t snesButtons = 0;
    
    // Botones de acción principales (4 botones de cara)
    if (serialData & (1 << 0))  snesButtons |= (1 << SNES_B);      // B (inferior derecha)
    if (serialData & (1 << 1))  snesButtons |= (1 << SNES_Y);      // Y (superior izquierda)
    if (serialData & (1 << 12)) snesButtons |= (1 << SNES_A);      // A (superior derecha)
    if (serialData & (1 << 2))  snesButtons |= (1 << SNES_X);      // X (superior centro)
    
    // Botones de hombro (2 botones L/R)
    if (serialData & (1 << 6))  snesButtons |= (1 << SNES_L);      // L (hombro izquierdo)
    if (serialData & (1 << 7))  snesButtons |= (1 << SNES_R);      // R (hombro derecho)
    
    // Botones de sistema (2 botones Select/Start)
    if (serialData & (1 << 2))  snesButtons |= (1 << SNES_SELECT); // Select (bit 2 compartido con X)
    if (serialData & (1 << 3))  snesButtons |= (1 << SNES_START);  // Start
    
    // D-Pad direccionales (4 direcciones)
    if (serialData & (1 << 8))  snesButtons |= (1 << SNES_UP);     // Arriba
    if (serialData & (1 << 9))  snesButtons |= (1 << SNES_DOWN);   // Abajo
    if (serialData & (1 << 10)) snesButtons |= (1 << SNES_LEFT);   // Izquierda
    if (serialData & (1 << 11)) snesButtons |= (1 << SNES_RIGHT);  // Derecha
    
    return snesButtons;
}

uint32_t readPhysicalButtons() {
    // Leer pines físicos (LOW = presionado)
    uint32_t buttons = 0;
    
    if (digitalRead(BUTTON_B) == LOW)      buttons |= (1 << SNES_B);
    if (digitalRead(BUTTON_Y) == LOW)      buttons |= (1 << SNES_Y);
    if (digitalRead(BUTTON_SELECT) == LOW) buttons |= (1 << SNES_SELECT);
    if (digitalRead(BUTTON_START) == LOW)  buttons |= (1 << SNES_START);
    if (digitalRead(PAD_UP) == LOW)        buttons |= (1 << SNES_UP);
    if (digitalRead(PAD_DOWN) == LOW)      buttons |= (1 << SNES_DOWN);
    if (digitalRead(PAD_LEFT) == LOW)      buttons |= (1 << SNES_LEFT);
    if (digitalRead(PAD_RIGHT) == LOW)     buttons |= (1 << SNES_RIGHT);
    if (digitalRead(BUTTON_A) == LOW)      buttons |= (1 << SNES_A);
    if (digitalRead(BUTTON_X) == LOW)      buttons |= (1 << SNES_X);
    if (digitalRead(BUTTON_L) == LOW)      buttons |= (1 << SNES_L);
    if (digitalRead(BUTTON_R) == LOW)      buttons |= (1 << SNES_R);
    
    return buttons;
}
