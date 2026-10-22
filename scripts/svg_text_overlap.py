"""Text-overlap check for the hand-read diagrams: every text in an SVG must be
clear of other text and of anything important drawn under it.

Each SVG is loaded in headless Chrome (real font metrics, not estimates) and a
script lists every text whose rendered box
  - hits another text,
  - hits a circle (holes, pins; a large unfilled ring only counts if the text
    crosses its outline),
  - has a point of a stroked line / path / polyline / polygon inside it,
  - or straddles the edge of a stroked rect.
Not counted: anything inside a `class="copper"` group (background), and an
obstacle hidden by an opaque tag rect drawn after it and before the text (the
white wire-length tags).

Origin: Evan asked 2026-10-20 for bold, never-overlapped labels on these three
diagrams (record KI); this keeps them that way.

Usage: python scripts/svg_text_overlap.py [file.svg ...]   (default: TARGETS)
Exit 0 = no overlaps; 1 = overlaps listed; 2 = no Chrome / Edge found.
Chrome is found via $CHROME, the usual Windows install paths, then PATH
(google-chrome, chromium, chromium-browser, msedge). Without one, self_check
raises FileNotFoundError, which run_checks.py reports as a SKIP (e.g. the Pi).
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ["docs/shield_holemap.svg", "docs/electronics_layout.svg", "docs/pack_wiring_full.svg",
           "docs/shield_build_guide.svg"]
WIN_PATHS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]

JS = r"""
const svg = document.querySelector('svg');
const P = (x, y) => { const p = svg.createSVGPoint(); p.x = x; p.y = y; return p; };
function box(el) { const b = el.getBBox(); const m = el.getCTM();
  const a = P(b.x, b.y).matrixTransform(m), c = P(b.x + b.width, b.y + b.height).matrixTransform(m);
  return [Math.min(a.x, c.x), Math.min(a.y, c.y), Math.max(a.x, c.x), Math.max(a.y, c.y)]; }
// getBBox of a text is the full font box; shrink it to the ink band
function tbox(el) { const b = box(el); const h = b[3] - b[1];
  return [b[0] + 0.5, b[1] + h * 0.18, b[2] - 0.5, b[3] - h * 0.12]; }
const hit = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];
const inside = (p, r) => p.x > r[0] && p.x < r[2] && p.y > r[1] && p.y < r[3];
const texts = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim());
const tb = texts.map(tbox);
const out = [];
const all = [...svg.querySelectorAll('*')]; const ord = e => all.indexOf(e);
const badges = [...svg.querySelectorAll('rect')].filter(r => { const f = r.getAttribute('fill'); const o = r.getAttribute('fill-opacity');
  return f && f !== 'none' && (o === null || +o >= 0.9); }).map(r => [r, box(r)]);
function covered(ti, obst) { const t = tb[ti]; return badges.some(([r, b]) => ord(r) > ord(obst) && ord(r) < ord(texts[ti]) &&
  t[0] >= b[0] - 1 && t[2] <= b[2] + 1 && t[1] >= b[1] - 1 && t[3] <= b[3] + 1 && (b[2] - b[0]) < 400); }
const name = t => t.textContent.trim().slice(0, 40);
for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++)
  if (hit(tb[i], tb[j])) out.push(['text/text', name(texts[i]), name(texts[j])]);
function samples(el) { const pts = []; const m = el.getCTM();
  if (el.tagName === 'line') { const g = n => +el.getAttribute(n); const n = 60;
    for (let k = 0; k <= n; k++) pts.push(P(g('x1') + (g('x2') - g('x1')) * k / n, g('y1') + (g('y2') - g('y1')) * k / n).matrixTransform(m));
  } else { const L = el.getTotalLength(); const n = Math.max(20, Math.ceil(L / 2));
    for (let k = 0; k <= n; k++) { const q = el.getPointAtLength(L * k / n); pts.push(P(q.x, q.y).matrixTransform(m)); } }
  return pts; }
const bg = e => !!e.closest('.copper, [data-bg]');
const strokes = [...svg.querySelectorAll('line, path, polyline, polygon')].filter(e => { if (bg(e)) return false;
  const s = getComputedStyle(e); return s.stroke !== 'none' && parseFloat(s.strokeWidth) > 0 && s.visibility !== 'hidden'; });
for (const e of strokes) { const pts = samples(e);
  for (let i = 0; i < texts.length; i++) if (!covered(i, e) && pts.some(p => inside(p, tb[i])))
    out.push(['text/' + e.tagName, name(texts[i]), (e.getAttribute('stroke') || '') + (e.getAttribute('stroke-dasharray') ? ' dashed' : '')]); }
for (const c of svg.querySelectorAll('circle, ellipse')) { if (bg(c)) continue; const b = box(c);
  const R = (b[2] - b[0]) / 2, cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2;
  const outline = R >= 15 && (c.getAttribute('fill') === 'none' || +(c.getAttribute('fill-opacity') ?? 1) < 0.5);
  for (let i = 0; i < texts.length; i++) { const t = tb[i]; if (!hit(b, t) || covered(i, c)) continue;
    const inside = [[t[0],t[1]],[t[2],t[1]],[t[0],t[3]],[t[2],t[3]]].every(([x, y]) => Math.hypot(x - cx, y - cy) < R);
    if (!outline && inside && ord(c) < ord(texts[i])) continue;  // a filled badge circle with its text drawn on top
    if (outline) {
      if ([[t[0],t[1]],[t[2],t[1]],[t[0],t[3]],[t[2],t[3]]].every(([x, y]) => Math.hypot(x - cx, y - cy) < R)) continue;  // inside the ring
      const nx = Math.max(t[0], Math.min(cx, t[2])), ny = Math.max(t[1], Math.min(cy, t[3]));
      if (Math.hypot(nx - cx, ny - cy) > R) continue; }  // outside the ring
    out.push(['text/circle', name(texts[i]), (c.getAttribute('fill') || '') + ' @' + b.map(Math.round)]); } }
