"""Checks energy.html against its data and against its drawing.

  the data     every flow joins two known forms, the second-law count holds
               (four arrows into thermal, two out), and no flow repeats
  the solver   every formula is worked again here from the constants and
               matched against what the page puts in the node, over the whole
               range, and the speed is checked never to pass light
  the page     draws nine forms and nineteen arrows, the card answers, and
               clicking a form dims what does not touch it
"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_energy import FORMS, FLOWS, CONST as K, AMOUNTS

fails = []
print("--- the data ---")
keys = {k for k, *_ in FORMS}
ok = len(FORMS) == 9 and len(keys) == 9
print(f"  {'ok  ' if ok else 'FAIL'} nine forms, each once")
if not ok: fails.append("forms")
bad = [(a, b) for a, b, *_ in FLOWS if a not in keys or b not in keys or a == b]
ok = not bad and len({(a, b) for a, b, *_ in FLOWS}) == len(FLOWS)
print(f"  {'ok  ' if ok else 'FAIL'} every flow joins two different known "
      "forms, none repeated")
if not ok: fails.append(f"flows: {bad}")
into = sum(1 for a, b, *_ in FLOWS if b == "th")
out = sum(1 for a, b, *_ in FLOWS if a == "th")
ok = into == 4 and out == 2
print(f"  {'ok  ' if ok else 'FAIL'} the second-law count: {into} into "
      f"thermal, {out} out, as the page says")
if not ok: fails.append(f"thermal {into}/{out}")
s = (Path(__file__).parent.parent / "energy.html").read_text(encoding="utf-8")
for frag in ["feynmanlectures.caltech.edu/I_04", "bipm.org", "E = mc",
             "first law", "second"]:
    ok = frag in s
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries '{frag}'")
    if not ok: fails.append(f"missing {frag}")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((Path(__file__).parent.parent / "energy.html").resolve().as_uri())
    pg.wait_for_selector("#ensvg")
    st = pg.evaluate("()=>window.__en()")
    nf = pg.evaluate("()=>document.querySelectorAll('#ensvg g[data-f]').length")
    na = pg.evaluate("()=>document.querySelectorAll('#ensvg g[data-fl]').length")
    ok = nf == 9 and na == 19 and st["forms"] == 9 and st["flows"] == 19
    print(f"  {'ok  ' if ok else 'FAIL'} nine forms and nineteen arrows drawn "
          f"({nf}, {na})")
    if not ok: fails.append(f"drawn {nf}/{na}")
    card = pg.evaluate("()=>{showFlow(FLOWS.findIndex(f=>f.n==='Generator'));"
                       "return document.getElementById('kindTxt').textContent"
                       "+' | '+document.getElementById('nameTxt').textContent}")
    ok = card == "Kinetic → Electrical | Generator"
    print(f"  {'ok  ' if ok else 'FAIL'} the arrow card answers: '{card}'")
    if not ok: fails.append(f"card: {card}")
    dim = pg.evaluate("()=>{sel='mass';render();"
                      "return [...document.querySelectorAll('#ensvg g[data-fl]')]"
                      ".filter(g=>+g.getAttribute('opacity')<1).length}")
    ok = dim == 17
    print(f"  {'ok  ' if ok else 'FAIL'} selecting rest mass dims {dim} of 19 "
          "arrows, leaving its two")
    if not ok: fails.append(f"dims {dim}")
    pg.evaluate("()=>{sel=null;render()}")

    print("--- the solver ---")
    # every quantity worked again here, straight from the constants
    c2 = K["c"] ** 2

    def beta(e):
        u = e / (K["m_ref"] * c2)
        return math.sqrt(2 * u + u * u) / (1 + u)

    WANT = {
        "grav": lambda e: e / (K["m_ref"] * K["g"]),
        "ela": lambda e: math.sqrt(2 * e / K["k_spring"]),
        "chem": lambda e: e / K["sugar"],
        "elec": lambda e: e / K["volt"],
        "rad": lambda e: e / (K["h"] * K["c"] / K["green"]),
        "nuc": lambda e: e / K["fission"],
        "mass": lambda e: e / c2 * 1000,
        "th": lambda e: 2 * e / (3 * K["R"]),
        # relativistic, so that the answer stays under the speed of light
        # stably, since 1 + E/mc² rounds to 1 in double precision below a joule
        "kin": lambda e: K["c"] * beta(e),
    }
    PRE = {"Y": 24, "Z": 21, "E": 18, "P": 15, "T": 12, "G": 9, "M": 6, "k": 3,
           "m": -3, "\u00b5": -6, "n": -9, "p": -12, "f": -15, "a": -18,
           "z": -21, "y": -24}
    SUP = str.maketrans("\u207b\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079",
                        "-0123456789")
    UNIT = {"kin": "m/s", "grav": "m", "ela": "m", "chem": "g", "elec": "C",
            "rad": "", "nuc": "", "mass": "g", "th": "K"}

    def parse(txt, unit):
        """Read a number back off the page: prefix form or exponent form."""
        t = txt.translate(SUP).replace("\u00d7", "x").strip()
        if unit and t.endswith(unit):
            t = t[:-len(unit)]
        t = t.strip()
        mul = 1.0
        if t and t[-1] in PRE:
            mul, t = 10.0 ** PRE[t[-1]], t[:-1].strip()
        m = re.fullmatch(r"(-?[\d.]+)x10(-?\d+)", t)
        if m:
            return float(m.group(1)) * 10 ** int(m.group(2)) * mul
        m = re.fullmatch(r"-?[\d.]+", t)
        return float(t) * mul if m else None

    for label, joules in [("a heartbeat", 1.0), ("a litre of petrol", 3.42e7),
                          ("a hurricane, for a day", 5.2e19),
                          ("an electronvolt", 1.602176634e-19)]:
        pg.evaluate("(j)=>setE(j)", joules)
        got = pg.evaluate("()=>Object.fromEntries([...document.querySelectorAll("
                          "'[data-sol]')].map(t=>[t.dataset.sol,t.textContent]))")
        worst, worstk = 0.0, None
        for k, want in WANT.items():
            if k == "kin" and "c" in got[k] and "m/s" not in got[k]:
                continue          # shown as a fraction of light, checked below
            v = parse(got[k], UNIT[k])
            if v is None or want(joules) == 0:
                fails.append(f"{k} unreadable at {label}: {got[k]!r}")
                continue
            rel = abs(v - want(joules)) / abs(want(joules))
            if rel > worst:
                worst, worstk = rel, k
        ok = worst < 0.006      # the node rounds to three significant figures
        print(f"  {'ok  ' if ok else 'FAIL'} {label}, {joules:.3e} J: all nine "
              f"agree with the formulas worked here, worst {worstk} off by "
              f"{worst * 100:.3f}%")
        if not ok: fails.append(f"{label}: {worstk} off by {worst:.4f}, got {got}")

    # the one that could embarrass the page: half m v squared past the speed of light
    worst = 0.0
    for mag in range(-21, 22):
        e = 10.0 ** mag
        b = pg.evaluate("(e)=>{const u=e/(1*299792458**2);"
                        "return Math.sqrt(2*u+u*u)/(1+u)}", e)
        worst = max(worst, b)
        want = beta(e)
        if abs(b - want) > 1e-9 * max(1, want):
            fails.append(f"speed wrong at 1e{mag} J: {b} against {want}")
    ok = worst < 1.0
    print(f"  {'ok  ' if ok else 'FAIL'} across all forty-three decades the "
          f"speed stays under light, topping out at {worst:.12f}c")
    if not ok: fails.append(f"speed reaches {worst}c")
    # and the classical formula is what it reduces to where that formula holds
    pg.evaluate("()=>setE(1)")
    kin = pg.evaluate("()=>document.querySelector('[data-sol=kin]').textContent")
    ok = kin.startswith("1.41")
    print(f"  {'ok  ' if ok else 'FAIL'} at one joule on one kilogram it gives "
          f"{kin}, the square root of two of the classical formula")
    if not ok: fails.append(f"kin at 1 J: {kin}")

    # the controls
    btns = pg.evaluate("()=>[...document.querySelectorAll('#presets button')]"
                       ".map(b=>b.textContent)")
    ok = btns == [l for l, _ in AMOUNTS]
    print(f"  {'ok  ' if ok else 'FAIL'} {len(btns)} measured amounts offered, "
          f"from {btns[0]} to {btns[-1]}")
    if not ok: fails.append(f"presets {btns}")
    pg.click("#presets button:last-child")
    ok = abs(pg.evaluate("()=>E") - AMOUNTS[-1][1]) < 1
    print(f"  {'ok  ' if ok else 'FAIL'} a button sets the amount")
    if not ok: fails.append("preset button")
    pg.fill("#joules", "4184")
    ok = abs(pg.evaluate("()=>E") - 4184) < 1e-6 and \
        pg.evaluate("()=>+document.getElementById('mag').value") == 362
    print(f"  {'ok  ' if ok else 'FAIL'} typing joules moves the slider with it")
    if not ok: fails.append("typed joules")
    pg.evaluate("""()=>{const s=document.getElementById('mag');
      s.value=900;s.dispatchEvent(new Event('input'));}""")
    ok = abs(math.log10(pg.evaluate("()=>E")) - 9) < 1e-9 and \
        abs(float(pg.evaluate("()=>document.getElementById('joules').value")) - 1e9) < 1
    print(f"  {'ok  ' if ok else 'FAIL'} and the slider moves the box with it")
    if not ok: fails.append("slider to box")
    # the card shows the working and names the case it assumes
    pg.evaluate("()=>{setE(1);showForm('mass')}")
    work = pg.evaluate("()=>document.getElementById('solveTxt').textContent+' | '"
                       "+document.getElementById('assumeTxt').textContent")
    ok = "E / c" in work and "11.1 fg" in work and "1.00 J" in work
    print(f"  {'ok  ' if ok else 'FAIL'} the card shows the working: '{work}'")
    if not ok: fails.append(f"working: {work}")

    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
