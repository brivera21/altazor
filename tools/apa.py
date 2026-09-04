#!/usr/bin/env python3
"""APA 7 reference formatting, shared by every builder on the site.

Entries are built with the helpers below and rendered by render(), which
emits one paragraph per reference with a hanging indent, and an optional
annotation under it saying what the source is doing on that page.

The retrieval date is fixed rather than taken from the clock, so that
rebuilding a page does not rewrite every reference. Update it when the
sources are actually checked again.
"""

import re
import urllib.parse

RETRIEVED = "September 4, 2026"
RETRIEVED_ES = "4 de septiembre de 2026"

CSS = (".refs p { padding-left:2em; text-indent:-2em; }\n"
       ".refs .ann { color:#7d7d7d; display:block; padding-left:0; "
       "text-indent:0; margin-top:2px; }")


def _title_from_url(url):
    """The article title a Wikipedia URL points at."""
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    slug = urllib.parse.unquote(slug)
    return slug.replace("_", " ")


def wiki(url, title=None):
    """A Wikipedia entry: a page that keeps changing, so no date and a
    retrieval date, per APA 7."""
    t = _auth(title or _title_from_url(url))
    return f"{t}. (n.d.). In <i>Wikipedia</i>. Retrieved {RETRIEVED}, from {url}"


def _auth(a):
    """One trailing period, never two."""
    return a[:-1] if a.endswith(".") else a


def web(author, year, title, site, url, retrieved=False):
    """A page or resource with an organisation or person behind it."""
    y = year or "n.d."
    bits = [f"{_auth(author)}. ({y}). <i>{title}</i>."]
    if site:
        bits.append(f"{site}.")
    if retrieved:
        bits.append(f"Retrieved {RETRIEVED}, from {url}")
    else:
        bits.append(url)
    return " ".join(bits)


def data(author, year, title, version, publisher, url):
    """A dataset, which APA marks as such in square brackets."""
    v = f" (Version {version})" if version else ""
    return (f"{_auth(author)}. ({year}). <i>{title}</i>{v} [Data set]. "
            f"{publisher}. {url}")


def article(authors, year, title, journal, volume, issue, pages, url):
    """A journal article."""
    iss = f"({issue})" if issue else ""
    vol = f"<i>{journal}, {volume}</i>{iss}" if volume else f"<i>{journal}</i>"
    pg = f", {pages}" if pages else ""
    return f"{_auth(authors)}. ({year}). {title}. {vol}{pg}. {url}"


def book(authors, year, title, publisher, url=None):
    tail = f" {url}" if url else ""
    return f"{_auth(authors)}. ({year}). <i>{title}</i>. {publisher}.{tail}"


def render(entries):
    """entries: an APA string, or (APA string, annotation). One <p> each."""
    out = []
    for e in entries:
        ref, ann = (e, None) if isinstance(e, str) else e
        ref = _link(ref)
        out.append(f"<p>{ref}"
                   + (f'<span class="ann">{ann}</span>' if ann else "")
                   + "</p>")
    return "\n".join(out)


def _link(ref):
    """Make every URL in a reference clickable."""
    return re.sub(r"(https?://[^\s<]+)", r'<a href="\1">\1</a>', ref)


