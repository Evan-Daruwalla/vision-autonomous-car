/* servo_bench -- measure the HOOYIJ MG90D-270's real pulse-to-angle map and
 * its end-of-travel pulses. A bench MEASUREMENT sketch, like uno_bringup --
 * NOT the car firmware. Re-flash uno_control afterwards.
 *
 * Serial Monitor at 115200, line ending "Newline": type a pulse width in
 * microseconds (400-2600) and Enter; 'c' re-centres to 1500. The sketch echoes
 * what it commanded.
 *
 * attach() gets explicit 400-2600 limits ON PURPOSE: with no limits the Servo
 * library clamps every pulse to 544-2400 us, which would hide both ends of a
 * 500-2500 us servo (record Appendix FI) -- the very thing being measured.
 *
 * Wiring: signal D9, V+ to the Uno 5V pin, GND to GND. UNLOADED servo only
 * (horn free, not on the rack): the Uno's USB 5 V rail sits behind a 500 mA
 * polyfuse and is not sized for a stalled servo.
 */
#include <Servo.h>

const uint8_t PIN_SERVO = 9;
const int US_MIN = 400, US_MAX = 2600;

Servo servo;
char line[8];
uint8_t n = 0;

void go(int us) {
  if (us < US_MIN) us = US_MIN;
  if (us > US_MAX) us = US_MAX;
  servo.writeMicroseconds(us);
  Serial.print(F("-> ")); Serial.print(us); Serial.println(F(" us"));
}

void setup() {
  Serial.begin(115200);
  servo.attach(PIN_SERVO, US_MIN, US_MAX);
  Serial.println(F("== SERVO BENCH == type us (400-2600) + Enter, c = centre"));
  go(1500);
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == 'c') { go(1500); n = 0; }
    else if (c >= '0' && c <= '9' && n < sizeof(line) - 1) line[n++] = c;
    else if ((c == '\n' || c == '\r') && n) { line[n] = 0; go(atoi(line)); n = 0; }
  }
}
