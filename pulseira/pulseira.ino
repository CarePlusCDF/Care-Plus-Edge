//Autores: Gabriel Ardito, Felipe Menezes, João Sarracine, João Gonzales
//Projeto: Boost Care - Pulseira Inteligente
//Descrição: Pulseira com detecção de movimento (MPU6050), sensor touch capacitivo (4 vias),
//           vibração (vibracall), comunicação MQTT/FIWARE e contagem de passos com metas.
//Revisão: Sprint 3
 
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
 
// ========== CONFIGURAÇÕES MQTT ==========
const char* topicPrefix        = "step001";
const char* SSID               = "FIAP-IOT";
const char* PASSWORD           = "F!@p25.IOT";
const char* BROKER_MQTT        = "34.95.171.195";
const int   BROKER_PORT        = 1883;
const char* TOPICO_SUBSCRIBE   = "/TEF/step001/cmd";
const char* TOPICO_ATTRS       = "/ul/TEF/step001/attrs";
const char* ID_MQTT            = "fiware_step001";
 
// ========== CONFIGURAÇÕES DE PASSOS ==========
const int          PASSOS_MINIMOS = 10;
const unsigned long JANELA_MS      = 30UL * 1000;
const unsigned long PUBLISH_MS     = 10UL * 1000;
 
// ========== PINOS ESP32-S3 MINI ==========
const int VIBRACALL_PIN   = 4;      // Vibracall (motor vibratório)
const int TOUCH_1_PIN     = 5;      // Touch capacitivo 1
const int TOUCH_2_PIN     = 6;      // Touch capacitivo 2
const int TOUCH_3_PIN     = 7;      // Touch capacitivo 3
const int TOUCH_4_PIN     = 10;     // Touch capacitivo 4
const int SDA_PIN         = 20;     // SDA do MPU6050
const int SCL_PIN         = 21;     // SCL do MPU6050
 
// ========== CONFIGURAÇÕES DE VIBRAÇÃO ==========
const int VIBRA_INTENSITY = 200;    // Intensidade PWM (0-255)
const int VIBRA_FREQ      = 1000;   // Frequência PWM em Hz
const int VIBRA_DURATION  = 100;    // Duração de cada pulso em ms
 
// ========== CONFIGURAÇÕES DE TOUCH ==========
const unsigned long DEBOUNCE_TOUCH_MS = 200;
const unsigned long SOS_HOLD_MS       = 3000;
 
// ========== VARIÁVEIS DE ESTADO ==========
bool          estadoAnteriorTouch[4] = {LOW, LOW, LOW, LOW};
unsigned long ultimoDebounceTouch[4] = {0, 0, 0, 0};
unsigned long pressaoInicioSOS       = 0;
bool          sosAguardando          = false;
 
// ========== WIFI E MQTT ==========
WiFiClient       espClient;
PubSubClient     MQTT(espClient);
 
// ========== MPU6050 ==========
Adafruit_MPU6050 mpu;
sensors_event_t  event;
 
// ========== VARIÁVEIS DE PASSOS ==========
int           passos        = 0;
int           passosJanela  = 0;
unsigned long ultimoPasso   = 0;
unsigned long inicioJanela  = 0;
unsigned long ultimoPublish = 0;
float         anterior      = 0;
bool          vibrando      = false;
 
// ========== VARIÁVEIS DE VIBRAÇÃO ==========
unsigned long ultimaVibracao = 0;
bool          contadorVibracall = false;
 
// ============================================
// FUNÇÕES DE VIBRAÇÃO
// ============================================
 
void iniciarVibracall() {
  digitalWrite(VIBRACALL_PIN, HIGH);
  contadorVibracall = true;
  ultimaVibracao = millis();
  Serial.println(">> Vibração iniciada.");
}
 
void pararVibracall() {
  digitalWrite(VIBRACALL_PIN, LOW);
  contadorVibracall = false;
  vibrando = false;
  Serial.println(">> Vibração parada.");
}
 
void vibrarPulsos(int numPulsos, int delayMs) {
  for (int i = 0; i < numPulsos; i++) {
    digitalWrite(VIBRACALL_PIN, HIGH);
    delay(delayMs);
    digitalWrite(VIBRACALL_PIN, LOW);
    delay(delayMs);
  }
}
 
// ============================================
// FUNÇÕES DE WIFI
// ============================================
 
void initWiFi() {
  WiFi.begin(SSID, PASSWORD);
  Serial.print("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi conectado. IP: ");
  Serial.println(WiFi.localIP());
}
 
void reconectWiFi() {
  if (WiFi.status() != WL_CONNECTED) initWiFi();
}
 
