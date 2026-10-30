# hardware-power.md - pack, BMS, charger, LM2596, power distribution, fuse, current limits, driver/motor current (split from hardware.md on 2026-10-29)
Moved verbatim from hardware.md, original relative order; router is hardware.md. Entries dated 2026-07-23 are desk research unless marked verified.
Cross-topic facts live in the file that fit best; check the sibling hardware-*.md files too.

- ~~**Pi 5 will not get 5V/5A from standard USB-PD** … Battery path is 2S
  LiPo → 5V/5A-class UBEC → 5V GPIO pins … Never a phone power bank.~~
  **(supersedes the 2026-07-23 ~16:17 entry — the CONSEQUENCE was wrong.)**
  Corrected 2026-07-23 ~17:59 (verified verbatim against official docs):
  the Pi 5 accepts **"5 V at 3 A (15 W) with a 600 mA peripheral limit"**.
  The 5 A rating is a **USB-peripheral budget, not a board requirement**,
  and the only documented consequence of a 3 A supply is that USB cap —
  **irrelevant here, since this build has no USB peripherals** (CSI camera
  only). Measured Pi 5 draw under CNN inference is **1.40 A**; all-core
  stress ~1.76 A. A USB power bank IS viable for the Pi.
- **The real Pi 5 power constraint is transient rail stiffness, not
  amperage.** A documented Pi 5 shut down at only ~1.5 A because of voltage
  drop in "5 A-rated" cables, and another got undervoltage warnings through
  a bench-tested 5 A buck due to transients a DC load never catches. Short
  thick cables; bulk capacitance at the Pi end if a regulator is ever in its
  path (2026-07-23).
- **NEVER put the Pi and the motor on one 5V/3A power bank.** Simultaneous
  Pi peak (2.32 A) + servo stall (0.70 A) + motor stall (1.6 A) = **4.62 A
  on a 3 A rail** → current limit, rail collapse, Pi hard-reset mid-run with
  the SD card mounted. Average draw (~2 A) is fine; the stall event is the
  killer. Split source is the design: bank → Pi only; 2S pack → motor +
  servo; **one shared ground**, star-grounded at the driver (2026-07-23).
- **Don't set `PSU_MAX_CURRENT=5000`** on this build — with no USB
  peripherals it enables nothing and only removes a brownout guardrail
  (2026-07-23).
- **Parallel BOTH TB6612FNG channels** (AIN1+BIN1, AIN2+BIN2, AO1+BO1,
  AO2+BO2) for 2 A continuous — steering is a servo, so the second channel
  is free. Also **PWM-cap duty at ~71%** of a full 8.4V pack so the 6V motor
  sees ≤6V, and add a firmware stall-timeout (2026-07-23).
- **Raspberry Pi Build HAT is rejected** (2026-07-23, both facts verified
  directly): it needs **8V ±10% (7.2-8.8V) at 48W via a barrel jack** — a
  2S pack is below that for most of its discharge — and it reserves **GPIO
  0/1/4/14/15/16/17** including the primary UART. It is also **not
  supported on Raspberry Pi OS Trixie** (official docs say stay on
  Bookworm), and no rpm/torque data is published for Lego 88013/88014
  anywhere, so their gearing can't be designed on paper.
- **Evan owns NO battery and NO charger** (confirmed 2026-07-23 ~17:32 CDT).
  The 2S-LiPo plan assumed equipment that doesn't exist; the complete power
  system (cells + charger + connectors) is an unbudgeted purchase and is
  under research as PRD M1.1c. Budget is projected over the $200 ceiling as
  a result.
- **Do not power the Uno from the 7.4V pack's VIN.** The pack sags under motor
  stall; if VIN falls below ~7V the AMS1117 regulator drops out and the Uno
  browns out MID-DRIVE, taking the servo and the watchdog with it. ~~Feed its 5V
  pin from the LM2596 rail and use a **data-only USB cable** (5V wire cut) so
  the two supplies cannot back-feed each other.~~ **(2026-10-29) the Uno runs on the Pi's USB; +5V2 feeds only the strips + encoder; servo V+ on the Uno 5V via JP1 (records JF, JR)**
