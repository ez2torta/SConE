/*
 * Definiciones de pines para ESP32
 * 
 * Puedes modificar estos pines según tu configuración de hardware
 */

#ifndef __PINS_ESP32_H__
#define __PINS_ESP32_H__

// Pines del protocolo SNES (conectar a la consola)
#define LATCH_PIN 25  // Latch/Strobe del SNES
#define CLOCK_PIN 26  // Clock del SNES
#define DATA_PIN  27  // Data serial al SNES

// Pines de botones físicos (opcional, si quieres conectar botones reales)
#define BUTTON_B      2   // GPIO2
#define BUTTON_Y      4   // GPIO4
#define BUTTON_SELECT 5   // GPIO5
#define BUTTON_START  18  // GPIO18
#define PAD_UP        19  // GPIO19
#define PAD_DOWN      21  // GPIO21
#define PAD_LEFT      22  // GPIO22
#define PAD_RIGHT     23  // GPIO23
#define BUTTON_A      13  // GPIO13
#define BUTTON_X      12  // GPIO12
#define BUTTON_L      14  // GPIO14
#define BUTTON_R      15  // GPIO15

// Índices de bits para el orden de envío SNES
// (estos NO son pines GPIO, sino posiciones de bit en el uint32_t interno)
#define SNES_B      0   // Clock 1
#define SNES_Y      1   // Clock 2
#define SNES_SELECT 2   // Clock 3
#define SNES_START  3   // Clock 4
#define SNES_UP     4   // Clock 5
#define SNES_DOWN   5   // Clock 6
#define SNES_LEFT   6   // Clock 7
#define SNES_RIGHT  7   // Clock 8
#define SNES_A      8   // Clock 9
#define SNES_X      9   // Clock 10
#define SNES_L      10  // Clock 11
#define SNES_R      11  // Clock 12

#endif