// ============================================
// FUNÇÕES MQTT
// ============================================
 
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (int i = 0; i < length; i++) msg += (char)payload[i];
  Serial.print("Comando recebido: ");
  Serial.println(msg);
 
  msg.toLowerCase();
  msg.trim();
 
  if (msg.indexOf("agua") != -1) {
    Serial.println(">> Comando 'agua' recebido.");
    vibrarPulsos(2, 150);
  }
}
 
void reconnectMQTT() {
  while (!MQTT.connected()) {
    Serial.print("Conectando ao broker MQTT...");
    if (MQTT.connect(ID_MQTT)) {
      Serial.println(" conectado!");
      MQTT.subscribe(TOPICO_SUBSCRIBE);
    } else {
      Serial.println(" falha. Tentando em 2s.");
      delay(2000);
    }
  }
}
 
void verificaConexoes() {
  reconectWiFi();
  if (!MQTT.connected()) reconnectMQTT();
}
 
// ============================================
// FUNÇÕES DE PUBLICAÇÃO
// ============================================
 
void publicarDados() {
  float mediaMin = (passosJanela > 0) ? (float)passosJanela * (60000.0 / JANELA_MS) : 0;
 
  char payload[64];
  snprintf(payload, sizeof(payload), "p|%d|m|%.1f", passos, mediaMin);
  MQTT.publish(TOPICO_ATTRS, payload);
 
  Serial.println("─────────────────────────────────");
  Serial.print("Publicado | Passos totais: ");
  Serial.print(passos);
  Serial.print(" | Média: ");
  Serial.print(mediaMin);
  Serial.println(" passos/min");
  Serial.println("─────────────────────────────────");
 
  passosJanela = 0;
}
 
void publicarToque(const char* evento) {
  char payload[64];
  snprintf(payload, sizeof(payload), "t|%s", evento);
  MQTT.publish(TOPICO_ATTRS, payload);
  Serial.print("Toque publicado: ");
  Serial.println(payload);
}
 
// ============================================
// INICIALIZAÇÃO DE PINOS
// ============================================
 
void initPinos() {
  // Vibracall como saída
  pinMode(VIBRACALL_PIN, OUTPUT);
  digitalWrite(VIBRACALL_PIN, LOW);
 
  // Touch capacitivo como entradas
  pinMode(TOUCH_1_PIN, INPUT);
  pinMode(TOUCH_2_PIN, INPUT);
  pinMode(TOUCH_3_PIN, INPUT);
  pinMode(TOUCH_4_PIN, INPUT);
 
  Serial.println("Pinos inicializados com sucesso!");
}
 
// ============================================
// LEITURA DOS SENSORES TOUCH
// ============================================
 
void lerSensoresTouch() {
  unsigned long agora = millis();
  int pinosToque[4] = {TOUCH_1_PIN, TOUCH_2_PIN, TOUCH_3_PIN, TOUCH_4_PIN};
  const char* nomesToques[4] = {"missao_progresso", "missao_saiu", "agua_confirmada", "sos"};
 
  // Processamento dos 3 primeiros botões (touch 1, 2, 3)
  for (int i = 0; i < 3; i++) {
    int leitura = digitalRead(pinosToque[i]);
 
    if (leitura != estadoAnteriorTouch[i]) {
      ultimoDebounceTouch[i] = agora;
      estadoAnteriorTouch[i] = leitura;
    }
 
    if ((agora - ultimoDebounceTouch[i]) >= DEBOUNCE_TOUCH_MS && leitura == HIGH) {
      switch (i) {
        case 0:
          publicarToque("missao_progresso");
          Serial.println(">> Toque 1 - Progresso na missão registrado.");
          vibrarPulsos(1, 100);
          break;
        case 1:
          publicarToque("missao_saiu");
          Serial.println(">> Toque 2 - Saiu da missão.");
          vibrarPulsos(2, 100);
          break;
        case 2:
          publicarToque("agua_confirmada");
          Serial.println(">> Toque 3 - Hidratação confirmada.");
          if (vibrando) pararVibracall();
          vibrarPulsos(1, 150);
          break;
      }
      estadoAnteriorTouch[i] = LOW;
    }
  }
 
  // Processamento do botão SOS (touch 4) - segura 3s
  int leituraSOS = digitalRead(TOUCH_4_PIN);
 
  if (leituraSOS != estadoAnteriorTouch[3]) {
    ultimoDebounceTouch[3] = agora;
    estadoAnteriorTouch[3] = leituraSOS;
  }
 
  if (agora - ultimoDebounceTouch[3] >= DEBOUNCE_TOUCH_MS) {
    if (leituraSOS == HIGH && !sosAguardando) {
      sosAguardando = true;
      pressaoInicioSOS = agora;
      Serial.println(">> Botão SOS pressionado. Aguardando 3s para confirmação...");
      vibrarPulsos(2, 150);
    }
    if (leituraSOS == LOW && sosAguardando) {
      sosAguardando = false;
      Serial.println(">> Botão SOS liberado antes de 3s.");
    }
    if (sosAguardando && (agora - pressaoInicioSOS >= SOS_HOLD_MS)) {
      publicarToque("sos");
      Serial.println(">> SOS ENVIADO! Alerta de emergência ativado.");
      vibrarPulsos(5, 200);
      sosAguardando = false;
    }
  }
}
 
