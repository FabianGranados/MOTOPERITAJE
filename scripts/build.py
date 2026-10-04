#!/usr/bin/env python3
"""
Genera el sitio estático de motoperitaje.com en ./public a partir del paquete de migración.

Fuente de verdad: migracion/html-original/*.html (el HTML exacto que servía WordPress).
El script conserva el marcado, las URLs, los <title>, metas, canonical, Open Graph y el schema
JSON-LD tal cual, y solo cambia lo necesario para que funcione sin WordPress:

  * Las páginas se escriben en <ruta>/index.html para que las URLs sigan siendo idénticas
    (con slash final), p. ej. /precio-peritaje-moto/ -> public/precio-peritaje-moto/index.html.
  * Los recursos (CSS, fuentes, imágenes) se publican en las MISMAS rutas que tenían en
    WordPress (/wp-content/...), así hasta las URLs de las imágenes se mantienen para Google Imágenes.
  * Se quita el lazy-load de Smush (data-src -> src) y los scripts de WordPress/LiteSpeed, que se
    reemplazan por /assets/js/sitio.js.

Uso:  python3 scripts/build.py
Requiere: Pillow y fontTools[woff] (pip install -r scripts/requirements.txt)
"""
import csv
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MIG = ROOT / 'migracion'
SRC = ROOT / 'src'
VENDOR = ROOT / 'vendor'
OUT = ROOT / 'public'
DOMAIN = 'https://motoperitaje.com'

# Archivo de html-original -> ruta pública (URL exacta del sitio WordPress)
PAGES = {
    'inicio.html': '/',
    'precio-peritaje-moto.html': '/precio-peritaje-moto/',
    'peritaje-de-motos-a-domicilio-en-bogota.html': '/peritaje-de-motos-a-domicilio-en-bogota/',
    'contactanos.html': '/contactanos/',
    'agendar-en-linea.html': '/agendar-en-linea/',
    'blog.html': '/blog/',
    'politica-de-tratamiento-de-datos.html': '/politica-de-tratamiento-de-datos/',
    'category_uncategorized.html': '/category/uncategorized/',
    'todo-lo-que-necesitas-saber-sobre-el-peritaje-de-motos.html': '/todo-lo-que-necesitas-saber-sobre-el-peritaje-de-motos/',
    'como-el-peritaje-revela-su-verdadero-precio-en-el-mercado-de-las-motos.html': '/como-el-peritaje-revela-su-verdadero-precio-en-el-mercado-de-las-motos/',
    'importancia-del-peritaje-de-motos-en-casos-de-accidentes.html': '/importancia-del-peritaje-de-motos-en-casos-de-accidentes/',
    'que-documentacion-necesito-para-realizar-un-peritaje-de-motos-en-bogota.html': '/que-documentacion-necesito-para-realizar-un-peritaje-de-motos-en-bogota/',
    'que-tipo-de-informacion-se-recopila-durante-un-peritaje-de-motos.html': '/que-tipo-de-informacion-se-recopila-durante-un-peritaje-de-motos/',
    'las-marcas-de-motos-mas-populares.html': '/las-marcas-de-motos-mas-populares/',
    'como-preparar-tu-moto-para-un-viaje-seguro-consejos-esenciales.html': '/como-preparar-tu-moto-para-un-viaje-seguro-consejos-esenciales/',
    'iluminando-el-camino-luces-led-para-motos.html': '/iluminando-el-camino-luces-led-para-motos/',
    'historia-de-las-motos.html': '/historia-de-las-motos/',
    'importancia-del-equipo-de-proteccion-para-motociclistas.html': '/importancia-del-equipo-de-proteccion-para-motociclistas/',
    'mejores-accesorios-para-motociclistas.html': '/mejores-accesorios-para-motociclistas/',
    'guia-de-mantenimiento-preventivo-para-motos-usadas.html': '/guia-de-mantenimiento-preventivo-para-motos-usadas/',
    'que-revisar-antes-de-comprar-una-moto-usada-en-bogota.html': '/que-revisar-antes-de-comprar-una-moto-usada-en-bogota/',
}

