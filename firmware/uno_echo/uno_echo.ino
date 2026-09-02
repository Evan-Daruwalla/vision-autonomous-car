/* Echo one byte back as fast as possible, to measure host<->board round trip.
 *
 * WHY: the Pi sends a command every 50 ms (20 Hz, SIM_TRANSFER_SPEC). If the
 * USB bridge sits on the reply, that delay is inside the control loop. The
 * FTDI FT232RL holds a SHORT packet for up to its LatencyTimer (16 ms default,
 * confirmed in the registry) before shipping it -- and a control reply is
 * exactly a short packet, so this is the worst case, not the average one.
 *
 * The sketch adds as close to zero as possible: no delay, no println, no
 * formatting. What is left is USB out + ~microseconds of AVR + USB back.
 */
void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    Serial.write((uint8_t)Serial.read());   // echo, no newline, no flush
  }
}
