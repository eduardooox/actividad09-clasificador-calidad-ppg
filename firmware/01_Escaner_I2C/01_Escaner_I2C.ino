#include <Wire.h>

// Pines para ESP32-S3 DevKitC-1. Si tu placa es diferente,
// verifica su pinout antes de cambiarlos.
#define SDA_PIN 8
#define SCL_PIN 9

void setup() {
  Serial.begin(115200);
  delay(1000);
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.println("\nESCANEO DEL BUS I2C");
}

void loop() {
  int encontrados = 0;
  for (byte direccion = 1; direccion < 127; direccion++) {
    Wire.beginTransmission(direccion);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("Dispositivo encontrado: 0x");
      if (direccion < 16) Serial.print('0');
      Serial.println(direccion, HEX);
      encontrados++;
    }
  }
  if (encontrados == 0) Serial.println("No se detectaron dispositivos I2C.");
  Serial.println("Escaneo terminado.\n");
  delay(3000);
}