# Ruta publicada (sin query) -> archivo de origen. Orden de prioridad:
#   1) migracion/wp-originales/<ruta>  (archivos originales que se consigan después: siempre ganan)
#   2) los mapeos explícitos de abajo (CSS original del paquete y librerías de npm)
#   3) src/reconstruido/<ruta>         (reconstrucciones propias de archivos que faltaban)
STATIC_MAP = {
    '/wp-content/plugins/elementor/assets/css/frontend.min.css': MIG / 'css-original/elementor-frontend.min.css',
    '/wp-content/plugins/elementor-pro/assets/css/frontend.min.css': MIG / 'css-original/elementor-pro-frontend.min.css',
    '/wp-content/themes/automobile-hub/style.css': MIG / 'css-original/style.css',
    '/wp-content/themes/automobile-hub/assets/css/bootstrap.css': VENDOR / 'bootstrap-4.0.0.css',
    '/wp-content/themes/automobile-hub/assets/css/animate.css': VENDOR / 'animate.compat.css',
    '/wp-content/themes/automobile-hub/assets/css/fontawesome-all.css': VENDOR / 'fontawesome/css/all.css',
    '/wp-content/plugins/elementor/assets/lib/font-awesome/css/fontawesome.min.css': VENDOR / 'fontawesome/css/fontawesome.min.css',
    '/wp-content/plugins/elementor/assets/lib/font-awesome/css/solid.min.css': VENDOR / 'fontawesome/css/solid.min.css',
    '/wp-content/plugins/elementor/assets/lib/font-awesome/css/regular.min.css': VENDOR / 'fontawesome/css/regular.min.css',
    '/wp-content/plugins/elementor/assets/lib/font-awesome/css/brands.min.css': VENDOR / 'fontawesome/css/brands.min.css',
    '/wp-content/plugins/elementor/assets/lib/swiper/v8/css/swiper.min.css': VENDOR / 'swiper/swiper-bundle.min.css',
    '/wp-content/plugins/elementor/assets/lib/swiper/v8/swiper.min.js': VENDOR / 'swiper/swiper-bundle.min.js',
}
for _f in (MIG / 'css-original').glob('post-*.css'):
    STATIC_MAP['/wp-content/uploads/elementor/css/' + _f.name] = _f
# Webfonts de Font Awesome (tema y Elementor usan rutas ../webfonts/ relativas al CSS)
for _f in (VENDOR / 'fontawesome/webfonts').iterdir():
    STATIC_MAP['/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/' + _f.name] = _f
    STATIC_MAP['/wp-content/themes/automobile-hub/assets/webfonts/' + _f.name] = _f

# Hojas de estilo de plugins que ya no se usan en el sitio estático (no se publican ni se enlazan)
DROP_STYLESHEETS = (
    'bookly-responsive-appointment-booking-tool',
    'all-in-one-seo-pack/dist/Lite/assets/css/table-of-contents',
)

# Referencias que existen en el HTML/CSS original pero que ninguna página llega a usar
# (estilos del tema para su cabecera/slider, que las plantillas Elementor Canvas no muestran).
OPTIONAL_REFS = {
    '/wp-content/themes/automobile-hub/assets/images/sliderimage.png',
    '/wp-content/themes/automobile-hub/assets/images/pin.png',
}

LAZY_PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg=='

warnings = []


def warn(msg):
    if msg not in warnings:
        warnings.append(msg)


# ----------------------------------------------------------------------------------------------
# Imágenes
# ----------------------------------------------------------------------------------------------