- ~~**The 2S pack has no HARDWARE over-discharge protection** (Appendix BI).~~ **SUPERSEDED: the ACEIRMC BMS (2.9 V cutoff) is in the circuit since the 2026-10-10 redraw (Appendices CK/FE); the firmware latch below is a soft layer above it. Kept as history:** BOM
  row 11's "BMS" documents over-voltage and short-circuit only, and the EVE
  cells are bare. `firmware/uno_packguard/` implements a latched firmware cutoff
  (warn 6.4 V, cut 6.0 V held 500 ms, fault outside 4.0-8.8 V, CLEAR needs
  6.8 V) - **but firmware cannot guard a pack while the firmware is off.** It
  supplements a protection board; it does not replace one.
- **Measure the pack against the internal 1.1 V band gap, never the 5 V rail.**
  ~~The Uno's 5 V comes from the LM2596~~ **(2026-10-29: superseded - the Uno's 5 V now comes from the Pi's USB, records JF/JR; the band-gap advice below still holds, its premise changed)** - the same supply that sags when the pack
  sags - so a rail-referenced reading lies exactly when it matters.
## A CHARGER IS NOT A BMS — the category error that kept a safety hole open (2026-09-03, Appendix CK)

- **A charge board cannot give you over-discharge protection, and no amount of
  shopping fixes that.** A charger IC terminates *charge*: it sits on the INPUT
  side and has **no discharge-path FET to open**. Over-discharge cutoff requires
  per-cell sensing and a **series FET on the pack OUTPUT** — structurally a
  BMS's job. `docs/BOM.md` row 11 asked one board to do both, and the hole it
  left stayed open from Appendix BI (2026-09-02) until this was understood.
  **The part was never missing; the requirement was aimed at the wrong part.**
- **The fix is two boards in series**, not a better single board: a USB-C
  charger (Adeept p0374, $7.99) **plus** a 2S BMS wired BETWEEN the charger and
  the pack (ACEIRMC 2S 8A, $9.59, documented cutoff **2.9 V ±0.05 V**). Once the
  BMS owns over-discharge, the charger's silence on it stops being a defect.
- **Verified negative worth keeping: NO established hobby vendor sells a 2S
  USB-C board documenting an over-discharge cutoff.** Adafruit, SparkFun,
  Pololu, Seeed, Waveshare, TinyCircuits and CanaKit have no 2S protection part
  at all. This is a structural absence, not a stock problem — stop looking.
- ⚠️ **Web-search summaries LIE about this specific part class.** Two separate
  searches returned text asserting these Type-C 2S modules "include
  over-discharge protection"; **the live pages contradict it** — the strings
  "over-discharge", "low voltage" and "under-voltage" appear nowhere on the
  Adeept page. The whole AITIAO/HiLetgo/Adeept family shares the same copy, so
  buying a different brand of the same board changes nothing. **Read the vendor
  page, never the snippet, for a protection claim.**
- ⚠️ **Cell C-ratings are routinely inflated on retail listings.** Reject Vapcell
  Z30's *"50A continuous"* (no 18650 chemistry sustains that; the listing's own
  5 mΩ implies ~12.5 W of self-heating) and Orbtronic's VTC6 *"30A"* (Murata's
  design CDR is **15 A**; 30 A is the 80 °C temperature-limited number). Prefer a
  cell whose headline is an **unqualified datasheet continuous rating** — the
  Samsung 25R's 20 A is one.
- **2026-10-04: a SECOND BMS listing nearly shipped, the same snippet-vs-page
  failure one level up.** Evan's cart held ACEIRMC `B08CV2VS8G` (5-pack, $8.99),
  not row 11b's vetted `B08HLQQCQJ`. Its spec documents overcurrent (~10 A),
  short-circuit and a discharge-side MOSFET - so unlike the Adeept charger above
  it IS the right KIND of part, with the series FET - but it publishes **NO
  over-discharge or overcharge voltage set point**. A BMS with an undocumented
  cutoff cannot satisfy `important.md` #4. Row 11b stays on `B08HLQQCQJ` ~~until
  Evan confirms which one he ordered~~ - **resolved the same day: Evan is
  ordering `B08HLQQCQJ`**, re-verified live in a browser (8PCS, $9.59, In
  Stock, "Overdischarge detection voltage: 2.9V+/-0.05V.").
