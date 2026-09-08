#include <Arduino.h>
#include <string.h>

constexpr uint8_t ENC_L=2, ENC_R=3, AIN2=4, AIN1=5, STBY=6, BIN1=7, BIN2=8, PWMB=9, PWMA=11;
constexpr uint8_t STX=0xAA, ETX=0x55, CMD_VEL=0x01, ENCODER=0x02, ACK=0x03;
constexpr uint8_t MAX_PAYLOAD=32;
volatile int32_t ticks_l=0, ticks_r=0;
volatile int8_t direction_l=0, direction_r=0;
uint8_t rx[37], rx_index=0, expected=0;
unsigned long last_command=0, last_encoder=0;

void pulseL(){ ticks_l += direction_l; }
void pulseR(){ ticks_r += direction_r; }

void drive(uint8_t pwm,uint8_t in1,uint8_t in2,int16_t rpm,volatile int8_t &direction){
  rpm=constrain(rpm,-120,120); direction=(rpm>0)-(rpm<0);
  digitalWrite(in1,rpm>0); digitalWrite(in2,rpm<0);
  analogWrite(pwm,map(abs(rpm),0,120,0,255));
}
void stopMotors(){ drive(PWMA,AIN1,AIN2,0,direction_l); drive(PWMB,BIN1,BIN2,0,direction_r); }

void sendPacket(uint8_t type,const uint8_t *payload,uint8_t length){
  uint8_t checksum=type^length; Serial.write(STX); Serial.write(type); Serial.write(length);
  for(uint8_t i=0;i<length;i++){ Serial.write(payload[i]); checksum^=payload[i]; }
  Serial.write(checksum); Serial.write(ETX);
}
void applyFrame(){
  uint8_t length=rx[2], checksum=0;
  for(uint8_t i=1;i<3+length;i++) checksum^=rx[i];
  if(rx[3+length]!=checksum || rx[4+length]!=ETX) return;
  if(rx[1]==CMD_VEL && length==5){
    int16_t left,right; memcpy(&left,rx+3,2); memcpy(&right,rx+5,2);
    drive(PWMA,AIN1,AIN2,left,direction_l); drive(PWMB,BIN1,BIN2,right,direction_r);
    last_command=millis(); sendPacket(ACK,rx+7,1);
  }
}
void readSerial(){
  while(Serial.available()){
    uint8_t b=Serial.read();
    if(rx_index==0){ if(b==STX) rx[rx_index++]=b; continue; }
    rx[rx_index++]=b;
    if(rx_index==3){ if(rx[2]>MAX_PAYLOAD){rx_index=0;continue;} expected=rx[2]+5; }
    if(expected && rx_index==expected){ applyFrame(); rx_index=0; expected=0; }
  }
}
void setup(){
  Serial.begin(115200);
  pinMode(ENC_L,INPUT_PULLUP); pinMode(ENC_R,INPUT_PULLUP);
  const uint8_t output_pins[] = {AIN1,AIN2,STBY,BIN1,BIN2,PWMA,PWMB};
  for(uint8_t i=0;i<sizeof(output_pins);i++) pinMode(output_pins[i],OUTPUT);
  digitalWrite(STBY,HIGH); stopMotors();
  attachInterrupt(digitalPinToInterrupt(ENC_L),pulseL,RISING);
  attachInterrupt(digitalPinToInterrupt(ENC_R),pulseR,RISING);
  last_command=millis();
}
void loop(){
  readSerial(); unsigned long now=millis();
  if(now-last_command>500) stopMotors();
  if(now-last_encoder>=20){
    last_encoder=now; noInterrupts(); int32_t l=ticks_l,r=ticks_r; interrupts();
    uint8_t payload[8]; memcpy(payload,&l,4); memcpy(payload+4,&r,4);
    sendPacket(ENCODER,payload,8);
  }
}