def load_manifest():
    """URL original (ruta) -> archivo en migracion/imagenes o migracion/logos."""
    m = {}
    with open(MIG / 'imagenes/_manifest.csv', encoding='utf-8-sig') as fh:
        for row in csv.DictReader(fh):
            path = row['url_original'].replace(DOMAIN, '')
            m[path] = MIG / 'imagenes' / row['archivo']
    for logo in (MIG / 'logos').iterdir():
        # Los logos no traen URL en el manifiesto; se ubican por nombre cuando se piden.
        m.setdefault('logo:' + logo.name, logo)
    return m


SIZE_RE = re.compile(r'^(?P<base>.+)-(?P<w>\d+)x(?P<h>\d+)(?P<ext>\.\w+)$')
THUMB_RE = re.compile(r'^(?P<base>.+)-(?P<hash>[a-z0-9]{40,})(?P<ext>\.\w+)$')


def find_source(path, manifest):
    if path in manifest:
        return manifest[path]
    name = path.rsplit('/', 1)[-1]
    for p in (MIG / 'imagenes' / name, MIG / 'logos' / name):
        if p.exists():
            return p
    return None


def resize_to(src, dst, w, h=None):
    """Recorte/redimensión al estilo de WordPress: escala y recorta al centro si cambia la proporción."""
    img = Image.open(src)
    img.load()
    if h is None:
        h = round(img.height * w / img.width)
    scale = max(w / img.width, h / img.height)
    nw, nh = max(w, round(img.width * scale)), max(h, round(img.height * scale))
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    img = img.crop((left, top, left + w, top + h))
    dst.parent.mkdir(parents=True, exist_ok=True)
    fmt = {'.webp': 'WEBP', '.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG'}[dst.suffix.lower()]
    if fmt == 'JPEG' and img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    kwargs = {'quality': 85} if fmt in ('WEBP', 'JPEG') else {'optimize': True}
    img.save(dst, fmt, **kwargs)


def publish_upload(path, manifest, width_hint=None):
    """Publica /wp-content/uploads/... en public/, copiando o generando el tamaño pedido."""
    dst = OUT / path.lstrip('/')
    if dst.exists():
        return True
    src = find_source(path, manifest)
    if src:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    folder, name = path.rsplit('/', 1)
    m = SIZE_RE.match(name)
    if m:
        base = find_source(folder + '/' + m['base'] + m['ext'], manifest)
        if base:
            resize_to(base, dst, int(m['w']), int(m['h']))
            return True
    m = THUMB_RE.match(name)
    if m and folder.endswith('/elementor/thumbs'):
        parent = folder[: -len('/elementor/thumbs')]
        base = find_source(parent + '/' + m['base'] + m['ext'], manifest) or find_source('/x/' + m['base'] + m['ext'], manifest)
        if base and width_hint:
            resize_to(base, dst, width_hint)
            return True
    warn('Imagen no disponible en el paquete (queda 404): ' + path)
    return False


# ----------------------------------------------------------------------------------------------
# Fuentes locales de Elementor (Roboto y Roboto Slab)
# ----------------------------------------------------------------------------------------------

GOOGLE_RANGES = {
    'cyrillic-ext': 'U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F',
    'cyrillic': 'U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116',
    'greek-ext': 'U+1F00-1FFF',
    'greek': 'U+0370-0377, U+037A-037F, U+0384-038A, U+038C, U+038E-03A1, U+03A3-03FF',
    'vietnamese': 'U+0102-0103, U+0110-0111, U+0128-0129, U+0168-0169, U+01A0-01A1, U+01AF-01B0, U+0300-0301, U+0303-0304, U+0308-0309, U+0323, U+0329, U+1EA0-1EF9, U+20AB',
    'latin-ext': 'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF',
    'latin': 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD',
}
SUBSET_ORDER = ['cyrillic-ext', 'cyrillic', 'greek-ext', 'greek', 'math', 'symbols', 'vietnamese', 'latin-ext', 'latin']


def ranges_from_cmap(cps):
    cps = sorted(c for c in cps if c > 0x7F)
    out, start, prev = [], None, None
    for c in cps:
        if start is None:
            start = prev = c
        elif c == prev + 1:
            prev = c
        else:
            out.append((start, prev))
            start = prev = c
    if start is not None:
        out.append((start, prev))
    return ', '.join('U+%04X' % a if a == b else 'U+%04X-%04X' % (a, b) for a, b in out)


