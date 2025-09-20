#include <AFMotor.h>

AF_DCMotor esq_tras(1);
AF_DCMotor dir_tras(2);
AF_DCMotor dir_frente(3);
AF_DCMotor esq_frente(4);

int dif_motores = 0;
int vel = 70;
int distancia_ultra;

unsigned long memoria = 0;

int pino_esq_fora = 14;
int pino_esq_dentro = 15;
int pino_dir_dentro = 16;
int pino_dir_fora = 17;

#define G 32
#define R 30
#define B 28
#define TRIG 50
#define ECHO 52

int PRETO = 1;
int BRANCO = 0;

unsigned long tempo2 = 0;
int intervalo = 1000;

// Variáveis dos sensores (inicializadas depois no atualizar_sensores)
int sensor_esq_dentro;
int sensor_dir_dentro;
int sensor_esq_fora;
int sensor_dir_fora;

// Estados lógicos
bool todosPreto;
bool algumPreto;
bool dentroPreto;
bool algumEsq;
bool algumDir;
bool todosEsq;
bool todosDir;
bool foraPreto;

void setup() {
  Serial.begin(9600);
  pinMode(R, OUTPUT);
  pinMode(G, OUTPUT);
  pinMode(B, OUTPUT);

  pinMode(pino_esq_fora, INPUT);
  pinMode(pino_esq_dentro, INPUT);
  pinMode(pino_dir_fora, INPUT);
  pinMode(pino_dir_dentro, INPUT);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  delay(1000);
}

void loop() {
  unsigned long agora = millis();
  if (agora - memoria >= 20) {
    memoria = agora;
    atualizar_sensores();
  }

  frente();

  if (distancia_ultra < 15) {
    parar();
    delay(100);
    desviar();
  }

  if (dentroPreto == 1) {
    tras();
    delay(20);
    parar();
    atualizar_sensores();
    segue_faixa();
  }
}

void atualizar_sensores() {
  distancia_ultra = calc_ultra();

  sensor_esq_dentro = digitalRead(pino_esq_dentro);
  sensor_dir_dentro = digitalRead(pino_dir_dentro);
  sensor_esq_fora = digitalRead(pino_esq_fora);
  sensor_dir_fora = digitalRead(pino_dir_fora);

  algumPreto = (sensor_esq_dentro == PRETO || sensor_dir_dentro == PRETO ||
                sensor_dir_fora == PRETO || sensor_esq_fora == PRETO);

  algumEsq = (sensor_esq_dentro == PRETO || sensor_esq_fora == PRETO);
  algumDir = (sensor_dir_dentro == PRETO || sensor_dir_fora == PRETO);

  todosPreto = (sensor_esq_dentro == PRETO && sensor_dir_dentro == PRETO &&
                sensor_dir_fora == PRETO && sensor_esq_fora == PRETO);

  todosEsq = (sensor_esq_dentro == PRETO && sensor_esq_fora == PRETO);
  todosDir = (sensor_dir_dentro == PRETO && sensor_dir_fora == PRETO);

  dentroPreto = (sensor_esq_dentro == PRETO || sensor_dir_dentro == PRETO);

  foraPreto = ((sensor_esq_fora == PRETO || sensor_dir_fora == PRETO) && !dentroPreto);
}

float calc_ultra() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  unsigned long tempo = pulseIn(ECHO, HIGH, 20000); // timeout de 20ms
  if (tempo == 0) return 999; // sem obstáculo
  float dist = tempo * 0.034 / 2;
  return dist;
}

void led(int r, int g, int b) {
  analogWrite(R, r);
  analogWrite(G, g);
  analogWrite(B, b);
}

#define sensor_atual sensor_dir_fora

void segue_faixa() {
  atualizar_sensores();

  if (algumDir) {
    if (sensor_esq_fora == PRETO && sensor_esq_dentro == BRANCO) {
      frente();
      delay(150);
    } else if (todosDir) {
      direita();
      delay(1000);
      parar();
    } else if (sensor_dir_dentro == PRETO && sensor_dir_fora == BRANCO) {
      do {
        atualizar_sensores();
        direita();
        delay(300);
      } while (sensor_esq_dentro != PRETO);
      parar();
      delay(150);
    } else if (foraPreto) {
      frente();
      delay(400);
    }
  } else if (algumEsq) {
    if (sensor_esq_fora == PRETO && sensor_esq_dentro == BRANCO) {
      frente();
      delay(150);
    } else if (todosEsq) {
      esquerda();
      delay(850);
      parar();
    } else if (sensor_esq_dentro == PRETO && sensor_esq_fora == BRANCO) {
      do {
        atualizar_sensores();
        esquerda();
        delay(200);
      } while (sensor_dir_dentro != PRETO);
      parar();
      delay(150);
    } else if (foraPreto) {
      frente();
      delay(400);
    }
  }
}