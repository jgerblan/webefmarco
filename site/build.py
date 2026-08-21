#!/usr/bin/env python3
"""Build a static HTML replica of www.efmarco.com from Wayback Machine captures."""
import re
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# Map of Joomla source paths (as they appear in wayback URLs) -> local static filenames.
PAGE_MAP = {
    "": "index.html",
    "novedades": "novedades.html",
    "blog": "blog.html",
    "industria-y-comercio": "industria-y-comercio.html",
    "instituciones-gubernamentales": "instituciones-gubernamentales.html",
    "hogar": "hogar.html",
    "rural": "rural.html",
    "aesthetic": "mip.html",
    "community-relations": "cip.html",
    "resuources": "control-verde.html",
    "stomach": "control-azul.html",
    "handicap": "k9.html",
    "reproduction": "control-de-vectores.html",
    "mouth-tube": "manejo-de-fauna.html",
    "community-reports": "control-de-aves.html",
    "microscope": "plagas-de-la-madera.html",
    "community-services": "plagas-de-granos.html",
    "community-health-wellness": "desinsectacion.html",
    "87-demo-contents/servicios/214-chinche-de-la-cama": "index.html",
    "87-demo-contents/servicios/213-murcielagos": "index.html",
    "87-demo-contents/servicios/212-desratizacion": "index.html",
    "87-demo-contents/servicios/211-laboratorio-de-zoologia": "index.html",
}

EXTERNAL_HOST_RE = re.compile(
    r'https://web\.archive\.org/web/\d+(?:im_|cs_|js_)?/(https?://(?:www\.)?(?:linkedin|facebook|instagram)\.com/[^"\'\s]*)'
)
MAILTO_RE = re.compile(r'https://web\.archive\.org/web/\d+/(mailto:[^"\'\s]*)')
# efmarco.com asset/page links sometimes appear as protocol-relative (/web/...)
# and sometimes as fully-qualified (https://web.archive.org/web/...) - accept both.
ASSET_RE = re.compile(
    r'(?:https?://web\.archive\.org)?(/web/\d+(?:im_|cs_|js_)/https?://(?:www\.)?efmarco\.com/([^"\'\)\s]*))'
)
PAGE_LINK_RE = re.compile(
    r'(?:https?://web\.archive\.org)?(/web/\d+/https?://(?:www\.)?efmarco\.com/([^"\'\)\s]*))'
)
# Safety-net: any remaining wayback-wrapped URL (e.g. schema.org refs in JSON-LD)
# that wasn't caught by a more specific rule above - strip the wayback wrapper,
# leaving the real external URL.
GENERIC_WAYBACK_RE = re.compile(r'https?://web\.archive\.org/web/\d+(?:im_|cs_|js_)?/')
# Same, but for backslash-escaped URLs found inside embedded JSON/JS strings.
ESCAPED_WAYBACK_RE = re.compile(r'https?:\\/\\/web\.archive\.org\\/web\\/\d+(?:im_|cs_|js_)?\\/')


def asset_local_path(path_and_query):
    path = path_and_query.split("?")[0]
    return path


def rewrite_links(html: str) -> str:
    # External social links: strip wayback prefix
    html = EXTERNAL_HOST_RE.sub(lambda m: m.group(1), html)
    # mailto links
    html = MAILTO_RE.sub(lambda m: m.group(1), html)

    # Asset links (im_/cs_/js_ marker) -> local relative path
    def _asset_sub(m):
        rel = asset_local_path(m.group(2))
        return rel if rel else "index.html"
    html = ASSET_RE.sub(_asset_sub, html)

    # Page links (no marker) -> mapped local page
    def _page_sub(m):
        path = m.group(2).split("?")[0].rstrip("/")
        mapped = PAGE_MAP.get(path)
        if mapped:
            return mapped
        return "index.html"
    html = PAGE_LINK_RE.sub(_page_sub, html)

    # Safety net for any leftover wayback-wrapped URLs (e.g. schema.org refs)
    html = GENERIC_WAYBACK_RE.sub("", html)
    html = ESCAPED_WAYBACK_RE.sub("", html)

    return html


def extract_middle(raw_html: str) -> str:
    """Extract the page-specific content between </header> and <!-- FOOTER -->."""
    start_marker = "<!-- //HEADER -->"
    end_marker = "<!-- FOOTER -->"
    start = raw_html.index(start_marker) + len(start_marker)
    end = raw_html.index(end_marker)
    return raw_html[start:end]


def extract_footer(raw_html: str) -> str:
    start = raw_html.index("<!-- FOOTER -->")
    end = raw_html.index("</body>")
    return raw_html[start:end]


def extract_head_and_nav(raw_html: str) -> str:
    """Extract everything from the t3-wrapper div through </header> (nav + logo + menu)."""
    body_start = raw_html.index('<div class="t3-wrapper">')
    header_end = raw_html.index("<!-- //HEADER -->") + len("<!-- //HEADER -->")
    return raw_html[body_start:header_end]


