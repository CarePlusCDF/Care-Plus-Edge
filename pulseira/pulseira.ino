//Autores: Gabriel Ardito, Felipe Menezes, João Sarracine, João Gonzales
//Resumo: Esse programa possibilita ligar e desligar o ledRgb, além de permetir o usuário escolher entre cores predefinidas, códigos hexadecimáis e adicionar cores novase também manda o status para o Broker MQTT possibilitando o Helix saber
//se o led está ligado ou desligado.
//Revisões:


//importando bibliotecas
#include <WiFi.h>
#include <PubSubClient.h>
#include <vector>
// Configurações - variáveis editáveis
const char* default_SSID = "Wokwi GUEST"; // Nome da rede Wi-Fi
const char* default_PASSWORD = ""; // Senha da rede Wi-Fi
const char* default_BROKER_MQTT = "bore.pub"; // IP do Broker MQTT
const int default_BROKER_PORT = 33313; // Porta do Broker MQTT
const char* default_TOPICO_SUBSCRIBE = "/TEF/lamp002/cmd"; // Tópico MQTT de escuta
const char* default_TOPICO_SUBSCRIBE2 = "/TEF/lamp002/cmd/"; // Tópico MQTT de escuta // recebendo mudanca de cor
const char* default_TOPICO_PUBLISH_1 = "/TEF/lamp002/attrs"; // Tópico MQTT de envio de informações para Broker
const char* default_TOPICO_PUBLISH_2 = "/TEF/lamp002/attrs/l"; // Tópico MQTT de envio de informações para Broker
const char* default_PICO_PUBLISH_3 = "/tef/lamp";
const char* default_ID_MQTT = "fiware_001"; // ID MQTT

// Declaração da variável para o prefixo do tópico
const char* topicPrefix = "lamp002";
 
// Variáveis para configurações editáveis
char* SSID = const_cast<char*>(default_SSID);
char* PASSWORD = const_cast<char*>(default_PASSWORD);
char* BROKER_MQTT = const_cast<char*>(default_BROKER_MQTT);
int BROKER_PORT = default_BROKER_PORT;
char* TOPICO_SUBSCRIBE = const_cast<char*>(default_TOPICO_SUBSCRIBE);
char* TOPICO_PUBLISH_1 = const_cast<char*>(default_TOPICO_PUBLISH_1);
char* TOPICO_PUBLISH_2 = const_cast<char*>(default_TOPICO_PUBLISH_2);
char* ID_MQTT = const_cast<char*>(default_ID_MQTT);

 
//iniciando tratamento de portas do difusor, cada letra do rgb se comporta como um led independente, por isso 3 entradas
const int RED_PIN = 25;
const int GREEN_PIN = 26;
const int BLUE_PIN = 27;
 
WiFiClient espClient;
PubSubClient MQTT(espClient);
char EstadoSaida = '0';

std::vector<String> nomesCores = {"ligar", "desligar", "vermelho", "azul", "verde", "amarelo"};
std::vector<String> hexaCores = {"#FFFFFF", "#000000", "#FF0000", "#0000FF", "#00FF00", "#FFFF00"};
void initSerial() {
    Serial.begin(115200);
}

void initWiFi() {
    delay(10);
    Serial.println("------Conexao WI-FI------");
    Serial.print("Conectando-se na rede: ");
    Serial.println(SSID);
    Serial.println("Aguarde");
    reconectWiFi();
}
 
void initMQTT() {
    MQTT.setServer(BROKER_MQTT, BROKER_PORT);
    MQTT.setCallback(mqtt_callback);
}
 
void setup() {
    InitOutput();
    initSerial();
    initWiFi();
    initMQTT();
    delay(5000);
    MQTT.publish(TOPICO_PUBLISH_1, "s|on");
}
 
void loop() {
    VerificaConexoesWiFIEMQTT();
    EnviaEstadoOutputMQTT();
    handleLuminosity();
    MQTT.loop();
}
 
void reconectWiFi() {
    if (WiFi.status() == WL_CONNECTED)
        return;
    WiFi.begin(SSID, PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(100);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("Conectado com sucesso na rede ");
    Serial.print(SSID);
    Serial.println("IP obtido: ");
    Serial.println(WiFi.localIP());
    //Garante que o Led inicie apagado
    setarCorPraHex("#000000");
   
}
 
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String msg;

    for (int i = 0; i < length; i++) {
        char c = (char)payload[i];
        msg += c;
    }

    // tratando a mensagem antes das validacoes
    msg.trim();
    msg.toLowerCase();
    Serial.print("- Mensagem recebida: ");
    Serial.println(msg);
 
    // procura o pipe
    int pos = msg.indexOf('|');
    // no caso de msg = "lamp001@cor|vermelho", corta tudo antes e deixa
    if (pos != -1) {
    msg = msg.substring(pos + 1);
    }
     


    //aqui acresentamos a lógica de chamada da funcao de cor pra hexadecimal
    if(msg.startsWith("#")){
      Serial.println("cor recebida Hex:");
      Serial.println(msg);
      EstadoSaida = '1';
 
      // chama funcao setarUsandoHexa passando msg como parametro
      setarUsandoHexa(msg);
    }else if(msg[0] == 'a' && msg[1] == 'd' && msg[2] == 'd'){ // "" é string, '' é char
      adicionarNovaCor(msg);
      EstadoSaida = '1';
      return;

    }else if(msg.length() > 0){
      Serial.println("cor recebida Nome:");
      Serial.println(msg);
      setarUsandoNome(msg);

    }if (msg == "#000000" || msg == "desligar") {
      EstadoSaida = '0';
    }

    }