// ============================================
// SETUP
// ============================================
 
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n=== BOOST CARE - PULSEIRA INTELIGENTE ===\n");
 
  // Inicializa pinos
  initPinos();
 
  // Inicializa MPU6050 com I2C customizado
  Wire.setPins(SDA_PIN, SCL_PIN);
  Wire.begin();
 
  int tentativas = 0;
  while (!mpu.begin() && tentativas < 5) {
    Serial.print("MPU6050 não encontrado... tentativa ");
    Serial.println(tentativas + 1);
    delay(1000);
    tentativas++;
  }
 
  if (tentativas >= 5) {
    Serial.println("ERRO: MPU6050 não inicializou!");
  } else {
    Serial.println("MPU6050 pronto!");
    mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
    mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  }
 
  // Inicializa WiFi e MQTT
  initWiFi();
  MQTT.setServer(BROKER_MQTT, BROKER_PORT);
  MQTT.setCallback(mqtt_callback);
 
  inicioJanela  = millis();
  ultimoPublish = millis();
 
  Serial.println("=================================");
  Serial.print("Dispositivo: ");
  Serial.println(topicPrefix);
  Serial.print("Meta: ");
  Serial.print(PASSOS_MINIMOS);
  Serial.print(" passos em ");
  Serial.print(JANELA_MS / 1000);
  Serial.println("s");
  Serial.println("Touch 1: Progresso Missão");
  Serial.println("Touch 2: Sair Missão");
  Serial.println("Touch 3: Confirmar Água");
  Serial.println("Touch 4: SOS (segura 3s)");
  Serial.println("=================================\n");
 
  vibrarPulsos(3, 100);
}
 
// ============================================
// LOOP PRINCIPAL
// ============================================
 
void loop() {
  unsigned long agora = millis();
 
  // Verifica conexões
  verificaConexoes();
  MQTT.loop();
 
  // Lê acelerômetro
  mpu.getAccelerometerSensor()->getEvent(&event);
  float total = sqrt(
    event.acceleration.x * event.acceleration.x +
    event.acceleration.y * event.acceleration.y +
    event.acceleration.z * event.acceleration.z
  );
 
  // Detecta passos
  float delta = total - anterior;
  if (delta > 3 && agora - ultimoPasso > 500) {
    passos++;
    passosJanela++;
    ultimoPasso = agora;
 
    unsigned long restante = (JANELA_MS - (agora - inicioJanela)) / 1000;
    Serial.print("Passo! Total: ");
    Serial.print(passos);
    Serial.print(" | Janela restante: ");
    Serial.print(restante);
    Serial.println("s");
 
    if (vibrando) pararVibracall();
 
    vibrarPulsos(1, 50);
  }
  anterior = total;
 
  // Lê sensores touch
  lerSensoresTouch();
 
  // Publica dados periodicamente
  if (agora - ultimoPublish >= PUBLISH_MS) {
    publicarDados();
    ultimoPublish = agora;
  }
 
  // Verifica fim da janela
  if (agora - inicioJanela >= JANELA_MS) {
    Serial.println("=================================");
    Serial.print("Janela encerrada. Passos: ");
    Serial.print(passosJanela);
    Serial.print(" / Meta: ");
    Serial.println(PASSOS_MINIMOS);
 
    if (passosJanela < PASSOS_MINIMOS) {
      Serial.print("Meta não atingida! Faltaram ");
      Serial.print(PASSOS_MINIMOS - passosJanela);
      Serial.println(" passos. Vibrando...");
      vibrando = true;
      iniciarVibracall();
    } else {
      Serial.println("Meta atingida! Parabéns!");
      vibrarPulsos(2, 150);
    }
    Serial.println("=================================\n");
 
    passosJanela = 0;
    inicioJanela = agora;
  }
 
  // Mantém vibração contínua se necessário
  if (vibrando && contadorVibracall) {
    if (agora - ultimaVibracao >= (VIBRA_DURATION * 2)) {
      pararVibracall();
    }
  }
 
  delay(50);
}