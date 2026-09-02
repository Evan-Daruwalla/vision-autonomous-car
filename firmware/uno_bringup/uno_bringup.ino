/* Bring-up test for the Uno R3 clone (FTDI FT232RL, COM3).
 *
 * NOT stock Blink on purpose. Clones frequently ship with the factory Blink
 * already flashed, so a 1 Hz LED proves nothing about whether OUR upload
 * worked. Two things make this unambiguous:
 *   1. a distinctive pattern -- 3 fast blinks, then a long pause
 *   2. a serial heartbeat, so success is READ, not eyeballed
 */
const unsigned long BAUD = 115200;
unsigned long n = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(BAUD);
  delay(200);
  Serial.println(F("UNO-BRINGUP-OK build=2026-09-02 pattern=3fast+pause"));
  Serial.print(F("F_CPU=")); Serial.println(F_CPU);
}

void loop() {
  for (int i = 0; i < 3; i++) {        // 3 fast blinks
    digitalWrite(LED_BUILTIN, HIGH); delay(120);
    digitalWrite(LED_BUILTIN, LOW);  delay(120);
  }
  Serial.print(F("tick ")); Serial.println(n++);
  delay(900);                          // long pause -- the giveaway
}
