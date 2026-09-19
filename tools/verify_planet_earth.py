"""Check planet-earth-species.html against Brian's table and its drawing.

  the data     137 rows over eleven episodes, 121 distinct taxa, fourteen
               of them in more than one episode and two of those in three;
               the per-episode counts are his; every row carries a rank, a
               group, a location and a working Wikipedia link; the
               episodes are numbered as the BBC broadcast them, with the
               streaming numbers recorded alongside
  the places   every row has coordinates and a precision; every region
               centroid carries a note saying how it was chosen; no marine
               row sits on land in the shared coastline raster
  the statuses set on every species and subspecies row and on no other;
               the five subspecies say which taxon was actually assessed
  the drawing  the page opens on the map with all 137 marks; the episode,
               group and above-species controls each cut it down by the
               right amount; a mark answers where the data says it is; the
               eleven panels list every row; the repeats view draws the
               fourteen; no label overlaps another; no script errors
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from planet_earth_data import EPISODES, ROWS as SRC, RANKED, ABOVE, NON_TAXON
from planet_earth_iucn import IUCN
import enrich_planet_earth as E

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "planet-earth-species.html"
DATA = json.loads((ROOT / "tools" / "data" / "planet-earth-species.json").read_text())
rows = DATA["rows"]
fails = []

# the counts Brian gave, which nothing downstream may quietly change
HIS = {"rows": 137, "taxa": 121, "repeats": 14, "in_three": 2, "above_and_non": 29}
PER_EPISODE = {"From Pole to Pole": 13, "Mountains": 12, "Fresh Water": 14, "Caves": 10,
               "Deserts": 10, "Ice Worlds": 10, "Great Plains": 14, "Jungles": 10,
               "Shallow Seas": 13, "Seasonal Forests": 16, "Ocean Deep": 15}


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
taxa = Counter(r["scientific"] for r in rows)
reps = {s: n for s, n in taxa.items() if n > 1}
check(len(rows) == HIS["rows"], f"{HIS['rows']} rows", f"{len(rows)}")
check(len(taxa) == HIS["taxa"], f"{HIS['taxa']} distinct taxa", f"{len(taxa)}")
check(len(reps) == HIS["repeats"], f"{HIS['repeats']} taxa in more than one episode", f"{len(reps)}")
three = sorted(s for s, n in reps.items() if n == 3)
check(three == ["Canis lupus", "Loxodonta africana"], "the wolf and the African bush elephant are the two in three episodes", f"{three}")
got = {e["title"]: sum(1 for r in rows if r["episode"] == e["episode"]) for e in DATA["episodes"]}
check(got == PER_EPISODE, "the per-episode counts are his", f"{ {k: v for k, v in got.items() if PER_EPISODE.get(k) != v} }")
check([e["episode"] for e in DATA["episodes"]] == list(range(1, 12)), "eleven episodes numbered 1 to 11")
alt = {e["title"]: e["streaming_episode"] for e in DATA["episodes"] if e["streaming_episode"] != e["episode"]}
check(alt == {"Jungles": 9, "Shallow Seas": 10, "Seasonal Forests": 8},
      "the three episodes the streaming order moves carry both numbers", f"{alt}")
check(all(r["episode_title"] == next(e["title"] for e in DATA["episodes"] if e["episode"] == r["episode"]) for r in rows),
      "every row's title matches its episode number")
above = [r for r in rows if r["rank"] in ABOVE]
non = [r for r in rows if r["rank"] in NON_TAXON]
check(len(above) + len(non) == HIS["above_and_non"], f"{HIS['above_and_non']} rows above species level, the three non-taxa included",
      f"{len(above)} + {len(non)}")
check(sorted(r["name"] for r in non) == ["Corals", "Snottites", "Vent bacteria"],
      "the three that are not taxa are the snottites, the vent bacteria and the corals")
check(all(r["rank"] in RANKED + ABOVE + NON_TAXON for r in rows), "every row carries a rank from his list")
check(all(r["group"] in ("mammal", "bird", "reptile", "amphibian", "fish", "invertebrate",
                         "plant", "fungus", "bacteria") for r in rows), "every row carries a group from his list")
check(all(r["location"] and r["name"] and r["scientific"] for r in rows), "every row has a name, a scientific name and a location")
check(all(r["wikipedia"].startswith("https://en.wikipedia.org/wiki/") for r in rows), "every row links to Wikipedia")
# the table itself, transcribed: no row invented, none dropped
flat = sorted((t, n, s, loc) for _, t, _ in EPISODES for n, s, _, _, _, loc, _ in SRC[t])
check(sorted((r["episode_title"], r["name"], r["scientific"], r["location"]) for r in rows) == flat,
      "the file is his table and nothing else")

print("--- the places ---")
check(all(r["lat"] is not None and r["lon"] is not None for r in rows), "every row has coordinates")
check(all(-90 <= r["lat"] <= 90 and -180 <= r["lon"] <= 180 for r in rows), "every coordinate is on the globe")
check(all(r["precision"] in ("site", "region") for r in rows), "every row is marked site or region")
check(all(r["place_note"] for r in rows if r["precision"] == "region"),
      "every region centroid says how it was chosen")
check(all(r["place_source"] or r["place_note"] for r in rows),
      "every coordinate names either the article it came from or the reasoning behind it")
check(E.check(DATA), "no marine row sits on land in the shared coastline raster")

print("--- the statuses ---")
have = [r for r in rows if r.get("iucn")]
check(all(r["rank"] in RANKED for r in have), "a status is set only on a species or a subspecies row")
check(len(have) == sum(1 for r in rows if r["rank"] in RANKED), "every species and subspecies row has one")
check(all(r.get("iucn") is None for r in rows if r["rank"] not in RANKED),
      "nothing above species level carries a status")
check(all(r["iucn"] in ("LC", "NT", "VU", "EN", "CR", "NE") for r in have), "every category is a Red List category")
subs = [r for r in rows if r["rank"] == "subspecies"]
check(all(r.get("iucn_note") for r in subs), "every subspecies row says which taxon the assessment covers",
      f"{[r['name'] for r in subs if not r.get('iucn_note')]}")
check(all("2026-1" in r["iucn_source"] and r["iucn_checked"] for r in have), "every status cites the Red List version and the date checked")
check(IUCN["Chelonia mydas"][0] == "LC" and IUCN["Loxodonta africana"][0] == "EN"
      and IUCN["Capra walie"][0] == "CR" and IUCN["Camelus dromedarius"][0] == "NE",
      "the spot checks hold: green turtle LC, African bush elephant EN, walia ibex CR, dromedary not evaluated")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1200})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#map")
    pg.wait_for_function("()=>window.__pe().land")

    def st(q=None):
        return pg.evaluate("(q)=>window.__pe(q)", q)

    def overlaps(sel):
        boxes = pg.evaluate("(sel)=>[...document.querySelectorAll(sel)].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})", sel)
        return sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes))
                   if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2]
                   and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])

    s = st()
    check(s["view"] == "map" and s["drawn"] == 137, f"opens on the map with all 137 marks", f"{s['drawn']}")
    check("137 appearances" in s["card"] and "121" not in s["kind"], "the opening card counts the marks")
    check("centroids" in s["card"] or "region" in s["card"], "the opening card says how many marks are centroids")
    # the map is painted, land and sea
    sah = st({"pixel": [int((10 + 180) / 360 * 980), int((90 - 22) / 180 * 490)]})["rgb"]
    atl = st({"pixel": [int((-35 + 180) / 360 * 980), int((90 - 40) / 180 * 490)]})["rgb"]
    check(sah[0] > 40 and atl[0] < 25, "the map is painted: the Sahara as land, the mid-Atlantic as sea", f"{sah} {atl}")
    # a mark answers where the data says it is
    ok = True
    for i, r in enumerate(rows):
        at = st({"row": i})["at"]
        hit = st({"px": at})
        if hit["hit"] is None or rows[hit["hit"]]["lat"] != r["lat"] or rows[hit["hit"]]["lon"] != r["lon"]:
            ok = False
    check(ok, "every mark answers at its own coordinates")
    # rows sharing a place fan out rather than hiding one another
    shared = {}
    for i, r in enumerate(rows):
        shared.setdefault((r["lat"], r["lon"]), []).append(i)
    multi = [v for v in shared.values() if len(v) > 1]
    spread = all(st({"row": i})["at"] != st({"row": j})["at"] for v in multi for i in v for j in v if i < j)
    check(spread, f"the {sum(len(v) for v in multi)} rows that share a place fan out around it")
    # the controls
    pg.click('#epCtl button[data-e="4"]')
    pg.wait_for_timeout(120)
    s = st()
    check(s["ep"] == 4 and s["drawn"] == 10 and "Caves" in s["name"], "the episode control: Caves, ten marks", f"{s['drawn']}")
    pg.click('#epCtl button[data-e="0"]')
    pg.click('#grpCtl button[data-g="bird"]')
    pg.wait_for_timeout(120)
    s = st()
    check(s["grp"] == "bird" and s["drawn"] == 22, "the group control: 22 bird marks", f"{s['drawn']}")
    pg.click('#grpCtl button[data-g=""]')
    pg.click("#openBtn")
    pg.wait_for_timeout(120)
    s = st()
    check(not s["showOpen"] and s["drawn"] == 137 - 29, "the toggle hides the 29 above species level", f"{s['drawn']}")
    check("hidden" in pg.inner_text("#openBtn"), "and says so")
    pg.click("#openBtn")
    pg.wait_for_timeout(120)
    check(st()["drawn"] == 137, "and puts them back")
    # a card for a known row
    i = next(i for i, r in enumerate(rows) if r["name"] == "Snottites")
    st({"show": i})
    s = st()
    check("Snottites" in s["name"] and "Caves" in s["kind"] and "not a taxon" in s["card"]
          and "Cueva de Villa Luz" in s["card"], "the snottites: episode 4, not a taxon, Cueva de Villa Luz")
    check("does not assess" in s["body"] or "carries none" in s["body"], "and the card says why it has no status")
    i = next(i for i, r in enumerate(rows) if r["name"] == "Amur leopard" and r["episode"] == 1)
    st({"show": i})
    s = st()
    check("Vulnerable" in s["card"] and "Panthera pardus" in s["card"] and "not the subspecies" in s["card"],
          "the Amur leopard shows the species assessment and says it is the species'")
    check("10 Seasonal Forests" in s["card"], "and says it turns up again in Seasonal Forests", s["card"][:200])
    i = next(i for i, r in enumerate(rows) if r["name"] == "Wolf" and r["episode"] == 1)
    st({"show": i})
    s = st()
    check("6 Ice Worlds, 7 Great Plains" in s["card"], "the wolf lists its other two episodes", s["card"][:200])
    i = next(i for i, r in enumerate(rows) if r["name"] == "Figs")
    st({"show": i})
    s = st()
    check("genus" in s["card"] and "a region" in s["card"] and "equatorial rainforest" in s["card"],
          "the figs: a genus, placed at a centroid the card explains")
    # the episodes
    pg.click('#views button[data-v="episodes"]')
    pg.wait_for_timeout(200)
    s = st()
    check(s["view"] == "episodes" and s["panels"] == 11 and s["entries"] == 137,
          "eleven panels listing all 137 rows", f"{s['panels']} panels, {s['entries']} entries")
    check(pg.inner_text('#eps .ep[data-ep="8"] h3').strip().startswith("8 Jungles"), "episode 8 is Jungles")
    check("episode 9 on some apps" in pg.inner_text('#eps .ep[data-ep="8"] .alt'),
          "and its panel gives the streaming number", pg.inner_text('#eps .ep[data-ep="8"] .alt'))
    check(pg.eval_on_selector_all('#eps .ep li.open', "e=>e.length") == 29,
          "the 29 above species level are drawn open in the panels")
    pg.click('#eps .ep[data-ep="10"] h3')
    pg.wait_for_timeout(100)
    s = st()
    check("Seasonal Forests" in s["name"] and "16 appearances" in s["card"] and "numbered 8" in s["card"],
          "the Seasonal Forests panel: 16 named, numbered 8 on some apps")
    # the repeats
    pg.click('#views button[data-v="repeats"]')
    pg.wait_for_timeout(250)
    s = st()
    check(s["view"] == "repeats" and s["reprows"] == 14, "the repeats view draws fourteen taxa", f"{s['reprows']}")
    check("Fourteen" in s["name"] and "107 are filmed once" in s["card"], "and says what the rest of the series does")
    pg.evaluate("()=>document.querySelector('#rsvg g[data-rep=\"Canis lupus\"]').dispatchEvent(new PointerEvent('pointermove',{bubbles:true}))")
    pg.wait_for_timeout(120)
    s = st()
    check("Wolf" in s["name"] and "3 episodes" in s["kind"]
          and "1 From Pole to Pole, 6 Ice Worlds, 7 Great Plains" in s["card"],
          "the wolf's line: three episodes, named", s["card"][:200])
    check(overlaps("#rsvg text") == 0, "no two labels overlap on the repeats", f"{overlaps('#rsvg text')}")
    # the rotated episode titles are skipped by getBBox, so check them on screen
    clash = pg.evaluate("""()=>{const b=[...document.querySelectorAll('#rsvg text')].map(t=>t.getBoundingClientRect());
      let n=0; for(let i=0;i<b.length;i++) for(let j=i+1;j<b.length;j++)
        if(b[i].left<b[j].right&&b[j].left<b[i].right&&b[i].top<b[j].bottom&&b[j].top<b[i].bottom) n++;
      return n;}""")
    check(clash == 0, "nor do the rotated episode titles overlap anything", f"{clash}")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print("--- the copy ---")
html = PAGE.read_text(encoding="utf-8")
check("—" not in html, "no em dashes")
check("<script src" not in html and 'rel="stylesheet"' not in html and "@import" not in html,
      "no dependencies beyond what the page carries itself")
am = subprocess.run([sys.executable, str(ROOT / "tools" / "americanize.py"), "--check"],
                    capture_output=True, text=True).stdout
check("planet-earth-species.html" not in am, "americanize.py finds nothing to change")
check(re.search(r"\bstreaming\b", html) and re.search(r"\bBBC broadcast", html),
      "the page itself explains the two numberings")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for x in fails:
        print("  -", x)
    sys.exit(1)
print("everything squares")
