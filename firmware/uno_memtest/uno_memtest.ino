/* Measure what the chip ACTUALLY has -- do not trust compile-time constants.
 *
 * WHY: avrdude reports signature 1E 95 0F as "ATmega328P, ATA6614Q,
 * LGT8F328P". The signature does NOT uniquely identify the part, and the
 * LGT8F328P is a different core that can run at 32 MHz. `F_CPU` is a macro the
 * BUILD supplies, not something the chip reports, so it proves nothing about
 * the silicon.
 *
 * Three real measurements:
 *   1. usable SRAM, by malloc'ing until the allocator refuses
 *   2. free SRAM, from the gap between heap end and stack pointer
 *   3. a timing beacon, so the HOST compares the chip's second against the wall
 *      clock -- which is what actually catches a 32 MHz part on a 16 MHz build
 *
 * The report REPEATS every 10 beacons on purpose. Printing it only in setup()
 * means any capture that starts late misses it entirely, and the board does not
 * reliably reset when the port is opened.
 */
#include <avr/io.h>
#include <avr/boot.h>
#include <stdlib.h>

extern char *__brkval;
extern char __heap_start;

int freeRam() {                       // gap between heap top and stack pointer
  char top;
  return __brkval ? &top - __brkval : &top - &__heap_start;
}

int g_mallocBytes = -1, g_blocks = -1, g_freeBefore = -1, g_freeAfter = -1;

void probeSram() {
  g_freeBefore = freeRam();
  const int BLK = 32;
  static void *blocks[64];            // static: 128B in .bss, NOT on the stack
  int n = 0;
  while (n < 64) {
    void *q = malloc(BLK);
    if (!q) break;
    blocks[n++] = q;
  }
  g_blocks = n;
  g_mallocBytes = n * BLK;
  for (int i = 0; i < n; i++) free(blocks[i]);
  g_freeAfter = freeRam();
}

void report() {
  Serial.println(F("== UNO MEMTEST =="));
  Serial.print(F("SIGNATURE = "));
  Serial.print(boot_signature_byte_get(0), HEX); Serial.print(' ');
  Serial.print(boot_signature_byte_get(2), HEX); Serial.print(' ');
  Serial.println(boot_signature_byte_get(4), HEX);
  Serial.print(F("F_CPU (compile-time, NOT measured) = ")); Serial.println(F_CPU);
  Serial.print(F("RAMEND (compile-time) = 0x")); Serial.println(RAMEND, HEX);
  Serial.print(F("SRAM total implied by RAMEND = "));
  Serial.println((long)RAMEND - 0x100 + 1);
  Serial.print(F("MEASURED malloc'd = ")); Serial.print(g_mallocBytes);
  Serial.print(F(" B in ")); Serial.print(g_blocks); Serial.println(F(" x 32B"));
  Serial.print(F("MEASURED freeRam before/after = "));
  Serial.print(g_freeBefore); Serial.print('/'); Serial.println(g_freeAfter);
  Serial.println(F("== BEACON =="));
}

unsigned long k = 0;
void setup() {
  Serial.begin(115200);
  delay(200);
  probeSram();
  report();
}

void loop() {
  if (k % 10 == 0 && k > 0) report();
  Serial.print(F("beacon ")); Serial.print(k++);
  Serial.print(F(" millis=")); Serial.println(millis());
  delay(1000);
}