def classify_font(cmap):
    if 0xE1 in cmap and 0x100 not in cmap:
        return 'latin'
    if 0x1EA0 in cmap:
        return 'vietnamese'
    if 0x460 in cmap:
        return 'cyrillic-ext'
    if 0x410 in cmap:
        return 'cyrillic'
    if 0x100 in cmap:
        return 'latin-ext'
    if 0x2200 in cmap or (0x3B1 in cmap and len(cmap) > 150):
        return 'math'
    if 0x3B1 in cmap:
        return 'greek'
    if 0x1F00 in cmap or any(0x1F00 <= c <= 0x1FFF for c in cmap):
        return 'greek-ext'
    return 'symbols'


def build_fonts():
    fonts_dir = OUT / 'wp-content/uploads/elementor/google-fonts/fonts'
    fonts_dir.mkdir(parents=True, exist_ok=True)
    css = {'roboto': [], 'robotoslab': []}
    for f in sorted((MIG / 'fuentes').glob('*.woff2')):
        shutil.copy2(f, fonts_dir / f.name)
        font = TTFont(f)
        cmap = font.getBestCmap()
        subset = classify_font(cmap)
        italic = bool(font['OS/2'].fsSelection & 1)
        family = 'roboto' if f.name.startswith('roboto-') else 'robotoslab'
        name = 'Roboto' if family == 'roboto' else 'Roboto Slab'
        urange = GOOGLE_RANGES.get(subset) or ranges_from_cmap(cmap)
        css[family].append((italic, SUBSET_ORDER.index(subset), (
            "/* %s */\n@font-face {\n  font-family: '%s';\n  font-style: %s;\n  font-weight: 100 900;\n"
            "  font-stretch: 100%%;\n  font-display: auto;\n  src: url(/wp-content/uploads/elementor/google-fonts/fonts/%s) format('woff2');\n"
            "  unicode-range: %s;\n}\n") % (subset, name, 'italic' if italic else 'normal', f.name, urange)))
    css_dir = OUT / 'wp-content/uploads/elementor/google-fonts/css'
    css_dir.mkdir(parents=True, exist_ok=True)
    for family, rules in css.items():
        rules.sort(key=lambda r: (r[0], r[1]))
        (css_dir / (family + '.css')).write_text(''.join(r[2] for r in rules), encoding='utf-8')


# ----------------------------------------------------------------------------------------------
# Recursos estáticos (CSS/JS/fuentes con la ruta original de WordPress)
# ----------------------------------------------------------------------------------------------

def resolve_static(path):
    for candidate in (MIG / 'wp-originales' / path.lstrip('/'),):
        if candidate.exists():
            return candidate
    if path in STATIC_MAP and STATIC_MAP[path].exists():
        return STATIC_MAP[path]
    candidate = SRC / 'reconstruido' / path.lstrip('/')
    if candidate.exists():
        return candidate
    return None


def publish_static(path, manifest):
    dst = OUT / path.lstrip('/')
    if dst.exists():
        return True
    src = resolve_static(path)
    if not src:
        warn('Recurso no disponible en el paquete (queda 404): ' + path)
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.suffix == '.css':
        text = src.read_text(encoding='utf-8', errors='replace')
        text = text.replace(DOMAIN + '/wp-content/', '/wp-content/')
        dst.write_text(text, encoding='utf-8')
        # Imágenes/fuentes a las que apunta el CSS
        for ref in re.findall(r'url\(\s*[\'"]?([^\'")]+)', text):
            if ref.startswith('data:') or ref.startswith('http') or ref.startswith('//'):
                continue
            target = ref.split('?')[0].split('#')[0]
            if not target.startswith('/'):
                target = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if target in OPTIONAL_REFS:
                continue
            if target.startswith('/wp-content/uploads/') and not target.startswith('/wp-content/uploads/elementor/google-fonts'):
                publish_upload(target, manifest)
            elif target.startswith('/wp-content/') and not (OUT / target.lstrip('/')).exists():
                publish_static(target, manifest)
    else:
        shutil.copy2(src, dst)
    return True


