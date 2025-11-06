/*
 * SNES Controller Emulator for ESP32
 * Adaptado para recibir comandos via Bluetooth BLE (uint32_t)
 * 
 * Protocolo: Envía 4 bytes (little-endian) que forman un uint32_t
 * donde cada bit representa un botón del SNES
 */

#include "pins_esp32.h"
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// UUIDs para el servicio BLE
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// Variables globales
volatile uint32_t buttonState = 0; // Estado de los botones (bit=1 -> botón presionado)
volatile bool newBLEData = false;  // Flag para indicar nuevos datos BLE
volatile uint8_t bleBuffer[4];     // Buffer para datos BLE

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
        // Obtener los datos como String y copiar a buffer
        String value = pCharacteristic->getValue();
        if (value.length() == 4) {
            // Copiar bytes al buffer (igual que Serial.readBytes)
            for (int i = 0; i < 4; i++) {
                bleBuffer[i] = (uint8_t)value[i];
            }
            newBLEData = true;
            
            // Debug: mostrar lo recibido
            Serial.printf("BLE recibido: %02X %02X %02X %02X\n", 
                         bleBuffer[0], bleBuffer[1], bleBuffer[2], bleBuffer[3]);
        } else {
            Serial.printf("BLE: longitud incorrecta (%d bytes)\n", value.length());
        }
    }
};

void initPins();
void sendButtonBit(uint32_t buttons, uint8_t bitPosition);

void setup() {
    Serial.begin(115200);
    
    initPins();
    
    // Inicializar BLE
    BLEDevice::init("SNES Controller");
    pServer = BLEDevice::createServer();
    
    BLEService *pService = pServer->createService(SERVICE_UUID);
    
    pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
    );
    
    pCharacteristic->setCallbacks(new MyCallbacks());
    pCharacteristic->setValue("0"); // Valor inicial
    
    pService->start();
    
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();
    
    Serial.println("SNES Controller Emulator - ESP32 BLE");
    Serial.println("BLE iniciado. Esperando conexiones...");
    Serial.println("Envía 4 bytes (little-endian) via BLE para controlar botones");
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
    // Procesar datos BLE si hay nuevos (igual que Serial)
    if (newBLEData) {
        // Convertir de little-endian a uint32_t (igual que Serial)
        buttonState = ((uint32_t)bleBuffer[0]) |
                      ((uint32_t)bleBuffer[1] << 8) |
                      ((uint32_t)bleBuffer[2] << 16) |
                      ((uint32_t)bleBuffer[3] << 24);
        
        newBLEData = false;
        
        // Debug: mostrar conversión
        Serial.printf("Convertido a buttonState: 0x%08X\n", buttonState);
    }
    
    // Esperar a que LATCH se ponga en HIGH
    if (digitalRead(LATCH_PIN) != HIGH) {
        return;
    }
    
    uint32_t buttons = mapSerialToSNES(buttonState);
    
    // Debug: mostrar estado cada cierto tiempo
    static unsigned long lastDebug = 0;
    if (millis() - lastDebug > 1000) {
        Serial.printf("buttonState: 0x%08X, SNES buttons: 0x%03X\n", buttonState, buttons);
        lastDebug = millis();
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
    delay(1)
}

void initPins() {
    // Pines de protocolo SNES
    pinMode(LATCH_PIN, INPUT);
    pinMode(CLOCK_PIN, INPUT);
    pinMode(DATA_PIN, OUTPUT);
    digitalWrite(DATA_PIN, HIGH); // Estado por defecto: no presionado
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
    
    // Debug: mostrar qué bit se está enviando
    static uint8_t bitCount = 0;
    if (bitCount == 0) {
        Serial.print("SNES bits: ");
    }
    Serial.print(pressed ? "1" : "0");
    bitCount++;
    if (bitCount >= 12) {
        Serial.println();
        bitCount = 0;
    }
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
    
    // Debug: mostrar mapeo cada cierto tiempo
    static uint32_t lastSerialData = 0;
    static unsigned long lastMapDebug = 0;
    if (serialData != lastSerialData && millis() - lastMapDebug > 500) {
        Serial.printf("Mapeo: entrada 0x%08X -> SNES 0x%03X\n", serialData, snesButtons);
        lastSerialData = serialData;
        lastMapDebug = millis();
    }
    
    return snesButtons;
}
