/*
 * Ejemplo de cliente BLE para Arduino/ESP32
 * Conecta a SNES Controller BLE y envía comandos
 *
 * Requiere biblioteca BLE de Arduino (incluida en ESP32)
 */

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEClient.h>

// UUIDs del servicio BLE (deben coincidir con el ESP32 servidor)
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// Dirección BLE del dispositivo SNES Controller (cambiar por la real)
#define SNES_CONTROLLER_ADDRESS "xx:xx:xx:xx:xx:xx"  // Reemplaza con la dirección MAC real

BLEClient* pClient = NULL;
BLERemoteCharacteristic* pRemoteCharacteristic = NULL;
bool connected = false;

// Mapeo de botones para uint32_t
#define BUTTON_A      (1 << 12)
#define BUTTON_B      (1 << 0)
#define BUTTON_X      (1 << 2)
#define BUTTON_Y      (1 << 1)
#define BUTTON_L      (1 << 6)
#define BUTTON_R      (1 << 7)
#define BUTTON_SELECT (1 << 2)  // Compartido con X
#define BUTTON_START  (1 << 3)
#define DPAD_UP       (1 << 8)
#define DPAD_DOWN     (1 << 9)
#define DPAD_LEFT     (1 << 10)
#define DPAD_RIGHT    (1 << 11)

class MyClientCallback : public BLEClientCallbacks {
  void onConnect(BLEClient* pclient) {
    connected = true;
    Serial.println("Conectado al SNES Controller!");
  }

  void onDisconnect(BLEClient* pclient) {
    connected = false;
    Serial.println("Desconectado del SNES Controller");
  }
};

bool connectToServer() {
    Serial.print("Conectando a SNES Controller...");

    pClient = BLEDevice::createClient();
    pClient->setClientCallbacks(new MyClientCallback());

    // Conectar a la dirección específica
    if (!pClient->connect(BLEAddress(SNES_CONTROLLER_ADDRESS))) {
        Serial.println("Error al conectar");
        return false;
    }

    Serial.println("Conectado!");

    // Obtener el servicio remoto
    BLERemoteService* pRemoteService = pClient->getService(BLEUUID(SERVICE_UUID));
    if (pRemoteService == nullptr) {
        Serial.println("Servicio no encontrado");
        pClient->disconnect();
        return false;
    }

    // Obtener la característica remota
    pRemoteCharacteristic = pRemoteService->getCharacteristic(BLEUUID(CHARACTERISTIC_UUID));
    if (pRemoteCharacteristic == nullptr) {
        Serial.println("Característica no encontrada");
        pClient->disconnect();
        return false;
    }

    return true;
}

void sendButtons(uint32_t buttonMask) {
    if (!connected || pRemoteCharacteristic == nullptr) {
        Serial.println("No conectado");
        return;
    }

    // Convertir uint32_t a bytes little-endian
    uint8_t data[4];
    data[0] = buttonMask & 0xFF;
    data[1] = (buttonMask >> 8) & 0xFF;
    data[2] = (buttonMask >> 16) & 0xFF;
    data[3] = (buttonMask >> 24) & 0xFF;

    pRemoteCharacteristic->writeValue(data, 4);
    Serial.printf("Enviado: 0x%08X\n", buttonMask);
}

void setup() {
    Serial.begin(115200);
    Serial.println("Cliente BLE SNES Controller");

    // Inicializar BLE
    BLEDevice::init("SNES Client");

    // Escanear y conectar
    if (connectToServer()) {
        Serial.println("Listo para enviar comandos!");
    } else {
        Serial.println("Error al conectar. Verifica la dirección BLE.");
    }
}

void loop() {
    if (!connected) {
        delay(1000);
        return;
    }

    // Ejemplo: enviar secuencia de botones
    static uint32_t sequence[] = {
        BUTTON_A,
        BUTTON_B,
        BUTTON_X,
        BUTTON_Y,
        DPAD_UP,
        DPAD_DOWN,
        DPAD_LEFT,
        DPAD_RIGHT,
        BUTTON_START,
        0  // Reset
    };

    static int index = 0;
    static unsigned long lastSend = 0;

    if (millis() - lastSend > 1000) {  // Enviar cada segundo
        sendButtons(sequence[index]);
        index = (index + 1) % (sizeof(sequence) / sizeof(sequence[0]));
        lastSend = millis();
    }

    delay(100);
}