# ----------------------------------------------------------------------------------------------
# Transformación del HTML
# ----------------------------------------------------------------------------------------------

def protect(html_text, pattern, store):
    def repl(m):
        store.append(m.group(0))
        return '\x00%d\x00' % (len(store) - 1)
    return re.sub(pattern, repl, html_text, flags=re.S | re.I)


def restore(html_text, store):
    return re.sub('\x00(\\d+)\x00', lambda m: store[int(m.group(1))], html_text)


def unlazy(tag):
    """Convierte una etiqueta <img>/<iframe> con lazy-load de Smush en una normal."""
    if 'data-src=' not in tag:
        return tag
    tag = re.sub(r'\ssrc="' + re.escape(LAZY_PLACEHOLDER) + '"', '', tag)
    tag = re.sub(r'\sdata-(src|srcset|sizes)=', r' \1=', tag)
    tag = re.sub(r'\sdata-load-mode="[^"]*"', '', tag)
    tag = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % ' '.join(c for c in m.group(1).split() if c not in ('lazyload', 'lazyloading')), tag)
    tag = tag.replace(' class=""', '')
    if 'loading=' not in tag and 'fetchpriority=' not in tag:
        tag = re.sub(r'^<(img|iframe)', r'<\1 loading="lazy"', tag)
    return tag


