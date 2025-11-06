/*
 * Ejemplo: Enviar comandos SNES desde Arduino/ESP32
 * 
 * Este sketch muestra cómo otro microcontrolador puede enviar
 * comandos al ESP32 que corre snes_esp32.ino
 * 
 * Conexión:
 *   TX (este Arduino) → RX (ESP32 con snes_esp32.ino)
 *   GND               → GND
 */

void setup() {
    Serial.begin(115200);
    delay(2000); // Esperar a que el ESP32 esté listo
    
    Serial.println("Enviando comandos de prueba al SNES Emulator...");
}

void loop() {
    // Presionar botón A (bit 12)
    sendSNESCommand(1 << 12);
    delay(500);
    
    // Soltar todos los botones
    sendSNESCommand(0);
    delay(500);
    
    // Presionar botón B (bit 0)
    sendSNESCommand(1 << 0);
    delay(500);
    
    // Soltar
    sendSNESCommand(0);
    delay(500);
    
    // Presionar A + B juntos
    sendSNESCommand((1 << 12) | (1 << 0));
    delay(500);
    
    // Soltar
    sendSNESCommand(0);
    delay(1000);
}

/**
 * Envía un comando de botones al ESP32
 * 
 * @param buttons - uint32_t donde cada bit representa un botón
 * 
 * Mapeo de bits:
 *   bit 0  = B
 *   bit 1  = Y
 *   bit 2  = SELECT
 *   bit 3  = START
 *   bit 6  = L
 *   bit 7  = R
 *   bit 8  = UP
 *   bit 9  = DOWN
 *   bit 10 = LEFT
 *   bit 11 = RIGHT
 *   bit 12 = A
 *   bit 2  = X
 */
void sendSNESCommand(uint32_t buttons) {
    // Enviar 4 bytes en formato little-endian
    Serial.write((uint8_t)(buttons & 0xFF));         // Byte 0 (LSB)
    Serial.write((uint8_t)((buttons >> 8) & 0xFF));  // Byte 1
    Serial.write((uint8_t)((buttons >> 16) & 0xFF)); // Byte 2
    Serial.write((uint8_t)((buttons >> 24) & 0xFF)); // Byte 3 (MSB)
}

// ============================================
// FUNCIONES DE AYUDA PARA BOTONES ESPECÍFICOS
// ============================================

void pressButton_A() { sendSNESCommand(1 << 12); }
void pressButton_B() { sendSNESCommand(1 << 0); }
void pressButton_X() { sendSNESCommand(1 << 2); }
void pressButton_Y() { sendSNESCommand(1 << 1); }
void pressButton_L() { sendSNESCommand(1 << 6); }
void pressButton_R() { sendSNESCommand(1 << 7); }
void pressButton_START() { sendSNESCommand(1 << 3); }
void pressButton_SELECT() { sendSNESCommand(1 << 2); }
void pressDPad_UP() { sendSNESCommand(1 << 8); }
void pressDPad_DOWN() { sendSNESCommand(1 << 9); }
void pressDPad_LEFT() { sendSNESCommand(1 << 10); }
void pressDPad_RIGHT() { sendSNESCommand(1 << 11); }
void releaseAll() { sendSNESCommand(0); }

// ============================================
// EJEMPLO DE USO CON LAS FUNCIONES DE AYUDA
// ============================================

void ejemploSecuencia() {
    // Saltar (A)
    pressButton_A();
    delay(100);
    releaseAll();
    delay(200);
    
    // Atacar (B)
    pressButton_B();
    delay(100);
    releaseAll();
    delay(200);
    
    // Moverse a la derecha
    pressDPad_RIGHT();
    delay(500);
    releaseAll();
    delay(200);
    
    // Salto hacia la derecha (UP + A)
    sendSNESCommand((1 << 8) | (1 << 12));
    delay(300);
    releaseAll();
}
