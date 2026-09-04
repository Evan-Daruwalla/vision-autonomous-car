# Bill of Materials — v1 (2026-07-23)

> **➡️ TO PLACE THE ORDER, READ [ORDER SHEET](#order-sheet--grouped-by-vendor-2026-09-03) BELOW.**
> The row table is the reasoning and the dated history; the order sheet is the
> shopping list, grouped by vendor with SKUs and live stock. Three things block
> it today — they are listed there.

**Status: FINAL pending Evan's order.** Every choice traces to a dated
research brief in `docs/research/`. Prices are 2026-07-23 and were volatile
this year (Pi RAM shortage) — **re-verify at checkout.**

**Decisions this BOM encodes** (Evan, 2026-07-23 ~20:46 CDT):
Pi 5 **4GB** (down from 8GB, −$25) · **owns a USB power bank**, so the
split-source power path costs almost nothing.

---

## The list

| # | Item | Why this one | Price | Source |
|---|---|---|---|---|
| **Compute + sensing** |
| 1 | ~~Raspberry Pi 5 4GB bare board~~ **→ Vilros Basic Starter Kit, 4GB — $179.99** | ✅ **FINAL DECISION 2026-09-03 (Evan): buying the Vilros kit, confirmed IN STOCK by Evan directly reaching checkout** (stronger evidence than the browser check in Appendix CM, whose render failed before confirming Board Only availability). **Kit contents fold into three other BOM rows — do not double-buy:** includes a 32GB Class 10 microSD preloaded with RPi OS (**supersedes row 4**), a metal case with passive+active PWM cooling (**supersedes the Active Cooler line below**), a Vilros 27W 5V/5A USB-C PSU, a Standard-to-Micro HDMI adapter cable, a quickstart guide, a neoprene storage bag, an LIR2032 RTC battery connector, and a **Mini-to-Standard Camera Module Adapter Cable (120mm)** — ⚠️ **UNCONFIRMED whether this covers row 3**: row 3 needs the 22-pin-0.5mm-to-15-pin-1mm FPC cable for Camera Module 3 specifically; the kit's cable is a generic accessory of unconfirmed pin count/pitch and length (120mm vs row 3's 200mm). **Keep row 3 as a separate purchase until the kit cable is physically checked against the camera on arrival.** ⚠️ **The bundled PSU does not fit this project's split-source power architecture** (`docs/research/2026-07-23_power-system.md`: USB power bank feeds the Pi alone) — it is unused capacity, but costs nothing marginal since it ships with the kit either way. Net effect on the BOM: replaces rows 1+4 ($131.95 combined) and the flagged cooler line with one $179.99 purchase — **+$48.04** vs the unbundled parts, buying convenience and one fewer vendor rather than a discount | includes SD card + cooling + PSU + adapters, one box, one shipment | **$179.99** | [vilros.com](https://vilros.com/products/raspberry-pi-5) ✅ **confirmed in stock by Evan, 2026-09-03 — Vilros Basic Starter Kit, 4GB** |
| 2 | Camera Module 3 **Wide** | ✅ **HOLD LIFTED 2026-08-13 (Appendix AI): the sim FOV was identified as `fov=90`, i.e. ~106° H / ~118° diagonal, and the Wide (102° H / 120° D) matches within 2-4°. The standard module is ~40° off and would be wrong. Correct part — by luck, since nobody set or checked it.** Superseded warning: The sim's camera FOV/offset/rotation were NEVER SET (`cam_config` absent from every conf dict), so the whole corpus was captured at an unrecorded Unity default. If it differs from this camera's 120°, the encoder trained on a different projection than this part will produce. One short sim run settles it — see `docs/SIM_TRANSFER_SPEC.md` §5.2. Original rationale: ≥120° FOV is the consensus lever for track following; rolling shutter is fine at 1–3 m/s | **$35.00** at DigiKey | [pishop.us](https://www.pishop.us/product/raspberry-pi-camera-module-3-wide/) ✅ **verified 2026-09-02, in stock** |  ⚠️ **CHEAPER AT DIGIKEY 2026-09-03: SC1224 $35.00, 7,215 in stock** (−$3.50 vs pishop).
| 3 | **Camera cable, Standard-Mini** | ⚠️ **Camera Module 3 ships with a Standard-Standard cable, which does NOT fit the Pi 5's mini 22-pin connector.** Verified against Raspberry Pi docs 2026-07-23. Without this, nothing works. | **$1.00** at DigiKey | ✅ **BUY AT PISHOP WITH THE CAMERA — verified 2026-09-03: "Camera Cable Standard-Mini 200mm V2", SKU 1971-1, $2.95, in stock.** Same vendor as row 2, so it costs no extra freight. Alternatives: [adafruit.com #5818 200mm](https://www.adafruit.com/product/5818) · [#5820 500mm](https://www.adafruit.com/product/5820) — the 22-pin 0.5mm to 15-pin 1mm FPC cable |  ⚠️ **CHEAPEST AT DIGIKEY 2026-09-03: SC1892 $1.00, 3,728 in stock — a THIRD of pishop's price**, on the very part this BOM was written to catch.
| 4 | ~~microSD card, 32GB+, A2/U3~~ **SUPERSEDED 2026-09-03 — included in the row 1 Vilros kit** (32GB Class 10, preloaded with RPi OS). ⚠️ Class 10 is a lower speed class than the A2/U3 this row originally specified; DonkeyCar logging is not proven to need A2/U3 specifically, so this is a real but unverified downgrade, not a confirmed problem. **$0 marginal cost — do not buy separately** | OS + driving logs, now bundled | **$0.00** *(was $21.95)* | included in row 1 |
| **Drive + steering** |
| 5 | ~~Pololu **#1093** N20 30:1 HP 6V~~ **Pololu #5159 — 30:1 HP 6V *with 12 CPR encoder*, side connector** | The only gear ratio that lands in the required 430–1550 rpm band; full spec sheet + CAD envelope. ⚠️ **CORRECTED 2026-09-02 (Appendix BO): this row listed #1093, which has NO ENCODER — but Evan chose the encoder variant on 2026-08-12 (Appendix O) and the firmware pin map has spent D2/D3 on encoder interrupts ever since. The BOM was buying a motor that could not feed the design.** Verified 2026-09-02: 29.86:1, 1000 rpm no-load, **1.6 A stall**, 0.57 kg·cm stall torque, encoder Vcc 2.7–18 V with internal 10k pull-ups, 12 CPR at the motor shaft = **~358 counts/output rev** | **$29.95** | [pololu.com/product/5159](https://www.pololu.com/product/5159) ✅ **verified 2026-09-02, $29.95, in stock** |
| 5b | **Pololu #4763** JST SH encoder cable, 6-pin, single-ended female, 30 cm | ⚠️ **NEW ROW 2026-09-02 (Appendix BO). Pololu states plainly that "cables are not included"** with #5159, and the encoder connector is **6-pin JST SH at 1.0 mm pitch — not hand-solderable to 0.1" protoboard**. Without this, the encoder cannot be connected at all. *Same class of defect as row 3, the camera cable — an omitted mating cable that stops the build dead.* Single-ended is the right variant: JST connector one end, bare wires to solder at the other | **$3.00** | [pololu.com/product/4763](https://www.pololu.com/product/4763) ✅ **verified 2026-09-02, $3.00** |
| 6 | Pololu **#713** TB6612FNG carrier | MOSFET bridge, ~0.5V drop, 4.5–13.5V. **Parallel both channels** for 2A continuous. ⚠️ **`STBY` MUST be driven high or the driver never leaves sleep** — Pololu: *"pulled low internally … must be driven high (2.7 V – 5.5 V) in order to enable the driver."* Omitted from this BOM and from the pin map until **2026-09-02 (Appendix BL)**; now **D10**. **Paralleling = tie AIN1↔BIN1, AIN2↔BIN2, PWMA↔PWMB on the input side and AO1↔BO1, AO2↔BO2 on the output side** — forced here rather than merely tidy, because there is ZERO spare PWM to drive the B channel separately. *Pololu states the 2 A paralleled rating but does NOT document the method; the pin pairing above is standard practice, unverified against Toshiba — confirm before soldering.* | **$4.95** | [pololu.com/product/713](https://www.pololu.com/product/713) ✅ **verified 2026-09-02, $4.95 unchanged** |
| 7 | MG90S metal-gear servo | Steering. Metal gears non-negotiable. ✅ **Its 180° travel is an EXACT 1:1 match to the measured 180° pinion sweep** (Evan, 2026-09-02) — no gearing, luck rather than design. ⚠️ **The MG996R "fallback if it stalls" is now a LIABILITY, not a safety net** (2026-09-02, Appendix BV): at ~1079 mN·m stall it puts the servo-to-pinion coupler at **SF 0.12–0.19**, against the MG90S's already-failing 0.57–0.96. Stalling harder is what shears the joint downstream — if the MG90S stalls, fix the travel limit (row 22) and the centring, not the servo. ⚠️ **MG90S pulse range varies by unit** (some 500–2400 µs for 180°, not 1000–2000): confirm the real endpoints on the bench before commanding full lock | **$7.99** (2-pack) | [amazon.com/dp/B09KXM5L7Z](https://www.amazon.com/Replace-Helicopter-Airplane-Controls-Vehicle/dp/B09KXM5L7Z) ✅ verified 2026-09-03, In Stock, metal gear stated in title, Amazon's Choice |
| **Power (split source — bank owned)** |
| 8 | USB power bank, **5V/3A** | → Pi ONLY. **You own this — check the label says 5V/3A** (see Verify below) | **$0.00** | owned |
| 9 | ~~2× EVE 25P 18650 cells~~ **→ 2× Samsung 25R, $4.99 each = $9.98** | ⚠️ **EVE 25P CONFIRMED SOLD OUT 2026-09-03** (page shows only "Notify me when back in stock"; also sold out at IMR). **Replacement verified in stock: Samsung 25R** — 2500 mAh, page states *"Continuous Discharge Rating 20A"*, **Flat Top, "Protected: No"**. Chosen because its headline is an **unqualified datasheet continuous rating with no thermal asterisk** — the only one of six that is. Alternatives, all in stock and all fine against the real ~2.5 A draw: **Molicel P30B** 3000 mAh $5.50 (Liion Wholesale, cheapest tier-1 found) · **Molicel P26A** 2600 mAh/35 A $5.99 (IMR) · **EVE 30P** $4.99 · **Samsung 30Q** $6.99. ⚠️ **Marketing vs datasheet — REJECT these:** Vapcell Z30 *"50A continuous"* (no 18650 chemistry sustains 50 A; its own 5 mΩ implies ~12.5 W self-heating) and Orbtronic's VTC6 at 30 A (Murata's design CDR is **15 A**; 30 A is the 80 °C temperature-limited figure). ⚠️ **USPS caps lithium at 8 cells/package**, and **all battery sales are final** (5-day DOA window only). Note IMR and 18650BatteryStore are almost certainly the same operation — not two independent sources | **$9.98** | [imrbatteries.com Samsung 25R](https://www.imrbatteries.com/products/samsung-25r-18650-2500mah-20a-battery) ✅ in stock 2026-09-03 |
| 10 | 2-cell 18650 series holder | | **$1.25** | [addicore.com 2-place 18650 holder ⚠️ **BACKORDERED 2026-09-03**](https://www.addicore.com/products/2-place-18650-battery-holder-with-wires) — price NOT re-verified |
| 11 | **USB-C 2S charge board — Adeept p0374** (CHARGER ONLY, see row 11b) | ✅ **THE SAFETY HOLE IS CLOSED, AND IT WAS A CATEGORY ERROR IN THIS BOM, NOT A SOURCING GAP** (2026-09-03, Appendix CK). This row asked ONE board to both charge and protect. **No such board exists at any established vendor — structurally.** A charger IC terminates *charge*: it sits on the input side and has no discharge-path FET to open. Over-discharge cutoff needs per-cell sensing and a **series FET on the pack output** — that is a BMS's job. **We were looking for the feature in the wrong part.** p0374 keeps its role as the USB-C charger; its missing over-discharge claim **stops mattering once it is no longer the part responsible for it.** Re-verified 2026-09-03: the page says only *"over voltage protection"* and *"short circuit"* — the strings "over-discharge", "low voltage" and "under-voltage" appear **nowhere**. ⚠️ **Two web-search summaries ASSERTED these modules have over-discharge protection; the live pages contradict them** — exactly the failure a snippet-based check produces | **$7.99** | [adeept.com p0374](http://www.adeept.com/li-ion-battery-charger-m-2s2a_p0374.html) |
| **11b** | **2S BMS protection board — ACEIRMC 2S 8A (sold as an 8-PACK)** ⚠️ **CORRECTED 2026-09-03: $9.59 buys 8 BOARDS, not 1** — checked live on the Amazon listing after Evan asked. The build needs exactly one; **the other 7 are spares**, which matters here specifically because Appendix CK found NO vendor reliably stocks a 2S BMS with a documented over-discharge cutoff — a spare on hand beats a second multi-week sourcing search if one board fails or is damaged soldering it in. No single-unit listing exists on this page; the smallest pack offered is 5-for-$8.59, so the 8-pack is also the better per-unit price ($1.20/board vs $1.72/board). | **This is what closes BOM Verify item 6, open since Appendix BI.** Page states a **single tight set point**, not a range: *"Overdischarge detection voltage: 2.9V+/-0.05V"*, plus *"Overcharge protection, over discharge protection, short circuit protection, overcurrent protection"* and 8 A continuous — comfortably over the ~2.5 A worst-case draw. Chosen over ElectronicNova 2S 10A ($7.11, cutoff given as a 2.82–2.98 V **range**) and ABRA `BAT-C-2S-BMS` ($4.99, 3.0 V ±0.1 V) for the tightest documented cutoff. **Wire it BETWEEN the charger and the pack.** Optional third layer: Pololu #2868 ($13.95, 60 in stock) has a user-set low-voltage cutoff — set it ABOVE the BMS trip so the BMS latching off is the failure you never reach. ⚠️ **Do NOT use TP5100-based boards** — they are buck chargers needing 9–12 V in, so 5 V USB-C cannot drive them | **$9.59** | [amazon.com/dp/B08HLQQCQJ](https://www.amazon.com/dp/B08HLQQCQJ) ✅ in stock 2026-09-03, 8-pack |
TLS" — **wrong**: the https URL resolves with a valid certificate; only the
apex adeept.com downgrades. Corrected 2026-09-02, Appendix BK)* |
| 12 | LM2596 buck module | 7.4V → 5.2V for the servo only (700mA peak — well within it). **Not for the Pi** | **$2.48** | [addicore.com LM2596 ⚠️ **BACKORDERED 2026-09-03**](https://www.addicore.com/products/lm2596-step-down-adjustable-dc-dc-switching-buck-converter) — price NOT re-verified |
| **Wiring + protection** |
| 13 | XT30 connector pair | | **$1.10** | [alofthobbies.com/products/xt30-plugs](https://alofthobbies.com/products/xt30-plugs) ✅ **verified 2026-09-02: $1.10, ONE male+female pair, genuine Amass, in stock** |
| 14 | ~~SPST rocker switch, 10A~~ **SUPERSEDED 2026-09-03 — see the Amazon-folded order below** | Main switch on the motor pack. Evan asked to right-size the Amazon bulk-pack items; SparkFun's single-unit price was fine but meant a 4th vendor for one $0.75 part (the old "small-order problem" this BOM already solved once in Appendix CP) | **$6.39** (5-pack) | [DaierTek KCD1 5-pack](https://www.amazon.com/dp/B07S1MV462) ✅ verified 2026-09-03, In Stock, Amazon's Choice, 12V DC/automotive rated (closer match than SparkFun's 125VAC household spec), pre-wired, 4.7★ (3,586 ratings) |
| 15 | ~~Inline ATO/ATC fuse holder + 3A fuse~~ **SUPERSEDED 2026-09-03 — see the Amazon-folded order below** | **Mandatory** — unprotected 18650s can deliver enormous short-circuit current. The CAD-currency cross-border problem this row used to flag is gone — right-sizing the Amazon fuse holder (Appendix CP) already fixed it once; this is a further size cut on the SAME US listing family | **$7.99** (4 holders + 20 fuses, 3A-15A) | [Anyongora 4-pack](https://www.amazon.com/dp/B0F6NPV287) ✅ verified 2026-09-03, In Stock, Amazon's Choice, IP67 waterproof, 16AWG pre-wired leads, confirmed 3A included, 4.9★ (109 ratings) |
| 16 | Wire, heat-shrink, bulk caps, headers | ~22AWG for motor, ~26AWG signal; 470–1000µF across the motor rail **+ 0.1 µF ceramic across the motor terminals for brush noise, and 0.1 µF at the TB6612 VM/GND** (added 2026-09-02 — `docs/WIRING_PROTOSHIELD.md` §2.2 flagged both as missing from this row) | **$49.09** | [Fermerry 22 AWG wire, 6×5ft](https://www.amazon.com/Fermerry-Stranded-Silicone-Flexible-Electrical/dp/B089D29FHC) $9.69 · [SCHDRA 26 AWG wire, 6×20ft](https://www.amazon.com/Silicone-Electrical-SCHDRA-Tinned-Copper/dp/B0C9MB4DTY) $9.99 · [KOOWIN heat-shrink, 720pc/8 sizes](https://www.amazon.com/Shrink-Tubing-Tubes-KOOWIN-Ratio/dp/B098LB9LTJ) $7.99 · [470µF 25V caps, 10-pack](https://www.amazon.com/Projects-Radial-Electrolytic-Capacitor-470uF/dp/B0CPTDPG6S) $7.07 · [0.1µF ceramic caps, 50-pack](https://www.amazon.com/BOJACK-Capacitors-Low-Voltage-Dielectric-Capacitor/dp/B07X5XTDPB) $6.99 · [40-pin 0.1" headers, 20-pack](https://www.amazon.com/Straight-Breakaway-Connector-Breadboard-Electronic/dp/B0FRZW75VS) $6.29 — ✅ all verified 2026-09-03, In Stock |
| **Lighting + I/O** |
| 17 | ~~**PCA9685** 16-ch I2C PWM/LED driver~~ **Arduino Uno R3 clone — OWNED** | ✅ **SUPERSEDES the PCA9685 2026-09-02 (Appendix BC).** Evan has an Uno R3 clone on hand: ATmega328P, 5V logic, FTDI FT232RL, working on COM3. It does everything the PCA9685 would (motor PWM + servo + 4 light channels, fits with **ZERO** PWM spare — corrected 2026-09-02 (Appendix BH): Servo takes Timer1 (kills D9/D10) and the encoder takes D3, leaving usable PWM {5, 6, 11}, all three consumed by motor + headlights + tail) **plus two things the PCA9685 cannot**: quadrature **encoder counting** on hardware interrupts D2/D3, and a **throttle watchdog** that stops the car if the Pi hangs. ⚠️ **5V logic — connect over USB, NEVER to Pi GPIO** (`gotchas.md`). Cost of the swap: no DonkeyCar backend exists, so the actuator path becomes custom firmware + a serial protocol | **$0.00** | owned |
| 18 | ~~8× 3mm LEDs (2 white, 2 red, 4 amber)~~ **SUPERSEDED 2026-09-03: 2× WS2812B addressable RGB strip segments, cut from one 1m/60px reel** | Headlights, tail lights, 4 indicators — same zones, now individually-addressed pixels on one data line instead of 8 discrete LEDs on 4 GPIO channels. Evan's call: "much easier to wire and mount." **Real, and it's bigger than wiring**: the old scheme used the car's last 3 free PWM pins with zero spare; the strip needs ONE regular digital pin (software-timed, not PWM), freeing 2 of those 3 pins. Rear lamps still must clear the forward camera's FOV (`docs/LIGHTING_SPEC.md` §1) — now a pixel-placement constraint on the strip, not a discrete-LED position. ⚠️ **Open, not resolved**: WS2812B libraries (Adafruit_NeoPixel/FastLED) disable interrupts during each pixel write, which can drop encoder ticks on D2/D3 — the car's only odometry. Needs a firmware answer (short strips, update only between control-loop ticks) before this gets coded; not blocking the purchase | **$7.99** | [BTF-LIGHTING WS2812B, 1m/60px, UL Listed](https://www.amazon.com/BTF-LIGHTING-Individual-Addressable-Flexible-Non-Waterproof/dp/B088BRY2SH) ✅ verified 2026-09-03, In Stock, pre-installed JST-SM connectors. One reel cut into 2 segments — not two separate reels |
| 19 | ~~LED series resistors~~ **MOSTLY MOOT 2026-09-03 — see row 18.** 1x 100k and 1x 12k for the pack-sense divider (Appendix BJ), plus ~1x 300-500Ω in series with the WS2812B data line (standard practice, protects the first pixel from spikes) | WS2812B pixels have a built-in constant-current driver per LED — no external series resistor per LED anymore. The whole 10mA-vs-20mA/per-pin-current derivation this row used to carry (Appendix BO) no longer applies to the lighting load — the strip draws off the LM2596 rail directly, not through an ATmega pin. Divider resistors (100k/12k) are unrelated to lighting and still needed regardless | **$7.38** | [30-value resistor kit, 600pc, 1Ω-1MΩ](https://www.amazon.com/KSOPUERT-Resistor-Assortment-Resistance-Values/dp/B0CN6N5DC4) — price from listing snippet, not individually re-verified live |
| 20 | Dupont jumpers + **data-only USB cable — CABLE OWNED** | Pi→Uno is **USB, not GPIO** (5V logic would damage the Pi's 3.3V pins). The USB 5V wire must be **cut or omitted**: the Uno's 5V pin is fed from the LM2596 rail so LED current stays off the Pi's bank, and two supplies must not back-feed each other. Plus LED and servo leads. ✅ **Evan already has a ~3ft USB 2.0 A-to-B cable, currently plugged into the Arduino (2026-09-03)** — no purchase needed, drops the $5.12 cable line entirely. ⚠️ The 5V-cut requirement above still applies to THIS cable once it moves to the permanent Pi↔Uno link: a standard USB cable is molded, so opening the jacket to find and isolate the red 5V conductor is still a real task, not skipped by already owning the cable | **$6.98** | [Dupont jumpers, 120pc M-M/M-F/F-F](https://www.amazon.com/EDGELEC-Optional-Breadboard-Assorted-Multicolored/dp/B07GCZ52WF) $6.98 — ✅ verified 2026-09-03, In Stock. USB cable: owned, no listing needed |
| **Assembly (added 2026-09-02, Appendix CF)** |
| 21 | **Arduino proto shield** (Uno footprint, solderable) | ⚠️ **NEW ROW.** `docs/WIRING_PROTOSHIELD.md` is written against this and it was never a line item. It carries the TB6612 carrier, the LM2596, the rocker, the bulk caps, the WS2812B data-line resistor and the pack-sense divider, and it exists to eliminate **flying Dupont jumpers, which back out under vibration** — the actual failure mode on a moving car. 68.6 × 53.4 mm, i.e. 60% of the measured 114.75 mm car width, so it mounts lengthwise; **stack height is still unbudgeted against the camera mount** | **$7.79** (2-pack + bonus breadboard) | [amazon.com/dp/B00HHYBWPO](https://www.amazon.com/HiLetgo-Prototype-Expansion-Breadboard-ProtoShield/dp/B00HHYBWPO) ✅ verified 2026-09-03, In Stock, Uno R3 fit confirmed in title |
| 22 | **Servo-to-pinion coupling** — UNRESOLVED | ⚠️ **NEW ROW, and it is a HARD CONSTRAINT, not a preference** (Appendices BS/BV). It was specified NOWHERE until 2026-09-02. **The steering coupler is the highest-torque joint on the car and a PRINTED cross-axle stub FAILS there: SF 0.57–0.96** at MG90S stall, against SF 2.26–3.77 for the drive coupler it was modelled on. It **must grip a real Lego axle**, never a printed cross profile. Manufactured candidate: **Adafruit #4252, $0.75** (micro-servo spline → 16 mm Lego cross axle) — ⚠️ Adafruit will not guarantee the spline beyond their own micro servo, and it is **injection-moulded plastic at the joint that just failed the printed check**; no torque rating is published. **Confirm the spline against a real MG90S; treat as working-torque-only.** Printed alternatives: Printables 61922 / 147626, socket-style only. ⚠️ **CHECKED 2026-09-03: no Amazon or eBay listing of THIS SPECIFIC adapter exists.** eBay surfaces only a different product (a motor+wheel assembly for LEGO/microbit robots, not a bare adapter for an existing servo); the only other manufactured option found anywhere is a laser-cut mindsensors.com adapter, not stocked on either marketplace. Adafruit remains the sole source for the exact part. **No coupling is chosen** | **$0.00–0.75** | [adafruit.com/product/4252](https://www.adafruit.com/product/4252) |
| — | ~~**Raspberry Pi Active Cooler (SC1148)**~~ **SUPERSEDED 2026-09-03 — the row 1 Vilros kit includes a metal case with passive+active PWM cooling.** The thermal argument in Appendix CI (soft throttle 80°C, hard 85°C, the 20.00 Hz control-rate risk) still stands and is now answered by the kit's included cooling rather than a separate purchase — ⚠️ **the kit's specific cooling solution (fan CFM, noise, whether it is PWM-controlled via the official 4-pin header or a simpler always-on fan) is UNVERIFIED — confirm on arrival against the same 80/85°C thresholds** | included in row 1 | **$0.00** *(was flagged $5.00, not added)* | included in row 1 |
| | | **TOTAL (sum of rows, current prices)** | **$397.70** | |

**LINKS ADDED + PRICES SPOT-CHECKED 2026-09-02 ~16:20 CDT.** The Source column
now carries markdown links, a deliberate departure from this file's bare-domain
convention — noted rather than slipped in.

**Re-verified live, all UNCHANGED from the 2026-08-08 re-pricing:** Pi 5 4GB
**$110.00** (in stock) · Camera Module 3 Wide **$38.50** (in stock) · Pololu
#1093 **$23.95** · Pololu #713 **$4.95**. **So the TOTAL below is current, not
stale** — which is the first time this file has been able to say that.

~~**Pi 5 2GB confirmed at $65.00 and IN STOCK at pishop.us**~~ **SOLD OUT as of
2026-09-03 (Evan) — the 2 GB path is CLOSED and row 1 is decided at 4 GB.**
The original note, kept because its reasoning about price risk still stands:
*it mattered* 
because it is the only path whose low end clears the $200 ceiling. **Adafruit
lists it at $75 and OUT OF STOCK** — so the cheap path depends on one vendor
having it, and that is a supply risk, not just a price.

**NOT re-verified** (linked but price unchecked): rows 9, 10, 12, 15. **Not
linked at all**~~ (no canonical product page found this pass): row 11 the USB-C
2S BMS, row 13 the XT30 pair, row 14 the SPST rocker.~~ **ALL THREE LINKED
2026-09-02 in the next commit** (Appendix BI) — and the COM-08837 suspicion was
right: the correct SparkFun part is **COM-11138**. Rows 4, 7, 16, 18-20 remain
generic `any` parts with no canonical page by design.

*(Total corrected 2026-08-06 from "≈$176–179" — the cold audit found it
excluded row 3, the camera cable, i.e. the very item this BOM was written to
catch. Fixed rows sum to $176.32; + $2–5 cable = $178.32–$181.32.)*
*(⚠️ That "2026-08-06" is wrong: this file's mtime is **2026-08-05 23:57 CDT**.
23:57 CDT = 04:57 UTC on 08-06 — the date was stamped in UTC, against the
Central-time rule. Left in place as written; flagged here, not silently edited.)*

*(**TOTAL raised 2026-09-01 ~21:20 CDT from ≈$222–225 to ≈$232–249** by rows
17–20, the lighting and I2C hardware (Appendix AY, `docs/LIGHTING_SPEC.md`).
Recomputed from the rows, not carried forward: rows 1–16 sum to
**$221.82–$224.82**, rows 17–20 add **$10.50–$24.00**, giving
**$232.32–$248.82 before shipping** and **≈$247–274 with the $15–25 shipping
estimate**. The earlier "≈$237–250" figure was the WITH-shipping number for the
old row set — the TOTAL row has always been pre-shipping, so the two were never
in conflict.*
*(~~**The $200 ceiling is now breached on every path, including the 2GB Pi.**
Swapping the Pi 5 4GB for the 2GB at $65 takes the build to **$187–204 before
shipping, ≈$202–229 with**. That was the swap that previously restored the
ceiling; with lighting it no longer does.~~ **SUPERSEDED 2026-09-02.**)*
*(**TOTAL lowered 2026-09-02 ~15:17 from ≈$232–249 to ≈$226–234** (Appendix BC):
row 17's PCA9685 is superseded by an **Arduino Uno R3 clone Evan already owns**,
taking rows 17–20 from $10.50–$24.00 to **$4.50–$9.00**. Recomputed from the
rows, not carried forward: **$226.32–$233.82 before shipping**, **≈$241–259
with** the $15–25 shipping estimate.)*
*(~~**The $200 ceiling is REACHABLE again at the low end — but only with the 2GB
Pi**, which now lands at **$181–189 before shipping, ≈$196–214 with**. The
bottom of that range clears $200; the top does not. On the 4GB Pi every path is
still over.~~ **SUPERSEDED 2026-09-02 ~17:45 CDT — see the row-5 correction
below.** Evan's call, and nothing is ordered.)*

*(**TOTAL raised 2026-09-02 ~17:45 CDT from ≈$226–234 to ≈$235–243** (Appendix
BO), by two changes that are drift repair rather than new scope: **row 5**
corrected from #1093 to the **#5159 encoder motor Evan chose on 2026-08-12**
(+$6.00), and **new row 5b**, the **#4763 JST SH cable** Pololu does not include
with it (+$3.00). Recomputed from the rows, not carried forward:
**$235.32–$242.82 before shipping**, **≈$250–268 with** the $15–25 estimate.)*

*(**TOTAL raised 2026-09-03 from ≈$235-243 to ≈$238-248** (Appendix CF) by two
rows that were never line items and are both required by documents already
written: **row 21**, the Arduino proto shield `docs/WIRING_PROTOSHIELD.md` is
entirely written against (+$3-4), and **row 22**, the servo-to-pinion coupling
that was specified nowhere until 2026-09-02 and whose printed form FAILS at
MG90S stall (+$0-0.75). Recomputed from the rows: **$238.32-$247.57 before
shipping, ≈$253-273 with** the $15-25 estimate. The **2GB Pi path** lands at
**$193.32-$202.57 before shipping, ≈$208-228 with**. Neither clears $200 with
shipping.)*

*(~~⚠️ **THE $200 CEILING IS NOW BREACHED ON EVERY PATH, INCLUDING THE 2GB Pi.**
The 2GB swap saves $45, landing at **$190.32–$197.82 before shipping** — which
still clears $200 — but **≈$205–223 with shipping**, which does not, at either
end.~~ **SUPERSEDED 2026-09-03 by the note above: rows 21–22 take the 2GB path
to $193.32–$202.57 before shipping, whose HIGH end no longer clears $200 either.
Struck rather than edited — a landing-check found it live and unstruck four
lines under its own replacement (Appendix CG).** The 2GB path was the last one whose low end cleared the ceiling and it no
longer does. **This is not a cost overrun from adding features**: both increments
are parts the existing design already required and the BOM had failed to list.
Evan decides whether the ceiling moves; nothing is ordered.)*

**⚠️ RE-PRICED 2026-08-08 ~23:03 CDT against live vendor pages — the total rose
≈$44 and the BOM's Pi price was already stale when this file was written.**

| Row | BOM price (dated 2026-07-23) | Live 2026-08-08 | Δ |
|---|---|---|---|
| 1 Pi 5 4GB | $70.00 | **$110.00** (pishop.us) · $130.00 (adafruit.com) | **+$40 to +$60** |
| 2 Camera Module 3 Wide | $35.00 | **$38.50** (pishop.us) | +$3.50 |
| 5 Pololu #1093 | $23.95 | **$23.95** — unchanged, confirmed on pololu.com | $0 |
| 6 Pololu #713 | $4.95 | **$4.95** — unchanged, confirmed on pololu.com | $0 |

Rows 3, 4, 7, 9–16 were **not** re-quoted: they are generic parts with "~"
estimates, and inventing two-decimal precision for them would be false
confidence. Assume they still hold.

**Revised fixed-row sum $219.82; + $2–5 cable = $221.82–$224.82; + $15–25
shipping = ≈$237–250** at pishop pricing, **≈$257–270** if the Pi comes from
Adafruit. The **$200 ceiling in the 2026-07-23 decision gate is now breached**
on the cheapest path.

**The $70 was never a 2026-07-23 price.** Raspberry Pi's own posts:
4GB was **$70 on 2025-12-01**, then **+$15 on 2026-02-02** → $85. So the figure
this BOM recorded as current on 2026-07-23 was **the December 2025 price, ~5½
months superseded at write time.** At least one further rise has happened since
(raspberrypi.com's own buy page now shows 16GB at **$305**, against $205 in
February) — I could not locate that announcement, so the exact current *official*
4GB price is **unverified**; the $110/$130 above are live retail, which is what
checkout actually costs.

**Cheaper Pi variants, live 2026-08-08 (pishop.us): 2GB $65.00 · 1GB $45.00.**
Dropping to 2GB returns the build to ≈$192–205 all-in — but 2GB is **below the
4GB DonkeyCar minimum** this BOM's row 1 cites. That is a real engineering
trade, not a free saving, and it is **Evan's call, not made here.**

**PI RECOMMENDATION 2026-08-12 (`docs/research/2026-08-12_onboard-compute-selection.md`):
~~switch row 1 to the Pi 5 **2GB at $65.00** (pishop.us, in stock).~~
**MOOT 2026-09-03: the 2 GB is SOLD OUT and row 1 is decided at 4 GB.** The
reasoning below is kept because it is still the correct account of WHY RAM was
never the binding constraint — which is what PRD task 8d (ONNX export) acts on.
 Same 2.4 GHz
Cortex-A76 silicon, saves **$45**, and it is the only variant Raspberry Pi has
held flat through all three 2025-26 DRAM hikes while the 4GB took every one
(official posts 2025-12-01 / 2026-02-02 / 2026-04-01). **Returns the build to
≈$192-205 all-in.** DonkeyCar's "4GB minimum" is an unjustified recommendation
— its `pi` extra installs tflite-runtime, not TensorFlow, and a 512MB Zero 2 W
already drives autonomously. The 2GB's risk is at `pip install`, fixable with a
temporary swap file, not at runtime. **Evan's call; not applied to row 1.**

**INDEPENDENTLY VERIFIED 2026-08-12 ~07:40 CDT** against live vendor pages by
a second session, because the re-pricing above was authored outside the session
that found it and a breached budget ceiling should not rest on an unattributed
edit. **All six prices confirmed exactly:** Pi 5 4GB $110.00 pishop (in stock)
and $130.00 Adafruit; Camera Module 3 Wide $38.50 pishop (in stock); Pololu
#1093 $23.95; Pololu #713 $4.95; Pi 5 2GB $65.00 pishop (in stock). **The
re-pricing is accurate and the $200 ceiling is genuinely breached.**

**Plus shipping**, which is the real risk: spread across Pololu, Adafruit /
Raspberry Pi, 18650BatteryStore, Addicore, Adeept, Aloft, SparkFun and BC
Robotics this could add **$15–25+**. Consolidating vendors matters more than
shaving item prices — most of the small parts (holder, buck, connectors,
switch, fuse, wire) are generic and can come from whichever single vendor
carries the most of them.

**Already owned, not purchased:** Lego Technic differential, steering
geometry donor parts, wheels/tires, 3D printer + filament, desktop PC
(RTX 3060 Ti), USB power bank, USB-C cable.

**Deliberately deferred, not in this BOM:** IMU (ICM-20948 $20 or BNO055
$35 — only if M4's observation design needs velocity/yaw) · RPLIDAR C1 $99
(chassis reserves the mount; only for a future SLAM milestone) · MG996R
servo (fallback only) · DRV8871 driver (not needed — the numbers say
paralleled TB6612 is enough).

---

## ORDER SHEET — grouped by vendor, 2026-09-03

**This is the section to buy from.** The row table below is the reasoning and
the history; this is the shopping list. Every price and stock string here was
checked on a live page on 2026-09-03. **Nothing is ordered.**

### ⚠️ Two things block placing it today

1. ~~The Pi 5 4 GB is out of stock at pishop, SparkFun and DigiKey.~~ **RESOLVED 2026-09-03: Evan is buying the Vilros Basic Starter Kit ($179.99, includes SD card + cooling + PSU), confirmed in stock at checkout.** See row 1.
2. **Both Addicore items are BACKORDERED** — 2-cell 18650 holder ($1.25) and
   LM2596 buck ($2.48). Substitutes needed, or wait.
3. **The fuse holder is priced in CAD from a Canadian vendor** and ships
   cross-border. Prefer a US source.

### The order, by vendor

| vendor | items | subtotal | note |
|---|---|---|---|
| **Vilros** | [Basic Starter Kit, 4GB](https://vilros.com/products/raspberry-pi-5?variant=40082990301278) (includes SD card, cooling, PSU, HDMI adapter, storage bag, RTC connector, camera adapter cable of unconfirmed fit) | **$179.99** | FINAL, Evan 2026-09-03, confirmed in stock at checkout |
| **DigiKey** | [Camera Module 3 Wide, SC1224](https://www.digikey.com/en/products/detail/raspberry-pi/SC1224/17278644) $35.00 · [camera cable 200 mm, SC1892](https://www.digikey.com/en/products/detail/raspberry-pi/SC1892/21658272) $1.00 — ⚠️ **keep both until the kit's bundled camera cable is checked against Camera Module 3 Wide on arrival**; if it fits, drop SC1892 ($1.00) | **$36.00** | $4.99 USPS Ground Advantage, **no free threshold** |
| **Pololu** | [#5159 encoder motor](https://www.pololu.com/product/5159) $29.95 · [#4763 JST SH cable](https://www.pololu.com/product/4763) $3.00 · [#713 TB6612](https://www.pololu.com/product/713) $4.95 | **$37.90** | all in stock (32/125/459). **$62.10 short of their $100 Pololu-branded free-shipping threshold** |
| **IMR or 18650BatteryStore** | 2× [Samsung 25R](https://www.imrbatteries.com/products/samsung-25r-18650-2500mah-20a-battery) @ $4.99 | **$9.98** | ⚠️ same operation — not two sources. USPS caps lithium at **8 cells/package**; sales are **final** |
| **Amazon** | [ACEIRMC 2S 8A BMS, 8-pack](https://www.amazon.com/dp/B08HLQQCQJ) — need 1, get 7 spares | **$9.59** | the safety-critical half; cutoff 2.9 V ±0.05 V. No single-unit listing exists |
| **Adeept** | [p0374 USB-C 2S charger](http://www.adeept.com/li-ion-battery-charger-m-2s2a_p0374.html) | **$7.99** | charger only — the BMS above does the protecting |
| **Amazon (folded 2026-09-03)** | [MG90S metal-gear servo, 2-pack](https://www.amazon.com/Replace-Helicopter-Airplane-Controls-Vehicle/dp/B09KXM5L7Z) $7.99 · [Arduino Uno proto shield, 2-pack + breadboard](https://www.amazon.com/HiLetgo-Prototype-Expansion-Breadboard-ProtoShield/dp/B00HHYBWPO) $7.79 · [XT30 pairs, genuine Amass, 20-pack](https://www.amazon.com/Amass-Upgrade-Female-Connectors-Battery/dp/B0CFFJK4XH) $11.99 · [ATO/ATC fuse holder + 20 fuses incl. 3A, 4-pack](https://www.amazon.com/dp/B0F6NPV287) $7.99 · [SPST rocker switch 12V DC, 5-pack](https://www.amazon.com/dp/B07S1MV462) $6.39 · [470µF 25V electrolytic caps, 10-pack](https://www.amazon.com/Projects-Radial-Electrolytic-Capacitor-470uF/dp/B0CPTDPG6S) $7.07 · [0.1µF ceramic caps, 50-pack](https://www.amazon.com/BOJACK-Capacitors-Low-Voltage-Dielectric-Capacitor/dp/B07X5XTDPB) $6.99 · [BTF-LIGHTING WS2812B strip, 1m/60px](https://www.amazon.com/BTF-LIGHTING-Individual-Addressable-Flexible-Non-Waterproof/dp/B088BRY2SH) $7.99 (supersedes the 3 discrete-LED packs, see row 18) · [30-value resistor kit, 600pcs, 1Ω-1MΩ](https://www.amazon.com/KSOPUERT-Resistor-Assortment-Resistance-Values/dp/B0CN6N5DC4) $7.38 · [Fermerry 22 AWG wire, 6×5ft](https://www.amazon.com/Fermerry-Stranded-Silicone-Flexible-Electrical/dp/B089D29FHC) $9.69 · [SCHDRA 26 AWG wire, 6×20ft](https://www.amazon.com/Silicone-Electrical-SCHDRA-Tinned-Copper/dp/B0C9MB4DTY) $9.99 · [KOOWIN heat-shrink, 720pc/8 sizes](https://www.amazon.com/Shrink-Tubing-Tubes-KOOWIN-Ratio/dp/B098LB9LTJ) $7.99 · [40-pin 0.1" headers, 20-pack](https://www.amazon.com/Straight-Breakaway-Connector-Breadboard-Electronic/dp/B0FRZW75VS) $6.29 · [Dupont jumpers, 120pc M-M/M-F/F-F](https://www.amazon.com/EDGELEC-Optional-Breadboard-Assorted-Multicolored/dp/B07GCZ52WF) $6.98 (USB-A-to-B cable dropped — Evan already owns one, plugged into the Arduino) | **$112.52** *(14 items, all live-verified 2026-09-03; right-sized twice, then the LED scheme itself changed to a WS2812B strip — see below)* | ✅ **RESOLVES THE OLD "small-order problem" ROW ENTIRELY** — the SPST rocker, XT30 pair and fuse holder all now ship in the SAME Amazon order as the BMS (row 11b) and servo, ending the 3-separate-vendor situation for $4.80 of parts. |
| — | ~~microSD, wire+shrink+caps+headers, LEDs, resistors, Dupont+USB, proto shield, coupling~~ **SUPERSEDED 2026-09-03 by the Amazon row above** — microSD is in the Vilros kit; every other generic item now has a live Amazon link with real price/stock, checked 2026-09-03, instead of an "any" placeholder | — | — |

**Update 2026-09-03: the last six Amazon-row items are now live-verified too** (22 AWG wire, 26 AWG wire, heat shrink, headers, Dupont jumpers, USB-A-to-B cable — the earlier note called them "the last five" because 22 AWG and 26 AWG were one bullet). Same standard as everything else in this row: title, price and stock read off the rendered page, not a search snippet. ~~**They came in over the earlier $35–$45 guess: $71.86 for all six**, driven mostly by the two wire kits ($20.49 + $24.99 = $45.48 alone — more than the entire old budget).~~ **RIGHT-SIZED same day, after Evan asked "why do I need so much wire": the 25ft/50ft spools were the largest size pre-selected on each listing, not a considered choice.** Every realistic run on this car (motor leads, battery/BMS/charger leads, servo leads, 8 LED pairs, pack-sense divider) adds up to roughly 15-30 ft total even with generous slack for mistakes — nowhere near 150 ft of 22 AWG + 300 ft of 26 AWG. Both listings sell smaller sizes on the same page (5ft/10ft/25ft/100ft for 22 AWG; 25ft/50ft/100ft for 26 AWG — 26 AWG has no smaller tier than 25ft). ~~Switched to the smallest size that still gives full 6-color runs: **22 AWG 6×5ft ($9.69) + 26 AWG 6×25ft ($16.49) = $26.18**, saving **$19.30** — and per-foot price is WORSE at the smaller size ($0.32/ft vs $0.14/ft for 22 AWG) because Amazon's bulk-pack economics cut the other way here too, but the absolute dollar cost is still lower since even 30ft (22 AWG) + 150ft (26 AWG) is more wire than needed.~~ **RE-SOURCED same day: Evan found a cheaper listing himself (SCHDRA, same seller carries both gauges as size variants of one product family) — 22 AWG 6×13ft ($10.76) + 26 AWG 6×20ft ($9.99) = $20.75**, a further **$5.43** below the right-sized Fermerry picks, for MORE wire (198 ft vs 180 ft) and a better gauge balance (the Fermerry split was oddly skewed toward 26 AWG). Live-verified 2026-09-03: both variants In Stock, ratings 4.5★/130 (26 AWG) and 4.3★/147 (22 AWG). **CORRECTED same day: Evan only meant to switch the 26 AWG — he already has the Fermerry 22 AWG 6×5ft on hand from the right-sizing pass, no need to re-buy it.** Final wire pick: **Fermerry 22 AWG 6×5ft ($9.69) + SCHDRA 26 AWG 6×20ft ($9.99) = $19.68.** Picked: stranded silicone wire both gauges (flexible insulation over plain PVC, which matters on a car that vibrates), a KOOWIN 720pc heat-shrink assortment, a 40-pin single-row 0.1" breakaway header 20-pack, an EDGELEC 120pc Dupont kit covering all three connector types (M-M/M-F/F-F), and the Amazon Basics USB-A-to-B cable needed for the Pi↔Uno serial link. ~~⚠️ The USB cable listing showed only 9 left in stock at check time — a real but minor reorder risk if it sells through before Evan checks out.~~ **MOOT, same day: Evan already owns a ~3ft USB 2.0 A-to-B cable, currently plugged into the Arduino — the cable line drops from this row entirely (-$5.12).** **Every remaining unlinked "any" placeholder in this BOM is now closed.**

**Second pass, same day: Evan asked to check the REST of the Amazon row for smaller options too** (“all the other amazon items have very large part counts”). Checked all nine remaining bulk items against smaller listings, live: **two had a real, cheaper, smaller alternative; seven did not.**

**Switched (rows 14 & 15, superseded above):**
- **Rocker switch**: SparkFun single-unit ($0.75, but its own vendor) → folded onto a 10-pack ($15.00, Appendix CP) → **DaierTek 5-pack, $6.39** — half the pack, better-matched spec (12V DC/automotive vs. the SparkFun part’s 125VAC household rating), pre-wired, more reviews (3,586 vs the old pick’s smaller count).
- **Fuse holder**: 10-pack + 70 fuses ($9.98) → **Anyongora 4-pack + 20 fuses, $7.99** — confirmed the 3A rating is still included (the exact spec a rejected earlier candidate, MCIGICM, failed on — Appendix CP), plus IP67 waterproofing and pre-wired 16AWG leads as a bonus.

**Checked, no better option found — stayed as-is:** XT30 pairs (smaller genuine-Amass packs either cost more per pair or ship in 3-7 weeks, not Prime-fast), 40-pin headers (already the cheapest listing found), the 600pc resistor kit (smaller assortment kits found were BOTH pricier and larger — 600pc is already near the floor for this product category), the 720pc heat-shrink assortment, and the 50-pack 0.1µF caps (already the smallest tier on its listing). **Not checked**: the 470µF caps (already modest at 10-for-3-needed) and the MG90S servo / proto shield 2-packs (both keep a deliberate spare for stated failure-mode reasons, not an unexamined default).

**Third pass, same day: the 3 discrete-LED packs are gone entirely, not just resized.** Evan proposed WS2812B addressable RGB strips instead of 8 discrete 3mm LEDs — "much easier to wire and mount." Verified: it is, and it also frees 2 of the car's last 3 PWM pins (the strip needs one software-timed digital pin, not PWM). Checked LM2596 headroom first (module rated 3A per Addicore's listing, closing a gap `WIRING_PROTOSHIELD.md` had flagged as unverified; existing peak load 840mA leaves ~2.16A margin — a strip at realistic brightness draws well under that). Picked **BTF-LIGHTING WS2812B, 1m/60px, $7.99, UL Listed, In Stock** — one reel, cut into 2 segments, not two separate reels. Drops the 3 LED packs ($20.97) and the 8-LED-resistor need (row 19), **net −$12.98**. ⚠️ **Genuinely open, not resolved by this purchase**: NeoPixel-style libraries disable interrupts during pixel writes, which can drop encoder ticks on D2/D3 — needs a firmware answer before the lighting code gets written. `docs/LIGHTING_SPEC.md` and `docs/WIRING_PROTOSHIELD.md` both still describe the old discrete-LED scheme and need updating to match — flagged, not done here.

⚠️ **CONSOLIDATION IS NOT FREE, AND THE JUMP IS LARGER THAN THE FIRST ESTIMATE — stated plainly rather than buried in a table.** Folding the small-order items and the generic parts onto Amazon (2026-09-03) cost **+$135.47 to +$141.72** over the previous piecemeal estimate, almost entirely because Amazon's hobby sellers sell in bulk packs, not the 1x quantities this build actually needs: **1 of 5** rocker switches (was 1 of 10), **1 of 20** XT30 pairs, **~20 of 600** resistors, **1 of 4** fuse holders (was 1 of 10), **1 of 6** wire spools per gauge — the LED multiple is gone entirely, not just smaller: the 3-pack LED buy (8 of 300) is superseded by a single WS2812B strip, a different lighting architecture, not a bulkier version of the same part. What remains is the same pattern as the ACEIRMC BMS (Appendix CO) — the individual per-unit price is often *cheaper* than the old single-unit sources — but repeated across ~14 items the cumulative overshoot is real money, not a rounding error. **The figure grew from an earlier +$104.86–$108.61 estimate once the last six commodity items were live-verified instead of budget-guessed, dropped once the USB cable turned out to already be owned, dropped again once the wire kits were right-sized, dropped once more when Evan found a cheaper wire listing (SCHDRA) himself, dropped a fourth time when a full sweep found smaller listings for the rocker switch and fuse holder, then dropped a fifth time when the LED scheme changed to a WS2812B strip: net **+$80.97 to +$87.22** over the pre-fold estimate.** **This is a genuine tradeoff (fewer vendors, no more sub-shipping-cost line items, no more CAD currency problem — for about $81–$87 more), and it has not been decided for Evan.**

**SUM OF ROWS: $397.70** before shipping (down from $410.68 — the LED scheme changed to a WS2812B strip, see below. First time under $400. Still a single precise figure, not a range: every row in the BOM has a live-verified price as of 2026-09-03). With shipping now concentrated mostly on ONE Amazon order (free with Prime or over $35, easily cleared) plus Vilros/Pololu/IMR/Adeept/DigiKey separately:
**≈$410 – $425 all-in** — a rough estimate, since per-vendor shipping was not re-summed line by line after this consolidation.

### The practical lesson this sheet encodes

**Several items cost less than the freight to get them.** A $0.75 rocker switch,
a $1.10 connector pair and a $2.95 fuse holder from three different vendors is
three shipping charges for $4.80 of parts. **Consolidation's real value here is
not a discount — it is not paying $8 to ship a 75-cent switch.**

---

## Wiring architecture

```
[USB POWER BANK 5V/3A] --USB-C--> [Raspberry Pi 5 4GB]  ... and nothing else
                                          |
                                          |  USB (DATA ONLY - 5V wire cut)
                                          v
                                    [ARDUINO UNO]  5V logic, FTDI, COM3
                                          |
                    +---------------------+----------------+
                    |  D9 servo   D5/D6 lights (PWM)       |  D2/D3 INT
                    |  D11 motor PWM  D4/D7 indicators     |  <- encoder
                    v                                      v
[2x 18650 = 7.4V] --fuse--switch--+--> [TB6612FNG] --> [N20 motor] --> Lego diff
   + USB-C BMS board             |       (both channels PARALLELED)
                                 +--> [LM2596 @ 5.2V] --+--> [MG90S servo]
                                                        +--> [UNO 5V pin]
                                                        +--> LED commons

                    [UNO] pin budget (CORRECTED 2026-09-02 -- the earlier
                    map double-booked D3, and BOTH files omitted STBY
                    entirely; see firmware/SERIAL_PROTOCOL.md SS1/SS1a):
                       D2  encoder A (INT0)    D5  headlights  (PWM Timer0)
                       D3  encoder B (INT1)    D6  tail lights (PWM Timer0)
                       D9  servo (Timer1)      D4  left  indicator (digital)
                       D11 motor PWM (Timer2)  D7  right indicator (digital)
                       D8/D12 motor DIR        D13 status LED
                       D10 TB6612 STBY         A0  pack sense divider
                    Motor PWM MUST be Timer2: Timer0 also drives millis(), so
                    its frequency cannot move, and motor PWM is the one channel
                    that may need raising above the audible band.
```

**The one rule that matters (amended again 2026-09-02):** **no power path
crosses between the Pi and the motor pack.** As of the Arduino swap, what
crosses is **USB data only** — the 5V conductor is cut, so even the data link
carries no power. Every actuator signal (PWM, direction, servo, lights) now
originates on the Uno, on the motor-pack side. **This is the cleanest the
separation has ever been:** the previous PCA9685 design had ground, SDA, SCL,
a 3.3V logic supply and two direction lines crossing; the Uno design has two
data wires and a shared ground reference.

*(History, kept because the rule was wrong twice. It originally read "they
share **ground only** … Nothing else crosses between them", which was already
self-contradictory — the same paragraph required the ground as a reference "for
the PWM/direction logic", so PWM and direction wires crossed all along. The
2026-09-01 amendment fixed the wording for I2C. The 2026-09-02 Arduino swap
then made the strong version true for the first time.)*

**Why the Uno sits on the motor rail, not on USB power:** its **5V pin** is fed
from the LM2596, so LED current (~120mA peak, see row 19) never touches the
Pi's 5V/3A bank with its 600mA peripheral cap. **Do NOT power it from VIN off
the 7.4V pack** — the pack sags under motor stall, and below ~7V the on-board
AMS1117 drops out and browns the Uno out mid-drive, taking the servo and the
watchdog with it. Feeding the 5V pin bypasses that regulator entirely.

**Why the USB 5V wire must be cut:** with the Uno powered from the LM2596 and
USB plugged in, two 5V supplies meet on one rail and back-feed. A data-only
cable removes the conflict rather than relying on the board's power-select
circuit, which is unverified on a clone.

**Why not one battery:** a simultaneous Pi peak + servo stall + motor stall
draws **4.62A**, which collapses a 3A rail and hard-resets the Pi mid-run
with the SD card mounted. The split is structural, not stylistic.

---

## Verify before ordering

1. **Your power bank's output rating** — the label or spec must say **5V/3A**
   (or 15W). Measured Pi 5 draw under CNN inference is 1.40A, so even a 2.4A
   bank very likely works, but confirm before relying on it. It must also be
   a plain 5V USB-A/C output; you do not need and should not rely on PD.
2. **Which Lego differential you actually have** — 62821 (28-tooth ring) or
   6573 (24/16). This sets the reduction and therefore the mesh centres in
   CAD. Count the teeth.
3. **Which tires** — the part name states the real diameter (44309 = 43.2mm,
   32019 = 62.4mm). Config B (62.4mm + 12t→28t) is the lower-risk drivetrain.
4. ~~**Prices at checkout** — Pi pricing moved twice in three months this year.~~
   **DONE 2026-08-08 ~23:03 CDT** — see the re-pricing table above. Total is
   ~~**≈$237–250**~~ **≈$241–259 with shipping as of 2026-09-02**, not ≈$195. Checks 1–3 remain open and are all physical
   inspection; this was the only one of the four that did not need Evan's hands.
   *(Amended 2026-09-01, again 2026-09-02 (Appendix BK): that "≈$237–250" was
   the with-shipping figure for the pre-lighting row set; it is now
   **≈$241–259** (~~≈$247–274~~, itself superseded when the PCA9685 became a
   $0 owned Arduino). And "Checks 1–3 remain open" is superseded twice over —
   checks 5 and 6 were added below, so **the open set is 1–3, 5 and 6**.
   Prices: 7 of 20 rows re-verified 2026-09-02; rows 9, 10, 12 and 15 are
   linked but their prices are NOT re-checked.)*
5. **Which LEDs** — forward voltage and current set every series-resistor value
   in row 19, and decide whether the Uno can drive them directly (20mA/pin,
   **200mA absolute max across ALL pins** — 8 LEDs at 20mA is 160mA, 80% of
   that hard limit) or whether they need MOSFETs off the LM2596 rail instead.
   The **~160mA total is an ESTIMATE** at
   20mA × 8 LEDs (`docs/LIGHTING_SPEC.md` §3); nothing has been measured. Pick
   the LEDs before ordering resistors, not after.
6. ⚠️ **OVER-DISCHARGE PROTECTION FOR THE 2S PACK — unresolved safety gap
   (found 2026-09-02, Appendix BI).** Row 11's board is titled "BMS" but Adeept's
   own page documents only over-voltage/overcharge and short-circuit protection.
   **Over-discharge protection is not listed**, and the EVE 25P cells in row 9 are
   bare (unprotected). So nothing in the BOM as written stops the pack being run
   flat under motor load. Below ~2.5 V/cell lithium suffers permanent capacity
   loss and, in the worst case, internal copper shunts that become a fire risk on
   the NEXT charge. Short-circuit is separately covered by the mandatory fuse
   (row 15); this is specifically the low-voltage end. **Close it one of three
   ways before ordering:** (a) a 2S protection board that explicitly states
   over-discharge cutoff, (b) protected cells, or (c) **firmware cutoff on the
   Arduino** — A0-A5 are free (`firmware/SERIAL_PROTOCOL.md` §1), so a resistor
   divider on the pack lets the Uno cut throttle at a voltage threshold, reusing
   the watchdog path that already exists. (c) costs two resistors and is the only
   option that also *logs* the event.
   ✅ **(c) IS NOW IMPLEMENTED (2026-09-02, Appendix BJ):**
   `firmware/uno_packguard/` — divider **100k (pack+ to A0) / 12k (A0 to GND)**,
   internal 1.1 V reference, warn 6.4 V, latched cutoff 6.0 V held 500 ms,
   fault outside 4.0-8.8 V. **SELFTEST PASS 27/27 on the real board.** Still
   needs (a) or (b) as well if you want protection that survives the Arduino
   being unpowered — firmware cannot guard a pack when the firmware is off.

## Caveats carried into the build

- **Matched cells:** ~~the $7.99 BMS board's published protection list covers
  overcharge, over-discharge and short circuit~~ ⚠️ **CORRECTED 2026-09-02
  (Appendix BK): it does NOT cover over-discharge** — see row 11 and Verify
  item 6. Adeept lists over-voltage and short-circuit only. The board also
  **does not state per-cell balancing**. With two new cells from the same order this is tolerable;
  check them with a multimeter occasionally, and never mix in an older cell.
  (The alternative — an XTAR FC2 at $6.99 charging cells individually —
  eliminates balancing entirely but means pulling cells out to charge and
  leaves the pack with no discharge protection.)
- **Two unverified motor dimensions** — mounting-hole spacing (10 ± 0.2mm,
  single-source) and D-flat depth (unpublished). **Measure both with
  calipers on arrival, before the rear module is committed to CAD.**
- **The printed coupler** must be a socket gripping a *real* Lego axle, never
  a printed axle cross-profile (SF 2–4 in torsion at stall).
- **Weight:** this is the heaviest power option (~320g of battery). If the
  car turns out underpowered, the battery is the first thing to revisit.

---

## Vendor consolidation — researched 2026-09-03 (Appendix CJ). **VERDICT: NO SINGLE VENDOR EXISTS.**

Evan asked to consolidate onto one vendor for a bulk order. Two sweeps have
landed (Adafruit, SparkFun); Pololu and the DigiKey/Mouser hypothesis are still
running. **The answer is already no**, and the reasons are structural rather
than stock-related.

### ⚠️ The Pi 5 4 GB is OUT OF STOCK at three of the four vendors checked

| vendor | 2 GB | 4 GB |
|---|---|---|
| pishop.us | **$65, IN STOCK** | $110, **out of stock** |
| adafruit.com | out of stock | **$130, 26 in stock** |
| sparkfun.com | — | $110, **out of stock** (DEV-23550) |
| CanaKit | — | **$110, In Stock** (PI5-4GB) |

**Only Adafruit and CanaKit can supply a 4 GB today.** The 2 GB is available at
pishop for $45 less. **This is Evan's call and it is now vendor-coupled.**

### Adafruit — 10 of 22, and the gap is a CATALOG gap

**Items 10–16 are a clean eight-item zero**: loose 18650s, 2-cell holder, 2S
BMS, adjustable buck, XT30, rocker switch, fuse holder. Adafruit's power
ecosystem is 1S-LiPo-with-JST-PH; loose-cell 2S is simply not a product line
there, so waiting for stock changes nothing. Also **no 30:1 N20** (ladder is
1:50 / 1:100 / 1:298) and their motors ship **bare leads, not JST SH**. Pi 5
4 GB is **$130**, $20 over the others. **No free-shipping threshold — and a
~$250 order CROSSES their $200 line, which removes the two cheapest services.**
Consolidating into one large order makes their shipping worse, not better.

### SparkFun — 18 of 22, free shipping at $100+, but TWO SPEC FAILURES

**The only vendor found so far with a free-shipping threshold** (UPS Ground,
$100+, under 10 lb, contiguous 48, logged in). That is a genuine consolidation
win. But two substitutions fail on physics, not preference:

- ⚠️ **ROB-28633 N20 encoder motor: 500 RPM no-load at 6 V — HALF the Pololu
  #5159's 1000 RPM.** Config B gives 1.28 m/s at 1000 RPM, so this lands at
  **~0.64 m/s — below the 1.0 m/s floor that rejected every Lego motor**
  (best case PF M was 0.88 m/s). **Same rejection, same reason.** It is also
  31.5:1 not 30:1, and 882 CPR at the output not 358 — the encoder is better,
  the speed is disqualifying. Sold as a pair, $19.95, cable included.
- ⚠️ **PRT-12895 18650: "0.2C to a maximum of 1C" = 2.6 A continuous.**
  Worst-case pack draw is ~2.5 A, so margin is **1.04x** against a stated
  requirement of ≥5 A (2x). **Do not buy these.** The page states neither
  protected/unprotected nor flat-top/button-top.

Also NOT FOUND at SparkFun: the 2S BMS, XT30 (only XT60), the blade fuse holder,
and the LEGO servo adapter.

### The safety item nobody stocks

**No vendor checked has a 2S BMS whose page documents OVER-DISCHARGE
protection.** SparkFun's nearest (Battery Babysitter, PRT-13777) is **1S only,
microUSB, and its page names no protection features at all.** Adafruit has no 2S
BMS in any form. **BOM Verify item 6 — the open safety hole — is still open, and
is now the hardest item to source rather than merely the most overlooked.**

### Where this leaves the order

**Two vendors minimum, and realistically three.** No catalog carries both a
30:1-class encoder motor at 1000 RPM *and* loose 2S lithium *and* automotive
fusing. The residual after any single vendor is always the power/wiring half.

### Pololu — 5 of 22 clean, and it owns the half nobody else does

**The three BOM parts only Pololu carries are all IN STOCK** (checked
2026-09-03, counts read from the page's own `data-available-stock`):
**#5159 encoder motor $29.95 (32 in stock)** · **#4763 JST SH cable $3.00 (125)**
· **#713 TB6612 carrier $4.95 (459)**. Basket **$37.90**.

⚠️ **Their free-shipping threshold does NOT help this order.** It is *"Orders of
$100 or more of **Pololu-branded, active-status** products"* — the drivetrain
basket is $37.90, **$62.10 short**, and most of what would pad it out (wire,
switches, LEDs, servo, jumpers) is Generic/PCX/FEETECH-branded and **does not
count toward the threshold at all.**

**Pololu cannot supply 13 of 22** — the entire compute half (no Pi 5, no camera,
no CSI cable, no cooler, no SD card; their Raspberry Pi category is standoffs
and headers), **no lithium cells or holders of any kind** (batteries are NiMH
AA/AAA only), no 2S BMS, no XT30, no fuse holder, no proto shield, no LEGO
adapter. Partials carry real compromises: their only metal-gear servo is **20 g
with a standard spline, not a 9 g micro**; the adjustable buck is either ~600 mA
(too weak) or a different topology; 3 mm LEDs are green/yellow only.

### ⚠️ THE 2S BMS DOES NOT EXIST AT ANY OF THE THREE

Confirmed independently by all three sweeps: **Adafruit has no 2S BMS in any
form; SparkFun's nearest is 1S/microUSB and its page names no protection
features at all; Pololu's only lithium charger is discontinued.** No page at any
vendor could be quoted for over-discharge or low-voltage cutoff **because no
such product is stocked.** BOM Verify item 6 is now the **hardest item in this
build to source**, not merely the most overlooked — and it is the one guarding
against a fire risk on the next charge.

### RECOMMENDED STRUCTURE: three vendors, not one

1. **Pololu** — #5159, #4763, #713 ($37.90, all in stock). Nothing else there is
   worth the freight.
2. **One general vendor for the bulk** — SparkFun is the only one found with a
   usable free-shipping threshold ($100+, under 10 lb, contiguous 48), **but do
   NOT take its N20 or its 18650s** (both fail on spec, above).
3. **A dedicated battery/RC source** for the 18650 cells, a 2S BMS that actually
   documents over-discharge cutoff, XT30, and the blade fuse holder.

Plus the Pi itself from wherever it is in stock — currently Adafruit ($130) or
CanaKit ($110) for a 4 GB, or pishop for a 2 GB ($65).

**Untested hypothesis:** DigiKey and Mouser are authorized distributors for
Adafruit, SparkFun *and* Pololu house-brand parts, so one of them might collapse
steps 1–3. Both block automated fetches; **not verified, do not assume.**

### DigiKey — the consolidation hypothesis is FALSIFIED, but it is the cheapest Pi source

**DigiKey does NOT consolidate this BOM**, despite being an authorized
distributor for Adafruit, SparkFun *and* Pololu. The reason is structural: the
Pololu parts are **DigiKey Marketplace, not DigiKey inventory** — #5159 ($29.95,
143 in stock) and #4763 ($3.00, 926) both state *"Will ship in approximately 1
days from Pololu. A separate shipping fee may apply."* **That is a Pololu order
with a DigiKey invoice — a second parcel and a second shipping charge, on
exactly the items that matter.** Zero consolidation gained.

It also fails the battery subsystem outright: **no high-drain 18650** (their
stocked cells top out at a **520 mA** continuous rating, against the ≥5 A this
build needs), **no 2S USB-C BMS**, and **no LM2596 module**. MG90S NOT FOUND.

**But it is meaningfully cheaper on three Pi-ecosystem items** — worth using as
a secondary vendor:

| item | DigiKey | pishop | saving |
|---|---|---|---|
| Camera Module 3 Wide (SC1224) | **$35.00**, 7,215 in stock | $38.50 | −$3.50 |
| Pi 5 camera cable 200 mm (SC1892) | **$1.00**, 3,728 in stock | $2.95 | −$1.95 |
| Active Cooler (SC1148) | **$5.00**, 27,926 in stock | $10.95 | −$5.95 |

**−$11.40 across three items.**

⚠️ **THIRD confirmation the Pi 5 4 GB is unavailable:** DigiKey SC1431 $110.00,
**0 in stock, 180 due 2026-10-05.** That restock date is the first hard timeline
anyone has published. Out at pishop, SparkFun and DigiKey; **CanaKit remains the
only verified in-stock 4 GB**, at the same $110.00.

⚠️ **A second search-snippet lie, same session.** A snippet claiming DigiKey
gives free shipping over $50 traces to `digikey.com/en/help/set-rate-shipping/`**`th`**
— **the THAILAND page.** No US page confirms it. **US shipping is verified only
as $4.99 USPS Ground Advantage and up, no threshold, no minimum.**

**Mouser is UNASSESSED, not ruled out** — five fetch attempts timed out with no
block page, so it reports 0 of 22 for connectivity reasons only.