ANALYTICS = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-K1BMVYM7ZX"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag("set","linker",{"domains":["motoperitaje.com"]});gtag("js",new Date());gtag("config","G-K1BMVYM7ZX");
</script>
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','1200120341805655');fbq('track','PageView');
</script>
<!-- End Meta Pixel Code -->
'''

WHATSAPP_WIDGET = {
    'title': 'Chatea con un asesor.',
    'description': 'Escríbenos ya mismo y obtén información.',
    'notice': 'El equipo suele responder en pocos minutos.',
    'label': 'Te ayudamos? <strong>Chatea con nosotros</strong>',
    'labelWidth': 156,
    'accounts': [
        {'name': 'July Vega', 'avatar': '/wp-content/uploads/2025/07/Asesora-comercial-July.jpeg',
         'info': {'number': '+573022507384', 'title': 'Asesora Comercial', 'predefinedText': ''}},
        {'name': 'Andrés Rodríguez', 'avatar': '/wp-content/uploads/2025/07/Asesor-comercial-Andres.jpeg',
         'info': {'number': '+573021138434', 'title': 'Asesor Comercial', 'predefinedText': 'Hola, quiero mas información. '}},
        {'name': 'Asesoría Comercial', 'avatar': '/wp-content/uploads/2026/01/moto-peritaje-marca.webp',
         'info': {'number': '+573019262267', 'title': 'Comunícate con nuestra área comercial', 'predefinedText': 'Hola, quiero mas información. '}},
    ],
}

BOOKLY_REPLACEMENT = '''<div class="wpforms-container wpforms-container-full mp-agenda" id="mp-agenda">
<form class="wpforms-form mp-form-whatsapp" data-wa-number="573022507384" data-wa-intro="Hola, quiero agendar un peritaje de moto:">
<div class="wpforms-field-container">
<div class="wpforms-field mp-campo"><label class="wpforms-field-label" for="mp-agenda-nombre">Nombre <span class="wpforms-required-label">*</span></label><input type="text" id="mp-agenda-nombre" class="wpforms-field-large" required autocomplete="name"></div>
<div class="wpforms-field mp-campo"><label class="wpforms-field-label" for="mp-agenda-telefono">Teléfono <span class="wpforms-required-label">*</span></label><input type="tel" id="mp-agenda-telefono" class="wpforms-field-large" required autocomplete="tel"></div>
<div class="wpforms-field mp-campo"><label class="wpforms-field-label" for="mp-agenda-sede">Sede</label><select id="mp-agenda-sede" class="wpforms-field-large"><option>Carrera 50 #2-49. B. Jazmín</option><option>Calle 134 # 46-35 - Prado Veraniego</option><option>A domicilio</option></select></div>
<div class="wpforms-field mp-campo"><label class="wpforms-field-label" for="mp-agenda-fecha">Fecha <span class="wpforms-required-label">*</span></label><input type="date" id="mp-agenda-fecha" class="wpforms-field-large" required></div>
<div class="wpforms-field mp-campo"><label class="wpforms-field-label" for="mp-agenda-hora">Hora</label><input type="time" id="mp-agenda-hora" class="wpforms-field-large" min="08:00" max="16:00"></div>
<div class="wpforms-field mp-campo"><label class="wpforms-field-label" for="mp-agenda-notas">Comentarios</label><textarea id="mp-agenda-notas" class="wpforms-field-large"></textarea></div>
</div>
<div class="wpforms-submit-container"><button type="submit" class="wpforms-submit">Agendar por WhatsApp</button></div>
</form>
</div>'''


def transform(src_html, route, manifest):
    h = src_html
    head_end = h.find('</head>')
    head, body = h[:head_end], h[head_end:]

    # ---- <head> ----
    # Elementos propios de WordPress que no tienen sentido sin el CMS
    head = re.sub(r'<link rel="(?:https://api\.w\.org/|EditURI|shortlink)"[^>]*>\s*', '', head)
    head = re.sub(r"<link rel='shortlink'[^>]*>\s*", '', head)
    head = re.sub(r'<link rel="alternate"[^>]*(?:oembed|wp-json|application/rss\+xml)[^>]*>\s*', '', head)
    head = re.sub(r'<meta name="(?:generator|ti-site-data)"[^>]*>\s*', '', head)
    head = re.sub(r"<link rel='dns-prefetch' href='//fonts.googleapis.com' />\s*", "<link rel='dns-prefetch' href='//fonts.googleapis.com' />\n", head)
    # Hojas de estilo de plugins retirados
    head = re.sub(r"<link rel='stylesheet'[^>]*(?:%s)[^>]*>\s*" % '|'.join(re.escape(d) for d in DROP_STYLESHEETS), '', head)
    # MonsterInsights + Site Kit (gtag) + jQuery: se reemplazan por un único bloque de analítica
    head = re.sub(r'<!-- This site uses the Google Analytics by MonsterInsights.*?<!-- / Google Analytics by MonsterInsights -->\s*', '', head, flags=re.S)
    head = re.sub(r'<script[^>]*(?:monsterinsights|jquery-core-js|google_gtagjs-js)[^>]*>.*?</script>\s*', '', head, flags=re.S)
    head = re.sub(r'<script src="//www\.googletagmanager\.com/gtag/js[^>]*>\s*</script>\s*', '', head)
    head = re.sub(r'<!--\s*Fragmento de código de la etiqueta de Google \(gtag\.js\).*?-->\s*', '', head, flags=re.S)
    head = head.replace('<!-- Fragmento de código de Google Analytics añadido por Site Kit -->\n', '')
    gtm = re.search(r'<!-- Fragmento de código de Google Tag Manager añadido por Site Kit -->', head)
    if gtm:
        head = head[:gtm.start()] + ANALYTICS + head[gtm.start():]
    else:
        head = head.replace('<link rel="icon"', ANALYTICS + '<link rel="icon"', 1)

    # ---- <body> ----
    body = re.sub(r'<script[^>]*type="litespeed/javascript"[^>]*data-src="https://cdn\.trustindex\.io/loader\.js[^"]*"[^>]*>\s*</script>',
                  '<script defer src="https://cdn.trustindex.io/loader.js?ver=1"></script>', body)
    body = re.sub(r'<script[^>]*type="litespeed/javascript"[^>]*>.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<script>window\.litespeed_ui_events.*?</script>', '', body, flags=re.S)
    body = re.sub(r"<script type='text/javascript'>\s*/\* <!\[CDATA\[ \*/\s*var wpforms_settings.*?</script>", '', body, flags=re.S)
    body = re.sub(r'<script[^>]*monsterinsights[^>]*>.*?</script>', '', body, flags=re.S)

    if route == '/agendar-en-linea/':
        body, n = re.subn(r'<!--\s*Plugin Name: Bookly.*?<div class="bookly-css-root">.*?</div>\s*</div>\s*</div>',
                          BOOKLY_REPLACEMENT, body, count=1, flags=re.S)
        if not n:
            warn('No se encontró el formulario de Bookly en /agendar-en-linea/')
        head = head.replace('</head>', '')
        head += ("<link rel='stylesheet' id='wpforms-full-css' href='/wp-content/plugins/wpforms-lite/assets/css/frontend/classic/wpforms-full.min.css?ver=1.10.2' media='all' />\n")

    page = head + body
    page = re.sub(r'<(img|iframe)\b[^>]*>', lambda m: unlazy(m.group(0)), page)

    # URLs: los recursos y enlaces internos pasan a rutas relativas a la raíz (misma URL final).
    # Canonical, metas Open Graph/Twitter y el JSON-LD se dejan EXACTAMENTE como estaban.
    store = []
    page = protect(page, r'<script type="application/ld\+json".*?</script>', store)
    page = protect(page, r'<meta\s[^>]*>', store)
    page = protect(page, r'<link rel="canonical"[^>]*>', store)
    page = page.replace(DOMAIN + '/wp-content/', '/wp-content/').replace(DOMAIN + '/wp-includes/', '/wp-includes/')
    page = page.replace('https:\\/\\/motoperitaje.com\\/wp-content\\/', '\\/wp-content\\/')
    page = re.sub(r'href="https://motoperitaje\.com(/[^"]*)?"', lambda m: 'href="%s"' % (m.group(1) or '/'), page)
    page = re.sub(r"href='https://motoperitaje\.com(/[^']*)?'", lambda m: "href='%s'" % (m.group(1) or '/'), page)
    page = restore(page, store)

    # Scripts del sitio estático
    tail = ['<script>window.MP_WHATSAPP_WIDGET=%s;</script>' % json.dumps(WHATSAPP_WIDGET, ensure_ascii=False)]
    if 'elementor-widget-image-carousel' in page:
        tail.append('<script src="/wp-content/plugins/elementor/assets/lib/swiper/v8/swiper.min.js?ver=8.4.5"></script>')
    tail.append('<script src="/assets/js/sitio.js?v=1"></script>')
    page = page.replace('</body>', '\n'.join(tail) + '\n</body>', 1)
    return page


def collect_assets(page, manifest):
    """Publica todo lo que la página referencia en /wp-content/ (y las imágenes absolutas de metas)."""
    refs = set()
    for m in re.finditer(r'(?:https://motoperitaje\.com)?(/wp-(?:content|includes)/[^\s"\'()<>,\\]+?)(?:\s+(\d+)w)?(?=[\s"\'()<>,\\])', page):
        refs.add((m.group(1).split('?')[0].replace('&quot;', ''), int(m.group(2)) if m.group(2) else None))
    for m in re.finditer(r'\\/wp-content\\/([^"&\s]+?)(?=&quot;|")', page):
        refs.add(('/wp-content/' + m.group(1).replace('\\/', '/'), None))
    for path, width in sorted(refs, key=lambda r: (r[0], r[1] or 0)):
        path = html.unescape(path)
        if '*' in path or path in OPTIONAL_REFS:
            continue  # comodines de las speculationrules de WordPress
        if path.startswith('/wp-content/uploads/') and not path.startswith('/wp-content/uploads/elementor/'):
            publish_upload(path, manifest, width)
        elif path.startswith('/wp-content/uploads/elementor/thumbs/'):
            publish_upload(path, manifest, width)
        elif path.startswith('/wp-content/uploads/elementor/google-fonts/'):
            pass  # generadas por build_fonts()
        elif path.startswith('/wp-content/uploads/elementor/css/') or path.startswith('/wp-content/plugins/') or path.startswith('/wp-content/themes/'):
            if not path.endswith('.js') or path.startswith('/wp-content/plugins/elementor/assets/lib/swiper/'):
                publish_static(path, manifest)
        elif path.startswith('/wp-content/uploads/'):
            publish_upload(path, manifest, width)
        elif path in OPTIONAL_REFS:
            pass
        elif path.startswith('/wp-includes/') or path.startswith('/wp-content/litespeed/') or '/wp-json/' in path:
            pass
        else:
            warn('Referencia no gestionada: ' + path)


# ----------------------------------------------------------------------------------------------
# Sitemaps, robots, 404 y archivos de configuración
# ----------------------------------------------------------------------------------------------

def build_sitemaps():
    for f in (MIG / 'sitemaps').iterdir():
        text = f.read_text(encoding='utf-8')
        if f.suffix == '.xml':
            # La hoja XSL de AIOSEO no existe en el sitio estático; los buscadores la ignoran igual.
            text = re.sub(r'<\?xml-stylesheet[^>]*\?>\s*', '', text)
            text = re.sub(r'<!-- Este mapa del sitio lo generó All in One SEO.*?-->\s*', '', text)
        (OUT / f.name).write_text(text, encoding='utf-8')


def build_404():
    tpl = (OUT / 'blog/index.html').read_text(encoding='utf-8')
    tpl = re.sub(r'<title>.*?</title>', '<title>Página no encontrada | Moto Peritaje</title>', tpl, count=1, flags=re.S)
    tpl = re.sub(r'<meta name="description"[^>]*>', '', tpl)
    tpl = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex, follow" />', tpl)
    tpl = re.sub(r'<link rel="canonical"[^>]*>\s*', '', tpl)
    tpl = re.sub(r'<script type="application/ld\+json".*?</script>\s*', '', tpl, flags=re.S)
    tpl = re.sub(r'<meta property="(?:og|article):[^>]*>\s*|<meta name="twitter:[^>]*>\s*', '', tpl)
    (OUT / '404.html').write_text(tpl, encoding='utf-8')


def build_redirects(shortlinks):
    """worker/atajos.json: atajos ?p=ID de WordPress -> URL definitiva (los aplica worker/index.js)."""
    data = dict(sorted(shortlinks.items(), key=lambda kv: int(kv[0])))
    (ROOT / 'worker/atajos.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    manifest = load_manifest()
    build_fonts()
    shortlinks = {}

    for fname, route in PAGES.items():
        src = (MIG / 'html-original' / fname).read_text(encoding='utf-8')
        m = re.search(r"<link rel='shortlink' href='https://motoperitaje\.com/\?p=(\d+)'", src)
        if m:
            shortlinks[m.group(1)] = route
        page = transform(src, route, manifest)
        dst = OUT / route.lstrip('/') / 'index.html'
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(page, encoding='utf-8')
        collect_assets(page, manifest)

    # Archivos propios del sitio estático
    shutil.copytree(SRC / 'assets', OUT / 'assets', dirs_exist_ok=True)
    for extra in ('/wp-content/plugins/whatsapp-for-wordpress/assets/img/whatsapp_logo.svg',
                  '/wp-content/plugins/elementor/assets/lib/swiper/v8/swiper.min.js'):
        publish_static(extra, manifest)
    build_sitemaps()
    build_404()
    build_redirects(shortlinks)

    print('Páginas generadas: %d' % len(PAGES))
    if warnings:
        print('\nAvisos (%d):' % len(warnings))
        for w in warnings:
            print('  - ' + w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