- **The set point lives in the listing's DESCRIPTION, not its bullets.** The
  vetted part's bullets say only "Over-discharge protection" - exactly what
  `B08CV2VS8G` said. A bullets-only check cannot tell the good board from the
  bad one; scroll to the description.
- **The BMS is not in the wiring doc (found 2026-10-04).** It was added to the
  BOM on 2026-09-03 (Appendix CK), but `docs/WIRING_PROTOSHIELD.md`'s net list
  was never redrawn - `PACK+` still runs holder -> fuse. Wiring from it would
  bypass the over-discharge cutoff entirely. Rule from the board's own pinout:
  pack to **B+ / B- / MB**, everything else (charger included) to **P+ / P-**.
  **MB needs the cell midpoint**, which the 2-lead DIANN holder does not
  expose - solder a third wire to its internal series strap. ~~Net redraw is open.~~
  **Redrawn 2026-10-10** (WIRING_PROTOSHIELD.md section 2.1): cells -> 3 A fuse
  -> B+ (fuse on the cell side, Evan's call), charger on P+ / P-, PACK- = P-.
- **Cheap 2S BMS boards ship LOCKED.** That listing: boards "need to be charged
  and activated before output... otherwise the circuit is locked." A freshly
  soldered board can read ZERO output and look dead. **Before meter-probing a
  "dead" BMS, connect the charger once to activate it.** Recorded from the
  `B08CV2VS8G` listing; whether `B08HLQQCQJ` behaves the same is unverified -
  assume it might.
- **Series resistance "less than 300 mOhm"** (same listing) is an upper bound
  and real boards usually measure far lower. At row 11b's ~2.5 A worst case it
  would be 0.75 V of drop and ~1.9 W on a small PCB, sagging the pack
  7.4 -> 6.65 V. That leaves ~1.65 V above the ~~5.20 V~~ 5.00 V rail (set point lowered 2026-10-11); whether that clears
  the LM2596's dropout at load is UNVERIFIED (the 2026-10-04 review called it
  headroom - check the module's datasheet, and see the rail-sag note above on
  the 5 V supply sagging as the pack drains; at the BMS cutoff, 2 x 2.9 V =
  5.8 V, only 0.8 V remains at 5.0 V - 0.6 V at the old 5.2 V). Measure the board on arrival; not a reason to
  reject it.
- **Holder substitute (row 10), 2026-10-04:** the Addicore holder was
  backordered; the DIANN `B0BJV9ZL3J` replacement's title says "2 Slots 3.7V".
  ~~**SERIES vs PARALLEL is unverified**~~ **SERIES per the listing** (Evan
  pasted it 2026-10-04: "Output Voltage: 7.4V", 2 cells, one red + one black
  lead, 7.6 x 4.0 x 1.9 cm, 13 cm leads). The copy is unreliable - it also says
  "AAA", and "Parallel or Series ... depending on how you set it up", which
  reads as combining several holders. **Meter it before wiring:** two charged
  cells read ~7.4-8.4 V across red/black in series, ~3.7-4.2 V in parallel; a
  parallel holder breaks 2S / 7.4 V, so reject it. Visual tell: in a 2-cell
  series holder the cells typically sit head-to-tail with a strap at one end.
  Lead gauge is not stated, and those leads carry full pack current upstream
  of the 3 A fuse.
- **TP5100-based chargers cannot be used here**: they are buck chargers needing
  9–12 V in, so 5 V USB-C cannot drive them.
- **Practical constraints on buying cells:** USPS caps lithium at **8 cells per
  package**; battery sales are typically **final** (5-day DOA window only); and
  IMR Batteries and 18650BatteryStore appear to be the same operation — not two
  independent sources for redundancy.

## Search snippets lie about purchase-critical facts — TWICE in one session (2026-09-03, CK/CL)

- **Read the vendor page, never the search summary, for any claim you would spend
  money or safety on.** Two independent instances on 2026-09-03:
  1. Summaries asserted Type-C 2S charge modules "include over-discharge
     protection". **The live pages contradict it** — the strings
     "over-discharge", "low voltage" and "under-voltage" appear nowhere.
  2. A snippet claimed DigiKey gives free shipping over $50. It traces to
     `digikey.com/en/help/set-rate-shipping/`**`th`** — **the THAILAND page.**
     Verified US shipping is **$4.99 USPS Ground Advantage and up, no threshold.**