for (const r of svg.querySelectorAll('rect')) { const b = box(r); const s = getComputedStyle(r);
  if (s.stroke === 'none' || parseFloat(s.strokeWidth) === 0) continue;
  for (let i = 0; i < texts.length; i++) { const t = tb[i];
    if (!hit(b, t) || covered(i, r)) continue;
    if (!(t[0] >= b[0] && t[2] <= b[2] && t[1] >= b[1] && t[3] <= b[3]))
      out.push(['text/rect-edge', name(texts[i]), (r.getAttribute('stroke') || '') + ' @' + b.map(Math.round)]); } }
document.body.innerHTML = '<pre id=r>' + JSON.stringify(out).replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</pre>';
"""


def find_chrome() -> str:
    cands = [os.environ.get("CHROME", "")] + WIN_PATHS
    for c in cands:
        if c and Path(c).exists():
            return c
    for n in ("google-chrome", "chromium", "chromium-browser", "msedge"):
        if shutil.which(n):
            return shutil.which(n)
    raise FileNotFoundError("no Chrome/Edge found ($CHROME, Windows paths, PATH)")


def overlaps(svg_text: str, chrome: str | None = None) -> list[list[str]]:
    """Every overlap in one SVG document, as [kind, text, obstacle]."""
    chrome = chrome or find_chrome()
    body = re.sub(r"<\?xml[^>]*\?>", "", svg_text)
    fd, tmp = tempfile.mkstemp(suffix=".html")
    os.close(fd)
    try:
        Path(tmp).write_text(f"<!doctype html><html><body>{body}<script>{JS}</script></body></html>",
                             encoding="utf-8")
        r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--dump-dom",
                            Path(tmp).as_uri()], capture_output=True, text=True,
                           encoding="utf-8", timeout=180)
    finally:
        os.remove(tmp)
    m = re.search(r'<pre id="?r"?>(.*?)</pre>', r.stdout, re.S)
    if not m:  # the page script never finished: a broken check, never a pass
        raise RuntimeError(f"no result from Chrome (exit {r.returncode}): {r.stderr[-400:]}")
    return json.loads(html.unescape(m.group(1)))


def self_check() -> None:
    chrome = find_chrome()
    # planted bugs: the checker must see each kind, and a clean drawing must pass
    head = '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="120" font-size="14">'
    clean = head + '<circle cx="20" cy="20" r="4" stroke="#000"/><text x="40" y="25">A1</text></svg>'
    assert overlaps(clean, chrome) == [], "clean drawing reported an overlap"
    planted = {
        "text/text": '<text x="10" y="50">HELLO</text><text x="20" y="52">WORLD</text>',
        "text/line": '<line x1="0" y1="45" x2="300" y2="45" stroke="#000"/><text x="10" y="50">LINE</text>',
        "text/circle": '<circle cx="20" cy="45" r="5" stroke="#000"/><text x="10" y="50">HOLE</text>',
        "text/rect-edge": '<rect x="30" y="30" width="100" height="40" fill="none" stroke="#000"/>'
                          '<text x="10" y="55">EDGE</text>',
    }
    for kind, frag in planted.items():
        got = [o[0] for o in overlaps(head + frag + "</svg>", chrome)]
        assert kind in got, f"planted {kind} not caught (got {got})"
    # a white tag drawn over the line hides it (the pack diagram's wire tags)
    tag = head + ('<line x1="0" y1="45" x2="300" y2="45" stroke="#000"/>'
                  '<rect x="5" y="35" width="60" height="20" fill="#fff"/><text x="10" y="50">TAG</text></svg>')
    assert overlaps(tag, chrome) == [], "text on an opaque tag was flagged"
    # a number drawn on its own filled badge circle (the build guide's step numbers) is clean
    badge = head + '<circle cx="60" cy="60" r="26" fill="#1f4e79"/><text x="60" y="70" font-size="30" text-anchor="middle">5</text></svg>'
    assert overlaps(badge, chrome) == [], "text on its own filled badge circle was flagged"
    # the real diagrams
    for t in TARGETS:
        res = overlaps((ROOT / t).read_text(encoding="utf-8"), chrome)
        assert not res, f"{t}: {len(res)} overlap(s), first: {' | '.join(res[0])}"


def main(argv=None) -> int:
    files = (argv if argv is not None else sys.argv[1:]) or [str(ROOT / t) for t in TARGETS]
    try:
        chrome = find_chrome()
    except FileNotFoundError as e:
        print(f"SKIP {e}")
        return 2
    total = 0
    for f in files:
        res = overlaps(Path(f).read_text(encoding="utf-8"), chrome)
        total += len(res)
        print(f"{'PASS' if not res else 'FAIL'} {Path(f).name}: {len(res)} overlap(s)")
        for o in res:
            print("   ", " | ".join(o))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