# The non-Wikipedia sources this site draws on, written out once so every
# page cites them the same way.
SOURCES = {
    "https://www.naturalearthdata.com/": data(
        "Natural Earth", "n.d.", "Natural Earth vector, 1:10m cultural and "
        "physical layers", None, "Public domain",
        "https://www.naturalearthdata.com/"),
    "https://github.com/plotly/datasets": data(
        "Plotly", "n.d.", "United States county boundaries (GeoJSON, from the "
        "Census cartographic files)", None, "GitHub",
        "https://github.com/plotly/datasets"),
    "https://github.com/balsama/us_counties_data": data(
        "Balsama, A.", 2025, "US counties data", None, "GitHub",
        "https://github.com/balsama/us_counties_data"),
    "https://github.com/generalpiston/geojson-us-city-boundaries": data(
        "Pistone, G.", "n.d.", "GeoJSON US city boundaries (from the Census "
        "TIGER place files)", None, "GitHub",
        "https://github.com/generalpiston/geojson-us-city-boundaries"),
    "https://registry.opendata.aws/terrain-tiles/": data(
        "Mapzen &amp; Amazon Web Services", "n.d.", "Terrain tiles", None,
        "AWS Open Data Registry",
        "https://registry.opendata.aws/terrain-tiles/"),
    "https://www.mrlc.gov/": data(
        "Multi-Resolution Land Characteristics Consortium", 2021,
        "National Land Cover Database 2021 (NLCD 2021)", None,
        "U.S. Geological Survey", "https://www.mrlc.gov/"),
    "https://www.census.gov/data/tables/time-series/dec/popchange-data-text.html": data(
        "U.S. Census Bureau", "n.d.", "Population change for states and "
        "counties, decennial census", None, "U.S. Department of Commerce",
        "https://www.census.gov/data/tables/time-series/dec/popchange-data-text.html"),
    "https://native-land.ca/": web(
        "Native Land Digital", "n.d.", "Native Land", "Native Land Digital",
        "https://native-land.ca/", retrieved=True),
    "https://openlibrary.org": web(
        "Internet Archive", "n.d.", "Open Library", "Internet Archive",
        "https://openlibrary.org", retrieved=True),
    "https://glottolog.org": data(
        "Hammarström, H., Forkel, R., Haspelmath, M., &amp; Bank, S.", 2025,
        "Glottolog", "5.2.1",
        "Max Planck Institute for Evolutionary Anthropology",
        "https://glottolog.org"),
    "https://github.com/glottolog/glottolog-cldf": data(
        "Hammarström, H., Forkel, R., Haspelmath, M., &amp; Bank, S.", 2025,
        "Glottolog as CLDF", "5.2.1", "Zenodo",
        "https://github.com/glottolog/glottolog-cldf"),
    "https://iso639-3.sil.org/": web(
        "SIL International", "n.d.", "ISO 639-3 registration authority",
        "SIL International", "https://iso639-3.sil.org/", retrieved=True),
    "https://ssd.jpl.nasa.gov/planets/approx_pos.html": web(
        "Jet Propulsion Laboratory", "n.d.",
        "Approximate positions of the planets", "NASA",
        "https://ssd.jpl.nasa.gov/planets/approx_pos.html", retrieved=True),
    "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html": data(
        "Jet Propulsion Laboratory", "n.d.", "Small-Body Database Lookup",
        None, "NASA", "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html"),
    "https://ssd.jpl.nasa.gov/planets/phys_par.html": data(
        "Jet Propulsion Laboratory", "n.d.",
        "Planetary and satellite physical parameters", None, "NASA",
        "https://ssd.jpl.nasa.gov/planets/phys_par.html"),
    "https://classicsofsciencefiction.com/classics-of-science-fiction-list/by-rank/": web(
        "Classics of Science Fiction", "n.d.", "Books by rank",
        "Classics of Science Fiction",
        "https://classicsofsciencefiction.com/classics-of-science-fiction-list/by-rank/",
        retrieved=True),
    "https://classicsofsciencefiction.com/essays/statistics-and-math/": web(
        "Classics of Science Fiction", "n.d.", "Statistics and math",
        "Classics of Science Fiction",
        "https://classicsofsciencefiction.com/essays/statistics-and-math/",
        retrieved=True),
    "https://classicsofsciencefiction.com/citations-bibliography/": web(
        "Classics of Science Fiction", "n.d.", "Citations bibliography",
        "Classics of Science Fiction",
        "https://classicsofsciencefiction.com/citations-bibliography/",
        retrieved=True),
    "https://www.thehugoawards.org/hugo-history/": web(
        "World Science Fiction Society", "n.d.", "Hugo Awards history",
        "The Hugo Awards", "https://www.thehugoawards.org/hugo-history/",
        retrieved=True),
    "https://nebulas.sfwa.org/": web(
        "Science Fiction and Fantasy Writers Association", "n.d.",
        "Nebula Awards", "SFWA", "https://nebulas.sfwa.org/", retrieved=True),
    "https://www.kimstanleyrobinson.info/content/2312": web(
        "KimStanleyRobinson.info", "n.d.", "2312",
        "KimStanleyRobinson.info",
        "https://www.kimstanleyrobinson.info/content/2312", retrieved=True),
    "https://en.wikipedia.org/": web(
        "Wikimedia Foundation", "n.d.", "Wikipedia, the free encyclopedia",
        None, "https://en.wikipedia.org/", retrieved=True),
    "https://sealevel.nasa.gov/understanding-sea-level/key-indicators/global-mean-sea-level/": web(
        "NASA", "n.d.", "Global mean sea level", "Sea Level Change",
        "https://sealevel.nasa.gov/understanding-sea-level/key-indicators/global-mean-sea-level/",
        retrieved=True),
}


