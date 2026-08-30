#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate chihuahua.html: the Chihuahua state map, in Spanish, in the
same form as the US state pages.

Geometry: CONABIO municipal boundaries via the PhantomInsights
mexico-geojson mirror (cached at /tmp/geo/chihuahua.json); municipal
populations from INEGI's Censo 2020 via Wikipedia's municipalities list
(cached at /tmp/geo/mun_pop.json); rivers and lakes from Natural Earth.
The page template is imported from build_states and translated.

Usage: python3 build_chihuahua.py   (run build_states first)
"""

import json
import unicodedata
from pathlib import Path

from shapely.geometry import shape, box
from shapely.ops import unary_union

import build_states_data as gd          # merc, rings, lines, W
from build_states import HTML, refs_html  # template (import rebuilds US pages)

ROOT = Path(__file__).parent.parent
OUT_DATA = Path(__file__).parent / "data" / "states" / "mx08.json"


def deaccent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn").strip()


def build_data():
    fc = json.loads(Path("/tmp/geo/chihuahua.json").read_text())
    pops = json.loads(Path("/tmp/geo/mun_pop.json").read_text())
    pops_n = {deaccent(k): v for k, v in pops.items()}
    shapes = {}
    for f in fc["features"]:
        g = shape(f["geometry"]).buffer(0)
        shapes[f["properties"]["CVEGEO"]] = (f["properties"]["NOMGEO"], g)
    outline = unary_union([g for _, g in shapes.values()]).buffer(0)
    minx, miny, maxx, maxy = outline.bounds
    VP, pad = 0.55, 0.90
    clipbox = box(minx - pad, miny - pad, maxx + pad, maxy + pad)
    mx0, my0 = gd.merc(minx - VP, miny - VP)
    mx1, my1 = gd.merc(maxx + VP, maxy + VP)
    W = gd.W
    H = round(W * (my1 - my0) / (mx1 - mx0), 1)

    def XY(lon, lat):
        mx, my = gd.merc(lon, lat)
        return (round((mx - mx0) / (mx1 - mx0) * W, 1),
                round((my1 - my) / (my1 - my0) * H, 1))

    def enc_rings(geom, tol):
        return [[XY(x, y) for x, y in ring]
                for ring in gd.rings(geom.simplify(tol))]

    data = {"name": "Chihuahua", "fips": "mx08", "W": W, "H": H,
            "m": [mx0, my0, mx1, my1],
            "ll": [minx - VP, miny - VP, maxx + VP, maxy + VP]}
    data["outline"] = enc_rings(outline, 0.008)
    data["counties"] = []
    missing = []
    for cid, (name, g) in sorted(shapes.items()):
        key = deaccent(name)
        # Batopilas was renamed "Batopilas de Manuel Gómez Morín" in 2021
        p = pops_n.get(key) or pops_n.get(key.split(" de manuel")[0])
        if p is None:
            missing.append(name)
        data["counties"].append({"n": name, "fips": cid, "p": p,
                                 "r": enc_rings(g, 0.004)})
    if missing:
        print("ATTENTION municipios sin poblacion:", missing)

    rivers_fc = json.loads((gd.GEO / "rivers.geojson").read_text())
    rivers_na_fc = json.loads((gd.GEO / "rivers_na.geojson").read_text())
    lakes_fc = json.loads((gd.GEO / "lakes.geojson").read_text())
    seen = {}
    for fc2 in (rivers_fc, rivers_na_fc):
        for f in fc2["features"]:
            if not f.get("geometry"):
                continue
            name = (f["properties"].get("name") or "").strip()
            g = shape(f["geometry"])
            if not g.intersects(clipbox):
                continue
            clipped = g.intersection(clipbox)
            if clipped.is_empty:
                continue
            key = name or f"~{round(clipped.length, 4)}"
            seen[key] = seen[key].union(clipped) if key in seen else clipped
    rivers = []
    for name, g in seen.items():
        if name.startswith("~") and g.length < 0.35:
            continue
        segs = gd.lines(g.simplify(0.006))
        rivers.append({"n": "" if name.startswith("~") else name,
                       "s": [[XY(x, y) for x, y in seg] for seg in segs]})
    data["rivers"] = rivers
    lakes = []
    for f in lakes_fc["features"]:
        if not f.get("geometry"):
            continue
        name = (f["properties"].get("name") or "").strip()
        g = shape(f["geometry"]).buffer(0)
        if not g.intersects(clipbox):
            continue
        inter = g.intersection(clipbox)
        if inter.is_empty or (inter.area < 0.0015 and not name):
            continue
        lakes.append({"n": name, "r": enc_rings(inter, 0.004)})
    data["lakes"] = lakes
    OUT_DATA.write_text(json.dumps(data, separators=(",", ":")))
    print(f"wrote {OUT_DATA} ({OUT_DATA.stat().st_size:,} B): "
          f"{len(data['counties'])} municipios, {len(rivers)} rios, "
          f"{len(lakes)} lagos")
    return data


BURGUNDY = {"a": "Cross of Burgundy"}
MX = {"a": "Flag of Mexico"}

HIST_CH = {
    "eras": [
        {"y0": 1492, "y1": 1567, "l": "Rarámuri, conchos, tepehuanes, sumas y apaches", "f": None},
        {"y0": 1567, "y1": 1821, "l": "Nueva España (la Nueva Vizcaya)", "f": BURGUNDY},
        {"y0": 1821, "y1": 1824, "l": "México independiente", "f": MX},
        {"y0": 1824, "y1": 1864, "l": "Estado de Chihuahua, 1824", "f": MX},
        {"y0": 1864, "y1": 1867, "l": "Intervención francesa; Juárez gobierna desde Chihuahua", "f": {"a": "Second Mexican Empire"}},
        {"y0": 1867, "y1": 1911, "l": "La República restaurada y el porfiriato", "f": MX},
        {"y0": 1911, "y1": 1920, "l": "La Revolución; la División del Norte", "f": MX},
        {"y0": 1920, "y1": 2026, "l": "Chihuahua contemporáneo", "f": MX},
    ],
    "marks": [{"y": 1811, "l": "Hidalgo fusilado en Chihuahua"},
              {"y": 1910, "l": "Comienza la Revolución"}],
    "border": 1824,
    "nb": [
        {"n": "Nuevo México (EE. UU.)", "lat": 32.1, "lon": -107.3},
        {"n": "Texas (EE. UU.)", "lat": 31.6, "lon": -104.55},
        {"n": "Sonora", "lat": 29.6, "lon": -109.4, "v": True},
        {"n": "Sinaloa", "lat": 26.15, "lon": -108.35},
        {"n": "Durango", "lat": 25.35, "lon": -105.6},
        {"n": "Coahuila", "lat": 27.4, "lon": -103.05, "v": True},
    ],
    "pre": "decenas de miles de rarámuris, conchos, tepehuanes, sumas y "
           "apaches vivían aquí; ningún conteo colonial sobrevive.",
    "nations": [
        {"n": "Rarámuri", "src": "es.wikipedia.org/wiki/Pueblo_tarahumara", "poly": [[-108.6, 26.4], [-106.9, 26.7], [-106.8, 28.6], [-108.3, 28.4]], "lat": 27.55, "lon": -107.6, "note": "La Sierra Tarahumara; hoy el pueblo indígena más numeroso del estado."},
        {"n": "Conchos", "src": "es.wikipedia.org/wiki/Conchos_(etnia)", "poly": [[-106.5, 27.3], [-104.6, 27.6], [-104.9, 29.2], [-106.3, 28.9]], "lat": 28.25, "lon": -105.5, "note": "A lo largo del río Conchos; diezmados y asimilados durante el siglo XVIII.", "after": {"y": 1750, "t": "asimilación forzada"}},
        {"n": "Ódami (tepehuanes)", "src": "es.wikipedia.org/wiki/Tepehuanes", "poly": [[-107.4, 25.6], [-105.9, 25.8], [-106.1, 27.0], [-107.3, 26.8]], "lat": 26.3, "lon": -106.6, "note": "El sur de la sierra; la rebelión de 1616 sacudió toda la Nueva Vizcaya."},
        {"n": "Tobosos", "src": "es.wikipedia.org/wiki/Tobosos", "poly": [[-105.3, 26.6], [-103.5, 27.0], [-103.8, 28.6], [-105.0, 28.2]], "lat": 27.5, "lon": -104.4, "note": "Nómadas del Bolsón de Mapimí; desaparecen como pueblo hacia 1800.", "after": {"y": 1800, "t": "exterminio y asimilación"}},
        {"n": "Sumas y janos", "src": "es.wikipedia.org/wiki/Suma_(etnia)", "poly": [[-108.9, 29.8], [-107.0, 30.0], [-107.3, 31.6], [-108.8, 31.4]], "lat": 30.6, "lon": -108.0, "note": "Pueblos del noroeste, absorbidos por las misiones y por los apaches.", "after": {"y": 1850, "t": "asimilación"}},
        {"n": "Ndee (apaches)", "src": "es.wikipedia.org/wiki/Apache", "poly": [[-107.5, 29.6], [-104.8, 30.2], [-105.4, 31.7], [-107.6, 31.5]], "lat": 30.7, "lon": -106.1, "note": "Chiricahuas y mescaleros; un siglo de guerra en la frontera de presidios.", "after": {"y": 1886, "t": "deportación y exterminio"}},
        {"n": "Guarijíos", "src": "es.wikipedia.org/wiki/Guarij%C3%ADo", "poly": [[-108.9, 27.0], [-108.1, 27.2], [-108.3, 28.3], [-108.9, 28.1]], "lat": 27.65, "lon": -108.5, "note": "Entre la sierra y Sonora."},
    ],
    "events": [
        {"y": 1567, "t": "set", "n": "Santa Bárbara", "lat": 26.81, "lon": -105.82, "note": "La primera villa española en el actual Chihuahua, tras las minas.", "src": "es.wikipedia.org/wiki/Santa_B%C3%A1rbara_(Chihuahua)"},
        {"y": 1616, "t": "rem", "n": "Rebelión tepehuana", "lat": 26.5, "lon": -106.4, "note": "1616 a 1618: la guerra tepehuana; la represión mata a miles.", "src": "en.wikipedia.org/wiki/Tepehu%C3%A1n_Revolt"},
        {"y": 1631, "t": "set", "n": "Parral", "pp": [[2020, 104836]], "lat": 26.93, "lon": -105.66, "note": "Real de minas de 1631, capital informal de la Nueva Vizcaya.", "src": "es.wikipedia.org/wiki/Hidalgo_del_Parral"},
        {"y": 1659, "t": "set", "n": "Paso del Norte (Ciudad Juárez)", "pp": [[1900, 8218], [1930, 39669], [1950, 122566], [1960, 262119], [1970, 407370], [1980, 544496], [1990, 789522], [2000, 1187275], [2010, 1321004], [2020, 1512450]], "lat": 31.73, "lon": -106.48, "note": "La misión de Guadalupe en el vado del río Bravo; hoy Ciudad Juárez.", "src": "es.wikipedia.org/wiki/Ciudad_Ju%C3%A1rez"},
        {"y": 1680, "t": "rem", "n": "Rebeliones conchas", "lat": 28.7, "lon": -105.3, "note": "Décadas de levantamientos conchos y tobosos contra encomiendas y misiones.", "src": "es.wikipedia.org/wiki/Conchos_(etnia)"},
        {"y": 1709, "t": "cap", "n": "Chihuahua", "pp": [[1900, 30405], [1930, 45595], [1950, 86961], [1960, 150430], [1970, 257027], [1980, 385603], [1990, 516153], [2000, 657876], [2010, 809232], [2020, 925762]], "lat": 28.63, "lon": -106.08, "note": "San Felipe el Real de Chihuahua, 1709; capital del estado desde 1824.", "src": "es.wikipedia.org/wiki/Chihuahua_(ciudad)"},
        {"y": 1759, "t": "set", "n": "Ojinaga", "lat": 29.56, "lon": -104.42, "note": "El presidio del norte en la junta de los ríos.", "src": "es.wikipedia.org/wiki/Ojinaga"},
        {"y": 1778, "t": "set", "n": "Namiquipa", "lat": 29.25, "lon": -107.42, "note": "Villa presidial fundada por Teodoro de Croix en 1778.", "src": "es.wikipedia.org/wiki/Namiquipa"},
        {"y": 1849, "t": "rem", "n": "Contratos de cabelleras", "lat": 29.9, "lon": -106.6, "note": "El estado paga recompensas por cabelleras apaches; caen también rarámuris y vecinos.", "src": "en.wikipedia.org/wiki/Apache%E2%80%93Mexico_Wars"},
        {"y": 1886, "t": "rem", "n": "Fin de la guerra apache", "lat": 31.0, "lon": -108.2, "note": "Con la rendición de Gerónimo terminan dos siglos de guerra en la frontera.", "src": "en.wikipedia.org/wiki/Geronimo"},
        {"y": 1892, "t": "rem", "n": "Tomóchic", "lat": 28.35, "lon": -107.84, "note": "El ejército arrasa el pueblo alzado; mueren casi todos sus defensores.", "src": "es.wikipedia.org/wiki/Rebeli%C3%B3n_de_Tom%C3%B3chic"},
        {"y": 1904, "t": "set", "n": "Cuauhtémoc", "lat": 28.41, "lon": -106.87, "note": "San Antonio de los Arenales; colonias menonitas desde 1922.", "src": "es.wikipedia.org/wiki/Cuauht%C3%A9moc_(Chihuahua)"},
        {"y": 1933, "t": "set", "n": "Delicias", "lat": 28.19, "lon": -105.47, "note": "Ciudad de riego fundada en 1933 sobre los canales del Conchos.", "src": "es.wikipedia.org/wiki/Delicias_(Chihuahua)"},
    ],
    "census": [[1895, 266831], [1900, 327784], [1910, 405707], [1921, 401622],
               [1930, 491792], [1940, 623944], [1950, 846414], [1960, 1226793],
               [1970, 1612525], [1980, 2005477], [1990, 2441873],
               [2000, 3052907], [2010, 3406465], [2020, 3741869]],
    "native": [],
    "cities": [],
    "unis": [],
    "geo": {"hp": {"n": "Cerro Mohinora", "el": "3,300 m", "lat": 25.95, "lon": -107.04}},
    "refs": [],
}

REFS_ES = [
    ("Natural Earth, ríos y lagos a 10m.", "https://www.naturalearthdata.com/"),
    ("Límites municipales: CONABIO, vía el espejo mexico-geojson.", "https://github.com/PhantomInsights/mexico-geojson"),
    ("Población municipal y estatal: censos del INEGI, 1895 a 2020.", "https://www.inegi.org.mx/programas/ccpv/2020/"),
    ("Relieve: Mapzen/AWS Terrain Tiles (Open Data).", "https://registry.opendata.aws/terrain-tiles/"),
    ("Banderas: la imagen del artículo de Wikipedia de cada era, cargada al vuelo.", "https://en.wikipedia.org/"),
    ("Series urbanas de Ciudad Juárez y Chihuahua: censos del INEGI vía los artículos de Wikipedia.", "https://es.wikipedia.org/wiki/Ciudad_Ju%C3%A1rez"),
    ("Las guerras apache-mexicanas y los contratos de cabelleras.", "https://en.wikipedia.org/wiki/Apache%E2%80%93Mexico_Wars"),
    ("La rebelión de Tomóchic, 1891 a 1892.", "https://es.wikipedia.org/wiki/Rebeli%C3%B3n_de_Tom%C3%B3chic"),
    ("El pueblo rarámuri.", "https://es.wikipedia.org/wiki/Pueblo_tarahumara"),
]

NOTE1_ES = ("El mapa es el Chihuahua real en Web Mercator: ríos y lagos de "
            "Natural Earth, límites municipales de CONABIO con la población "
            "del Censo 2020, y el relieve sombreado al vuelo con las AWS "
            "Terrain Tiles. Cada botón prende o apaga una capa; la marca "
            "bajo el cursor llena la tarjeta y un clic la fija. La frontera "
            "y los nombres vecinos aparecen desde que se trazó el límite "
            "estatal.")
NOTE2_ES = ("La línea del tiempo corre desde 1492: primero los pueblos "
            "originarios como manchas de color, territorios aproximados "
            "dibujados para orientar, luego villas, presidios, capitales y "
            "despojos año por año, mientras el panel muestra de quién fue "
            "la tierra hasta la bandera actual. Los círculos urbanos crecen "
            "de verde a amarillo y naranja al pasar los censos de 10 mil, "
            "100 mil y un millón, y los años sobre la barra saltan a los "
            "momentos clave. Los pueblos originarios siguen aquí; Native "
            "Land Digital documenta sus territorios con sus comunidades.")

# English template strings -> Spanish
TR = [
    ("&larr; Library &middot; USA", "&larr; Library &middot; M&eacute;xico"),
    ('  <button id="cWoo" class="on">Woods</button>\n', ""),
    ('  <button id="cUni">Colleges</button>\n', ""),
    ("const CH={cTer:'ter',cWoo:'woo',cRiv:'riv',cLak:'lak',cCou:'cou',cNat:'nat',cTow:'tow',cUni:'uni'};",
     "const CH={cTer:'ter',cRiv:'riv',cLak:'lak',cCou:'cou',cNat:'nat',cTow:'tow'};"),
    ("{ter:true,woo:true,", "{ter:true,woo:false,"),
    ("terrain(); woods();", "terrain();"),
    (">Terrain</button>", ">Relieve</button>"),
    (">Rivers</button>", ">R&iacute;os</button>"),
    (">Lakes</button>", ">Lagos</button>"),
    (">Counties</button>", ">Municipios</button>"),
    (">Nations</button>", ">Pueblos</button>"),
    (">Towns</button>", ">Ciudades</button>"),
    (">Play</button>", ">Correr</button>"),
    ("textContent='Play'", "textContent='Correr'"),
    ("textContent='Pause'", "textContent='Pausa'"),
    ("'loading terrain\\u2026'", "'cargando relieve\\u2026'"),
    ("'terrain unavailable'", "'relieve no disponible'"),
    ("'flag unavailable'", "'bandera no disponible'"),
    ("'No flag: the nations\\u2019 own land'", "'Sin bandera: tierra de los pueblos originarios'"),
    ("'Census (interpolated): '", "'Censo (interpolado): '"),
    ("'Colonial estimate: '", "'Estimaci\\u00f3n colonial: '"),
    ("'Before the counts: '", "'Antes de los censos: '"),
    ("'Native population (estimate): '", "'Poblaci\\u00f3n ind\\u00edgena (estimada): '"),
    ("'A nation of this land'", "'Un pueblo de esta tierra'"),
    ("' The patch is an approximate homeland, drawn for orientation.'",
     "' La mancha es un territorio aproximado, dibujado para orientar.'"),
    ("'Removal and dispossession'", "'Despojo y violencia'"),
    ("'Capital \\u00b7 '", "'Capital \\u00b7 '"),
    ("'Settlement \\u00b7 '", "'Fundaci\\u00f3n \\u00b7 '"),
    ("' Population around '", "' Poblaci\\u00f3n hacia '"),
    ("'Population around '", "'Poblaci\\u00f3n hacia '"),
    ("' (census, interpolated).'", "' (censo, interpolado).'"),
    ("'County \\u00b7 recent population'", "'Municipio \\u00b7 poblaci\\u00f3n reciente'"),
    ("'Established '+c.y+'. '", "'Creado en '+c.y+'. '"),
    ("'Population about '", "'Poblaci\\u00f3n aproximada: '"),
    ("'Founding year via Wikipedia\\u2019s county list; census figures via the Balsama county dataset, 2025'",
     "'Poblaci\\u00f3n municipal: Censo 2020 del INEGI, v\\u00eda Wikipedia'"),
    ("'Highest point'", "'Punto m\\u00e1s alto'"),
    ("'Elevation '", "'Altitud '"),
    ("A mark under the cursor lands here", "La marca bajo el cursor aparece aqu&iacute;"),
    ("City population</text>", "Poblaci&oacute;n urbana</text>"),
    ("'On the map from the first census over 10,000.'",
     "'En el mapa desde el primer censo con m\\u00e1s de 10,000.'"),
    ("'Census series via the city\\u2019s Wikipedia article'",
     "'Serie censal: art\\u00edculo de Wikipedia de la ciudad'"),
]


def main():
    data = build_data()
    hist = HIST_CH
    html = HTML
    for en, es in TR:
        assert en in html, f"missing template string: {en!r}"
        html = html.replace(en, es)
    sibs = (' <a href="mexico.html">M&eacute;xico</a>'
            ' <a href="norte-mexico.html">El norte</a>'
            ' <a href="valle-santa-maria.html">El valle del Santa Mar&iacute;a</a>')
    refs = "\n".join(f'<p>{t}\n<a href="{u}">{u}</a></p>' for t, u in REFS_ES)
    html = (html.replace("__TITLE__", "Chihuahua")
            .replace("__SIBS__", sibs)
            .replace("__NOTE1__", NOTE1_ES).replace("__NOTE2__", NOTE2_ES)
            .replace("__REFS__", refs)
            .replace("__ST__", json.dumps(data, separators=(",", ":")))
            .replace("__HIST__", json.dumps(hist, separators=(",", ":"))))
    html = html.replace("<h2 class=\"refh\">References</h2>",
                        "<h2 class=\"refh\">Referencias</h2>")
    out = ROOT / "chihuahua.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} B): {len(hist['nations'])} pueblos, "
          f"{len(hist['events'])} eventos, {len(hist['eras'])} eras")


if __name__ == "__main__":
    main()
