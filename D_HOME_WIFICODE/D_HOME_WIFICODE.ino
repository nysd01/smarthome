#include <SPI.h>
#include <WiFiNINA.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// WiFi credentials
const char* ssid = "MTN HomeBox_92BCD1";
const char* password = "12345678911";

// MQTT broker
const char* mqtt_server = "test.mosquitto.org";
const int mqtt_port = 1883;

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// LED/Relay pins
const int ledPins[] = {3, 5, 6};
const int ledCount = sizeof(ledPins) / sizeof(ledPins[0]);

// DHT11 sensor setup
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Reconnect and fire alert
#define STATUS_LED 12
#define BUZZER_PIN 4

// OLED display setup
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Timer for temperature update
unsigned long lastTempSend = 0;
const unsigned long tempInterval = 5000;

// ====== Setup WiFi ======
void setup_wifi() {
  Serial.print("Connecting to WiFi");
  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\n✅ Connected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// ====== MQTT Callback ======
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) message += (char)payload[i];

  String topicStr = String(topic);
  Serial.println("📩 MQTT: " + topicStr + " → " + message);

  // Handle ON/OFF
  if (topicStr.indexOf("/control") > 0) {
    int idStart = topicStr.indexOf("led/") + 4;
    int idEnd = topicStr.indexOf("/control");
    int ledId = topicStr.substring(idStart, idEnd).toInt();

    if (ledId >= 1 && ledId <= ledCount) {
      digitalWrite(ledPins[ledId - 1], message == "on" ? HIGH : LOW);
      String statusTopic = "nysd/derek/led/" + String(ledId) + "/status";
      client.publish(statusTopic.c_str(), message.c_str());
      Serial.println("💡 LED " + String(ledId) + " set to " + message);
    }
  }

  // Handle brightness
  else if (topicStr.indexOf("/brightness") > 0) {
    int idStart = topicStr.indexOf("led/") + 4;
    int idEnd = topicStr.indexOf("/brightness");
    int ledId = topicStr.substring(idStart, idEnd).toInt();

    if (ledId >= 1 && ledId <= ledCount) {
      int brightness = message.toInt();
      brightness = constrain(brightness, 0, 255);
      analogWrite(ledPins[ledId - 1], brightness);
      Serial.println("🔆 LED " + String(ledId) + " brightness set to " + String(brightness));
    }
  }
}

// ====== MQTT Reconnect ======
void reconnect() {
  while (!client.connected()) {
    digitalWrite(STATUS_LED, HIGH);
    Serial.print("Connecting to MQTT...");
    if (client.connect("arduinoClientMosquitto")) {
      Serial.println("✅ MQTT connected");
      client.subscribe("nysd/derek/led/+/control");
      client.subscribe("nysd/derek/led/+/brightness");
    } else {
      Serial.print("❌ MQTT failed (rc=");
      Serial.print(client.state());
      Serial.println("), retrying...");
      digitalWrite(STATUS_LED, LOW);
      delay(5000);
    }
  }
}

// ====== Setup ======
void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(STATUS_LED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(STATUS_LED, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  for (int i = 0; i < ledCount; i++) pinMode(ledPins[i], OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);

  // ✅ OLED INIT
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("❌ OLED failed"));
    for (;;); // Halt
  }

  // Display welcome
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 10);
  display.println(F("Welcome, NYSD!"));
  display.setCursor(0, 30);
  display.println(F("D-HOME Ready!"));
  display.display();
  delay(3000);
  display.clearDisplay();
  display.display();
}

// ====== Main Loop ======
void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // 🌡️ Send temperature every 5s
  if (millis() - lastTempSend > tempInterval) {
    float temp = dht.readTemperature();
    if (!isnan(temp)) {
      String topic = "nysd/derek/temperature";
      String payload = String(temp, 1);
      client.publish(topic.c_str(), payload.c_str());
      Serial.println("🌡️ Temperature: " + payload + " °C");

      // 🔥 Fire Alert Handling
      if (temp > 30) {
        digitalWrite(BUZZER_PIN, HIGH);
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);
        display.setCursor(0, 10);
        display.println("🔥 DANGER! FIRE!");
        display.setCursor(0, 30);
        display.println("Temp: " + payload + " C");
        display.display();
      } else {
        digitalWrite(BUZZER_PIN, LOW);
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);
        display.setCursor(0, 10);
        display.println("Temp: " + payload + " C");
        display.setCursor(0, 30);
        display.println("System OK");
        display.display();
      }

    } else {
      Serial.println("⚠️ Failed to read DHT11");
    }
    lastTempSend = millis();
  }
}