// verifica se o MQTT está conectado
void VerificaConexoesWiFIEMQTT() {
    if (!MQTT.connected()){
        reconnectMQTT();
        }
    reconectWiFi();
}

// printa o estado do Led na Serial
void EnviaEstadoOutputMQTT() {
    if (EstadoSaida == '1') {
        Serial.println("- Led Ligado"); 
    }
 
    if (EstadoSaida == '0') {
        Serial.println("- Led Desligado");
    }
    Serial.println("- Estado do LED enviado ao broker!");
    delay(1000);
}
 
void InitOutput() {
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);
}
void reconnectMQTT() {
    while (!MQTT.connected()) {
        Serial.print("* Tentando se conectar ao Broker MQTT: ");
        Serial.println(BROKER_MQTT);
        if (MQTT.connect(ID_MQTT)) {
            Serial.println("Conectado com sucesso ao broker MQTT!");
            MQTT.subscribe(TOPICO_SUBSCRIBE);
        } else {
            Serial.println("Falha ao reconectar no broker.");
            Serial.println("Haverá nova tentativa de conexão em 2s");
            delay(2000);
        }
    }
}

void handleLuminosity() {
    const int potPin = 34;
    int sensorValue = analogRead(potPin);
    int luminosity = map(sensorValue, 0, 4095, 0, 100);// mapeando o valor da luminosidade, para 0 a 100
    String mensagem = String(luminosity);
    Serial.print("Valor da luminosidade: ");
    Serial.println(mensagem.c_str());
    MQTT.publish(TOPICO_PUBLISH_2, mensagem.c_str());
}
 
// funcao que converte o hexadecimal em RGB
 
void setarCorPraHex(String hexColor){
  // removendo o # caso a string seja "#xxxxx" por exemplo, deixando só os caractere numéricos
  if (hexColor.startsWith("#")){
    hexColor.remove(0, 1);
  }
 
  // convertendo a string recebida em um numero inteiro que o esp consegue usar
  // esp normalmente tem 32 bits
  // exemplo: 0xFFFFFF = 16777215
  //strtol -> String To Long ou seja, texto pra numero
  //hexColor.c_str() --> conversão de tipo, temos String hexColor, mas o strtol() não aceita String, ele aceita chars 
  // resumidamente, transformamos String "#FF0000" em FF0000 (formato C)
  // NULL indica onde a conversão deve parar, sem isso oq não é numero ficaria como "endptr", não queremos isso.
  // com o 16 estamos ditando a base numérica que queremos, Hex de 16, tamo quase lá
  //vai ficar mais ou menos assim:
  //  FF AA 33
  //  │  │  │
  //  R  G  B
  // IMPORTANTE --> O hexadecimal já é RGB compactado em 24 bits. Por isso separamos por >> (Bit Shifting)
  long number = strtol(hexColor.c_str(), NULL, 16);
 
  // feito isso, podemos só declarar:
  // 0xFF indica pro compilador que o valor tá em hexadecimal
  int r = number >> 16;
  int g = (number >> 8) & 0xFF;
  int b= number & 0xFF;
 
    analogWrite(RED_PIN, r);
    analogWrite(GREEN_PIN, g);
    analogWrite(BLUE_PIN, b);
 
    Serial.print("RGB -> ");
    Serial.print(r);
    Serial.print(",");
    Serial.print(g);
    Serial.print(",");
    Serial.println(b);
}

void setarUsandoNome(String msg) {
    msg.trim();
    msg.toLowerCase();

    // Com vector, usamos .size() para saber quantos itens existem
    int total = nomesCores.size(); 

    for (int i = 0; i < total; i++) {
        if (msg == nomesCores[i]) {
            Serial.print("Sucesso! Nome: "); Serial.print(nomesCores[i]);
            Serial.print(" -> Hex: "); Serial.println(hexaCores[i]);
            EstadoSaida ='1';
            setarCorPraHex(hexaCores[i]);
            return; // Encontrou? Sai da função.
        }
        
    }Serial.println("Cor nao encontrada na lista.");
    EstadoSaida = '0';
}

void setarUsandoHexa(String msg){
  setarCorPraHex(msg);
}

void adicionarNovaCor(String msg) {
  // No Arduino, usamos int ou size_t, mas o retorno de erro é -1
  int pos1 = msg.indexOf('|'); 
  int pos2 = msg.indexOf('|', pos1 + 1);

  // Verificamos se encontrou os dois pipes (-1 significa não encontrado)
  if (pos1 != -1 && pos2 != -1) {
    
    // No Arduino: substring(inicio, fim) 
    // Diferente do C++ padrão, o segundo parâmetro é a POSIÇÃO FINAL, não o tamanho.
    String nomeCor = msg.substring(pos1 + 1, pos2); 
    String hexaCor = msg.substring(pos2 + 1);

    nomesCores.push_back(nomeCor);
    hexaCores.push_back(hexaCor);

    Serial.print("Nova cor cadastrada: ");
    Serial.println(nomeCor);

    EstadoSaida = '1';
    Serial.println(EstadoSaida);
    setarUsandoNome(nomeCor);


  } else {
    Serial.println("Erro no formato! Use: add|nome|#hexa");
  }
}