CSS_LINKS = """\
\t<link href="templates/system/css/system.css" rel="stylesheet" type="text/css"/>
\t<link href="plugins/system/t3/base-bs3/fonts/font-awesome/css/font-awesome.min.css" rel="stylesheet" type="text/css"/>
\t<link href="templates/ja_medicare/local/css/bootstrap.css" rel="stylesheet" type="text/css"/>
\t<link href="templates/ja_medicare/local/css/legacy-grid.css" rel="stylesheet" type="text/css"/>
\t<link href="templates/ja_medicare/local/css/off-canvas.css" rel="stylesheet" type="text/css"/>
\t<link href="templates/ja_medicare/local/css/megamenu.css" rel="stylesheet" type="text/css"/>
\t<link href="modules/mod_jaslideshowlite/assets/css/animate.css" rel="stylesheet" type="text/css"/>
\t<link href="templates/ja_medicare/local/css/mod_jaslideshowlite.css" rel="stylesheet" type="text/css"/>
\t<link href="modules/mod_jaslideshowlite/assets/css/mod_jaslideshowlite-fade.css" rel="stylesheet" type="text/css"/>
\t<link href="templates/ja_medicare/fonts/font-awesome/css/font-awesome.min.css" rel="stylesheet" type="text/css"/>
\t<link href="templates/ja_medicare/css/template.css" rel="stylesheet" type="text/css"/>
"""

JS_SCRIPTS = """\
\t<script src="media/jui/js/jquery.min.js" type="text/javascript"></script>
\t<script src="media/jui/js/jquery-noconflict.js" type="text/javascript"></script>
\t<script src="media/jui/js/jquery-migrate.min.js" type="text/javascript"></script>
\t<script src="media/system/js/caption.js" type="text/javascript"></script>
\t<script src="plugins/system/t3/base-bs3/bootstrap/js/bootstrap.js" type="text/javascript"></script>
\t<script src="plugins/system/t3/base-bs3/js/jquery.tap.min.js" type="text/javascript"></script>
\t<script src="media/system/js/mootools-core.js" type="text/javascript"></script>
\t<script src="media/system/js/core.js" type="text/javascript"></script>
\t<script src="modules/mod_jaslideshowlite/assets/js/script.js" type="text/javascript"></script>
\t<script src="plugins/system/t3/base-bs3/js/menu.js" type="text/javascript"></script>
\t<script src="plugins/system/t3/base-bs3/js/off-canvas.js" type="text/javascript"></script>
\t<script src="plugins/system/t3/base-bs3/js/script.js" type="text/javascript"></script>
\t<script src="t3-assets/js/js-87621.js" type="text/javascript"></script>
"""


def build_page(title: str, nav_html: str, content_html: str, footer_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es-es" dir="ltr">
<head>
\t<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
\t<meta name="viewport" content="width=device-width, initial-scale=1"/>
\t<meta name="generator" content="Sitio recuperado desde Wayback Machine - efmarco.com"/>
\t<title>{title}</title>
\t<link href="templates/ja_medicare/favicon.ico" rel="shortcut icon" type="image/vnd.microsoft.icon"/>
{CSS_LINKS}	<script>
		// Algunas imagenes originales del sitio ya no estan disponibles en el
		// archivo de Wayback Machine; las ocultamos en lugar de mostrar el icono roto.
		document.addEventListener("error", function (e) {{
			if (e.target.tagName === "IMG") {{
				e.target.style.display = "none";
			}}
		}}, true);
	</script>
</head>
<body>
{JS_SCRIPTS}{nav_html}
{content_html}
{footer_html}
</body>
</html>
"""


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    index_raw = load("index_raw.html")
    nav_html = rewrite_links(extract_head_and_nav(index_raw))
    footer_html = rewrite_links(extract_footer(index_raw))

    pages = [
        # (raw file, title, output filename)
        ("index_raw.html", "Efmarco - Control de Plagas", "index.html"),
        ("raw_hogar.html", "Hogar - Efmarco", "hogar.html"),
        ("raw_rural.html", "Rural - Efmarco", "rural.html"),
        ("raw_industria-y-comercio.html", "Industria y Comercio - Efmarco", "industria-y-comercio.html"),
        ("raw_instituciones-gubernamentales.html", "Inst. Gubernamentales - Efmarco", "instituciones-gubernamentales.html"),
        ("raw_novedades.html", "Novedades - Efmarco", "novedades.html"),
        ("raw_blog.html", "Blog - Efmarco", "blog.html"),
        ("pages/raw_aesthetic.html", "MIP - Manejo Integrado de Plagas - Efmarco", "mip.html"),
        ("pages/raw_community-relations.html", "CIP - Control Integral de Plagas - Efmarco", "cip.html"),
        ("pages/raw_resuources.html", "Control Verde - Efmarco", "control-verde.html"),
        ("pages/raw_stomach.html", "Control Azul - Calidad de Agua Potable - Efmarco", "control-azul.html"),
        ("pages/raw_handicap.html", "K9 - Unidad Canina de Rastreo - Efmarco", "k9.html"),
        ("pages/raw_reproduction.html", "Control de Vectores - Efmarco", "control-de-vectores.html"),
        ("pages/raw_mouth-tube.html", "Manejo de Fauna - Efmarco", "manejo-de-fauna.html"),
        ("pages/raw_community-reports.html", "Control de Aves - Efmarco", "control-de-aves.html"),
        ("pages/raw_microscope.html", "Plagas de la Madera - Efmarco", "plagas-de-la-madera.html"),
        ("pages/raw_community-services.html", "Plagas de Granos Almacenados - Efmarco", "plagas-de-granos.html"),
        ("pages/raw_community-health-wellness.html", "Desinsectación - Efmarco", "desinsectacion.html"),
    ]

    for raw_file, title, out_file in pages:
        raw = load(raw_file)
        content = rewrite_links(extract_middle(raw))
        page_html = build_page(title, nav_html, content, footer_html)
        out_path = os.path.join(ROOT, "dist", out_file)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        print("Wrote", out_file)


if __name__ == "__main__":
    main()