# Text that is already a citation: it opens with a name or an
# organisation and carries a year, "n.d." or "s.f." somewhere near the
# front, after an author list that can run long.
_YEAR = re.compile(r"\((\d{4}[a-z]?|n\.d\.|s\.\s?f\.)\)")


def _is_citation(text):
    t = text.strip()
    if not t or not t[0].isupper():
        return False
    m = _YEAR.search(t[:400])
    return bool(m)


def entry(text, url):
    """A row of (prose, url). Where the prose is already a citation it
    becomes the reference itself; otherwise it becomes the annotation."""
    t = text.strip()
    if _is_citation(t):
        ref = t if t.endswith(".") else t + "."
        return (f"{ref} {url}", None)
    return auto(url, t)


ORGS = {
    "census.gov": "U.S. Census Bureau",
    "science.nasa.gov": "NASA", "sealevel.nasa.gov": "NASA",
    "nasa.gov": "NASA", "humanorigins.si.edu": "Smithsonian Institution",
    "stratigraphy.org": "International Commission on Stratigraphy",
    "mammaldiversity.org": "American Society of Mammalogists",
    "ourworldindata.org": "Our World in Data",
    "population.un.org": "United Nations, Department of Economic and Social Affairs",
    "inegi.org.mx": "Instituto Nacional de Estad\u00edstica y Geograf\u00eda",
    "encyclopediaofalabama.org": "Encyclopedia of Alabama",
    "historyofmassachusetts.org": "History of Massachusetts Blog",
    "mnhs.org": "Minnesota Historical Society",
    "philadelphiaencyclopedia.org": "The Encyclopedia of Greater Philadelphia",
    "digitalprojects.scranton.edu": "University of Scranton",
    "github.com": "GitHub", "universetoday.com": "Universe Today",
    "solarsystemscope.com": "Solar System Scope",
    "archive.org": "Internet Archive",
}


def _org_for(url):
    host = url.split("//", 1)[-1].split("/", 1)[0].replace("www.", "")
    return ORGS.get(host) or host


def _page_title(url):
    """A readable title from the last useful part of a URL."""
    parts = [x for x in url.rstrip("/").split("/")[3:] if x]
    if not parts:
        return url
    GENERIC = {"facts", "index", "index.html", "home", "about", "data",
               "en", "wms", "list", "main"}
    slug = urllib.parse.unquote(parts[-1]).rsplit(".", 1)[0]
    if (slug.lower() in GENERIC or len(slug) < 5) and len(parts) > 1:
        slug = urllib.parse.unquote(parts[-2]).rsplit(".", 1)[0] + " " + slug
    slug = slug.replace("-", " ").replace("_", " ").strip()
    return slug[:1].upper() + slug[1:] if slug else url


