"""Check dna.html against the genetic code and the genome, and its drawing.

  the code     the page's table against the standard code written here in
               NCBI's compact form; 64 codons, 3 stops, 20 amino acids,
               methionine and tryptophan with one codon each; the gene
               translates to the start of beta-globin; each preset does
               what its text says (sickle: Glu to Val at 7; silent: no
               change; stop: seven amino acids; frame: a different chain)
  the genome   25 chromosomes summing to 3.09 billion base pairs and about
               20,000 genes; 19 the densest, 1 the longest, 21 the smallest
               nuclear one; the stretched length near two metres a cell
  the helix    40 pairs drawn, each base with its partner, purine with
               pyrimidine; the rungs advance 1/10.5 of a turn each; the
               pointer names a pair; the base clicks cycle A, C, G, T
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dna_data import CODE, AMINO, GENE, MUTATIONS, CHROMOSOMES, HELIX, BASES

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "dna.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


# the standard code in NCBI's form: bases in the order T C A G, first base slowest
NCBI = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
mine = {}
for i, aa in enumerate(NCBI):
    mine["TCAG"[i // 16] + "TCAG"[(i // 4) % 4] + "TCAG"[i % 4]] = aa


def translate(s):
    out = ""
    for i in range(0, len(s) - 2, 3):
        aa = mine[s[i:i + 3]]
        out += aa
        if aa == "*":
            break
    return out


print("--- the code ---")
check(len(CODE) == 64 and all(CODE[c] == mine[c] for c in mine), "the page's 64 codons match the standard code")
check(sum(1 for c in CODE.values() if c == "*") == 3 and len(set(CODE.values()) - {"*"}) == 20, "three stops and twenty amino acids")
check(sum(1 for c in CODE.values() if c == "M") == 1 and sum(1 for c in CODE.values() if c == "W") == 1, "methionine and tryptophan have one codon each")
check(all(k in AMINO for k in set(CODE.values())), "every amino acid is named")
check(len(GENE) == 90 and translate(GENE) == "MVHLTPEEKSAVTALWGKVNVDEVGGEALG", f"the gene is 30 codons and reads {translate(GENE)}, beta-globin's start")
m = {x[0]: x for x in MUTATIONS}


def mutate(k):
    _, _, i, b, _, _ = m[k]
    return GENE[:i] + b + GENE[i + 1:] if b else GENE[:i] + GENE[i + 1:]


check(translate(mutate("sickle")) == translate(GENE)[:6] + "V" + translate(GENE)[7:], "the sickle mutation turns the seventh amino acid, Glu, into Val")
check(mutate("sickle")[18:21] == "GTG" and GENE[18:21] == "GAG", "  GAG to GTG, an A to a T")
check(translate(mutate("silent")) == translate(GENE) and mutate("silent")[6:9] == "CAC", "the silent change, CAT to CAC, leaves the protein as it was")
check(translate(mutate("stop")) == "MVHLTPE*" and mutate("stop")[21:24] == "TAG", "the stop, GAG to TAG, ends the protein after seven amino acids")
fr = translate(mutate("frame"))
check(fr[:1] == "M" and fr[1:] != translate(GENE)[1:len(fr)], f"a lost base gives a different chain: {fr}")

print("--- the genome ---")
tot = sum(c[1] for c in CHROMOSOMES)
genes = sum(c[2] for c in CHROMOSOMES)
check(len(CHROMOSOMES) == 25 and abs(tot - 3.088e9) / 3.088e9 < 0.01, f"25 chromosomes, {tot / 1e9:.3f} billion base pairs in one set")
check(19000 < genes < 21000, f"{genes:,} protein-coding genes")
by = {c[0]: c for c in CHROMOSOMES}
check(max(CHROMOSOMES, key=lambda c: c[1])[0] == "1", "chromosome 1 is the longest")
check(min((c for c in CHROMOSOMES if c[0] not in ("MT",)), key=lambda c: c[1])[0] == "21", "21 the smallest in the nucleus")
check(max((c for c in CHROMOSOMES if c[0] != "MT"), key=lambda c: c[2] / c[1])[0] == "19", "19 the densest in genes")
check(by["Y"][1] < by["X"][1] / 2 and by["Y"][2] < 100, "Y is under half of X and carries few genes")
check(by["MT"][1] == 16569 and by["MT"][2] == 13, "the mitochondrial ring is 16,569 bases with 13 protein-coding genes")
check(abs(tot * 0.34e-9 - 1.05) < 0.02, f"one set stretched is {tot * 0.34e-9:.2f} m, two sets about two metres")
check(abs(HELIX["rise_nm"] * HELIX["bp_per_turn"] - HELIX["pitch_nm"]) < 0.01, "0.34 nm a step times 10.5 steps is a 3.57 nm turn")
check(all(b[2] == {"A": "T", "T": "A", "G": "C", "C": "G"}[b[0]] and b[3] == (2 if b[0] in "AT" else 3) for b in BASES), "A with T by two bonds, G with C by three")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#dsvg")
    pg.evaluate("()=>document.getElementById('spin').click()")
    pg.wait_for_timeout(100)

    def st(q=None):
        return pg.evaluate("(q)=>window.__dna(q)", q)

    s = st({"translate": GENE, "code": True})
    check(s["view"] == "helix" and s["pairs"] == 40, "opens on the helix with 40 base pairs drawn")
    check(all(s["code"][c] == mine[c] for c in mine), "the page's code table is the standard one")
    check(s["tr"] == translate(GENE), "the page translates the gene as this checker does")
    for k in m:
        check(st({"translate": mutate(k)})["tr"] == translate(mutate(k)), f"  and the {m[k][1]} the same way")
    # the rungs advance a tenth-and-a-half of a turn: the left backbone's x follows a sine of period 10.5 rungs
    xs = pg.evaluate("()=>[...document.querySelectorAll('#dsvg g[data-p] line:first-child')].map(l=>+l.getAttribute('x1'))")
    import math
    ok = all(abs((xs[i] - 300) - 60 * math.sin(i / 10.5 * 2 * math.pi + st()["turn"] * math.pi / 180)) < 0.6 for i in range(40))
    check(ok, "the left backbone winds at 10.5 pairs a turn, radius 60")
    pg.evaluate("()=>document.querySelector('#dsvg g[data-p=\"2\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check(s["hot"] == 2 and "guanine and cytosine" in s["name"] and "3 hydrogen bonds" in s["card"] and "0.68 nm along" in s["card"], "hovering the third pair: guanine and cytosine, three bonds, 0.68 nm along")
    pg.click('#views button[data-v="code"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["codons"] == 30 and s["protein"] == translate(GENE) and "beta-globin" in s["name"], "the code view: 30 codons, the protein on the card")
    pg.click('#muts button[data-m="sickle"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["mut"] == "sickle" and "Glu to Val at 7" in s["card"] and "malaria" in pg.inner_text("#bodyTxt"), "the sickle preset: Glu to Val at 7, and the malaria story")
    pg.click('#muts button[data-m="stop"]')
    pg.wait_for_timeout(150)
    s = st()
    check("ending in a stop" in s["card"] and s["protein"] == "MVHLTPE*", "the stop preset ends the chain after seven")
    pg.click("#reset")
    pg.wait_for_timeout(100)
    check(st()["seq"] == GENE, "as written restores the gene")
    pg.evaluate("()=>document.querySelector('#dsvg g[data-b=\"19\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check(s["seq"][19] == "C" and s["seq"][:19] == GENE[:19] and "Glu to Ala at 7" in s["card"], "clicking base 20 turns its A into C, and the card reads Glu to Ala at 7")
    pg.evaluate("()=>document.querySelector('#dsvg g[data-c=\"0\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    check("ATG is methionine" in st()["name"] and "AUG" in st()["card"], "hovering the first codon: ATG is methionine, read as AUG")
    pg.click('#views button[data-v="genome"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["chroms"] == 25 and "3.09 billion" in s["card"] and f"{genes:,}" in s["card"], "the genome view: 25 bars, 3.09 billion base pairs, the gene count")
    order = pg.evaluate("()=>[...document.querySelectorAll('#dsvg g[data-ch]')].map(g=>g.dataset.ch)")
    check(order[:3] == ["1", "2", "3"] and order[-1] == "MT", "sorted by number to start")
    pg.click('#sorts button[data-s="density"]')
    pg.wait_for_timeout(100)
    order = pg.evaluate("()=>[...document.querySelectorAll('#dsvg g[data-ch]')].map(g=>g.dataset.ch)")
    check(order[0] == "MT" and order[1] == "19" and order[-1] == "Y", f"by density: the mitochondrion, then 19, with Y last")
    pg.evaluate("()=>document.querySelector('#dsvg g[data-ch=\"21\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check("chromosome 21" in s["name"] and "46.7 million" in s["card"] and "234" in s["card"] and "Down" in pg.inner_text("#bodyTxt"), "hovering 21: 46.7 million bases, 234 genes, Down syndrome")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print("--- the copy ---")
html = PAGE.read_text()
check("—" not in html, "no em dashes")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for x in fails:
        print("  -", x)
    sys.exit(1)
print("everything squares")
