#include <Wire.h>
#include "MAX30105.h"  // La biblioteca SparkFun MAX3010x también es compatible con MAX30102

#define SDA_PIN 8
#define SCL_PIN 9
#define SERIAL_BAUD 115200

// Configuración inicial para obtener solo el canal rojo a 100 muestras/s.
const byte LED_BRIGHTNESS = 0x1F;  // Intensidad inicial moderada
const byte SAMPLE_AVERAGE = 1;
const byte LED_MODE = 1;           // 1 = rojo solamente
const int SAMPLE_RATE = 100;       // muestras/s
const int PULSE_WIDTH = 411;       // microsegundos
const int ADC_RANGE = 4096;

MAX30105 sensor;
uint32_t sampleIndex = 0;

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(1000);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);

  Serial.println("# Iniciando MAX30102...");
  if (!sensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("# ERROR: MAX30102 no detectado. Revise VCC, GND, SDA y SCL.");
    while (true) delay(1000);
  }

  sensor.setup(LED_BRIGHTNESS, SAMPLE_AVERAGE, LED_MODE,
               SAMPLE_RATE, PULSE_WIDTH, ADC_RANGE);
  sensor.setPulseAmplitudeRed(LED_BRIGHTNESS);
  sensor.setPulseAmplitudeIR(0);
  sensor.setPulseAmplitudeGreen(0);

  delay(500);
  Serial.println("# MAX30102 listo. Coloque el dedo sin presionar excesivamente.");
  Serial.println("sample_idx,red_raw");
}

void loop() {
  sensor.check();  // Actualiza el FIFO interno del MAX30102

  while (sensor.available()) {
    uint32_t redValue = sensor.getFIFORed();
    Serial.print(sampleIndex++);
    Serial.print(',');
    Serial.println(redValue);
    sensor.nextSample();
  }
}