def auto(url, annotation=None):
    """The APA entry for a URL: a known source, a Wikipedia article, or a
    plain web page, with the prose kept as the annotation under it."""
    if url in SOURCES:
        return (SOURCES[url], annotation)
    if "wikipedia.org/wiki/" in url:
        return (wiki(url), annotation)
    return (web(_org_for(url), "n.d.", _page_title(url), None, url,
                retrieved=True), annotation)


def wiki_es(url, title=None):
    """Una entrada de Wikipedia, en el formato APA en español."""
    t = _auth(title or _title_from_url(url))
    site = "Wikipedia, la enciclopedia libre" if "es.wikipedia" in url \
        else "Wikipedia"
    return (f"{t}. (s.f.). En <i>{site}</i>. Recuperado el {RETRIEVED_ES}, "
            f"de {url}")


def web_es(author, year, title, site, url, retrieved=False):
    y = year or "s.f."
    bits = [f"{_auth(author)}. ({y}). <i>{title}</i>."]
    if site:
        bits.append(f"{site}.")
    bits.append(f"Recuperado el {RETRIEVED_ES}, de {url}" if retrieved else url)
    return " ".join(bits)


def auto_es(url, annotation=None):
    """Como auto(), para las páginas en español."""
    if "wikipedia.org/wiki/" in url:
        return (wiki_es(url), annotation)
    if url in SOURCES:
        return (SOURCES[url], annotation)
    return (web_es(_org_for(url), None, _page_title(url), None, url,
                   retrieved=True), annotation)


def from_html(block, es=False):
    """Re-render a hand-written references block in APA.

    Each paragraph becomes one entry. Where its prose is already a
    citation that prose is the reference and the links are appended;
    otherwise the prose becomes the annotation under a generated entry.
    """
    out = []
    for para in re.findall(r"<p>(.*?)</p>", block, re.S):
        urls = re.findall(r'href="([^"]+)"', para)
        prose = re.sub(r"<a[^>]*>.*?</a>", " ", para, flags=re.S)
        prose = re.sub(r"<(?!/?i\b)[^>]+>", "", prose)
        prose = re.sub(r"\s+", " ", prose).strip(" .;,")
        if not urls:
            if prose:
                out.append((prose + ".", None))
            continue
        if _is_citation(prose):
            out.append((f"{_auth(prose)}. " + " ".join(urls), None))
        elif (prose and len(prose) < 90 and ":" not in prose
              and prose[0].isupper() and "wikipedia.org/wiki/" not in urls[0]):
            # a document with a title and no author or date of its own
            nd = "s.f." if es else "n.d."
            got = ("Recuperado el " + RETRIEVED_ES + ", de "
                   if es else "Retrieved " + RETRIEVED + ", from ")
            out.append((f"<i>{_auth(prose)}</i>. ({nd}). {got}"
                        + " ".join(urls), None))
        else:
            ref, ann = (auto_es if es else auto)(
                urls[0], (prose + "." if prose else None))
            if len(urls) > 1:
                ref = ref + " " + " ".join(urls[1:])
            out.append((ref, ann))
    return render(out)


def apa_pass(html, es=False):
    """Rewrite a finished page's reference block in APA, and give it the
    hanging indent. For the builders that keep their references inline in
    the template rather than behind a placeholder."""
    m = re.search(r'(<div class="refs">)(.*?)(</div>)', html, re.S)
    if not m:
        return html
    body = from_html(m.group(2), es=es)
    html = html[:m.start(2)] + "\n" + body + "\n" + html[m.end(2):]
    if "text-indent:-2em" not in html:
        html = html.replace("</style>", CSS + "\n</style>", 1)
    return html


def css_pass(html):
    """Give a finished page the hanging indent, leaving its already-APA
    reference list alone."""
    if "text-indent:-2em" in html or "</style>" not in html:
        return html
    return html.replace("</style>", CSS + "\n</style>", 1)