- **Two instances in one session is a pattern, not bad luck.**
- **A distributor relationship does not imply consolidation.** DigiKey is an
  authorized distributor for Adafruit, SparkFun and Pololu, yet the Pololu parts
  are **DigiKey MARKETPLACE, not DigiKey inventory**: *"Will ship in
  approximately 1 days from Pololu. A separate shipping fee may apply."* A second
  parcel and a second shipping charge — check who actually SHIPS the item.
- **DigiKey stocks no high-drain 18650** — their cells top out at a **520 mA**
  continuous rating. Distributor breadth does not extend to power cells.

- 2026-10-14 (records IP-IT): the 2S holder's strap is not reachable inside; its MB node is the brass star rivet on the end WITHOUT the leads (metered: 3.55 V to each lead). MB wire SOLDERED to the rivet, re-metered 3.55 / 3.55 V; not yet on the BMS. Fuse = 3 A violet ATO (kit holds 3-15 A).
- 2026-10-15 (records IY-JE): pack charged (charger board 1 wired reversed, likely damaged, RETIRED; spare board 2 stopped at 8.29 V; no-load test of board 2 still owed - attend charges). LM2596 set UNLOADED from the pack: 4.95 V (JE), then nudged to 4.99 V on the DT830B (module display reads ~0.05-0.1 V low). Lock state of the pot not recorded.
- **2026-10-30 MEASURED (record LS; CORRECTED in LT): ~~the Anker PowerCore Speed 20000 PD (A1275, 5 V / 3 A at 5 V) + its unrecorded cable SAGS~~ the Pi's CURRENT supply (NOT the Anker bank - LT; source unknown) SAGS** - Pi 5 EXT5V 4.52-4.60 V on 7 of 12 readings under 60 s of all-core load + inference, `get_throttled` 0x50005 (under-voltage and throttling LIVE); 4.91 V idle; the under-voltage flag also trips during boot. ~~So 'a USB power bank IS viable' (above) holds on amperage and FAILS on rail stiffness for this bank+cable. Cable vs bank not separated yet;~~ The bank is untested; the driving-loop load (lighter than all-core) not measured.
- 2026-10-30 (records LT, LU): the Pi's bench supply is a 'battery backup' (model unrecorded; USB-C port label per Evan 2026-10-30: 5V 3A / 9V 3A / 15V 2A - the Pi 5 only uses the 5 V / 3 A step, so it runs at that step's full rating). Through cable + USB-C extension: 7/12 under-voltage readings, low 4.520 V; one cable, no extension: 4/12, low 4.535 V, swinging 4.53-5.07 V under steady load -> the backup's regulation is the likely main cause (inference; no second supply tried). Never feed the Pi through a USB-C extension.
- **2026-10-30 (record LV): RESOLVED for the bench - the battery backup was the cause.** On another USB-C wall charger (identity unrecorded) the same 60 s all-core + inference test held EXT5V 5.11-5.15 V with throttled 0x0 throughout, boot included. Use a wall charger, not the backup, for any Pi measurement. New flag: 77.9 C peak in 60 s (Pi 5 thermal throttle starts at 80 C) - decide a heatsink / Active Cooler for the car.
- 2026-10-30 (record LW): the LV charger negotiates 5 A (usb_max_current_enable=1, max_current 5000 mA) - likely the Vilros 27 W kit PSU (identity unconfirmed). That PSU is the right BENCH supply; BOM row 1's 'unused capacity' note holds only for the car. The 77.9 C was a BARE board (no case/fan, Evan): the kit's metal fan case is the fix, no purchase.
- **2026-10-30 (record LX): the car's planned Pi supply, the Anker A1275 bank, ALSO sags** - 5/12 readings at 0x50005, low 4.539 V, flag at boot, 3 A mode (max_current 3000 -> 600 mA USB cap for Uno + TB6612 logic + servo). Possible confound: same USB-C cable as the backup run. The car's Pi supply is NOT proven until a different-cable bank test passes or a stiffer 5 V source is chosen.
