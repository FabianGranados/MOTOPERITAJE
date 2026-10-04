#!/usr/bin/env python3
"""
Compara cada página original de WordPress (migracion/html-original) con la generada en public/
y falla si cambió algo que Google usa: <title>, metas, canonical, Open Graph/Twitter, JSON-LD,
encabezados, texto visible, enlaces internos e imágenes (src + alt).

Uso: python3 scripts/verificar_seo.py
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import DOMAIN, MIG, OUT, PAGES  # noqa: E402


class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.headings, self.anchors, self.images = {}, {}, [], [], []
        self.text, self.ld, self.title = [], [], ''
        self._stack, self._skip, self._cur_h, self._in_ld = [], 0, None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and (a.get('name') or a.get('property')):
            self.meta[a.get('name') or a.get('property')] = a.get('content')
        elif tag == 'link' and a.get('rel') in ('canonical', 'icon', 'apple-touch-icon'):
            self.links.setdefault(a['rel'], []).append(a.get('href'))
        elif tag in ('script', 'style', 'template', 'noscript'):
            self._skip += 1
            self._in_ld = tag == 'script' and a.get('type') == 'application/ld+json'
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._cur_h = [tag, '']
        elif tag == 'a' and a.get('href'):
            self.anchors.append(norm_url(a['href']))
        elif tag == 'img':
            src = a.get('src') or ''
            if src.startswith('data:'):
                src = a.get('data-src') or src
            self.images.append((norm_url(src.split('?')[0]), a.get('alt')))
        if tag == 'title':
            self._stack.append('title')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'template', 'noscript'):
            self._skip = max(0, self._skip - 1)
            self._in_ld = False
        elif self._cur_h and tag == self._cur_h[0]:
            self.headings.append((self._cur_h[0], ' '.join(self._cur_h[1].split())))
            self._cur_h = None
        if tag == 'title' and self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if self._in_ld:
            self.ld.append(data.strip())
            return
        if self._stack and self._stack[-1] == 'title':
            self.title += data
            return
        if self._skip:
            return
        if self._cur_h:
            self._cur_h[1] += data
        if data.strip():
            self.text.append(' '.join(data.split()))


def norm_url(u):
    return u.replace(DOMAIN, '') or '/'


def parse(path):
    p = Extract()
    p.feed(path.read_text(encoding='utf-8'))
    return p


# Diferencias esperadas y aceptadas
IGNORED_META = {'generator', 'ti-site-data'}
REPLACED_PAGES = {'/agendar-en-linea/'}  # el widget de Bookly se reemplazó por un formulario propio


def main():
    errors = 0
    for fname, route in PAGES.items():
        a = parse(MIG / 'html-original' / fname)
        b = parse(OUT / route.lstrip('/') / 'index.html')
        problems = []
        if a.title.strip() != b.title.strip():
            problems.append('title: %r != %r' % (a.title, b.title))
        ma = {k: v for k, v in a.meta.items() if k not in IGNORED_META}
        mb = {k: v for k, v in b.meta.items() if k not in IGNORED_META}
        if ma != mb:
            problems.append('metas distintas: %s' % sorted(set(ma.items()) ^ set(mb.items())))
        if a.links.get('canonical') != b.links.get('canonical'):
            problems.append('canonical: %s != %s' % (a.links.get('canonical'), b.links.get('canonical')))
        if [norm_url(x) for x in a.links.get('icon', [])] != [norm_url(x) for x in b.links.get('icon', [])]:
            problems.append('favicon distinto')
        if a.ld != b.ld:
            problems.append('JSON-LD distinto')
        if a.headings != b.headings:
            problems.append('encabezados distintos: %s' % [h for h in a.headings if h not in b.headings][:5])
        if a.anchors != b.anchors:
            problems.append('enlaces distintos: %s' % sorted(set(a.anchors) ^ set(b.anchors))[:5])
        if a.images != b.images and route not in REPLACED_PAGES:
            problems.append('imágenes distintas: %s' % [i for i in a.images if i not in b.images][:5])
        if route not in REPLACED_PAGES and a.text != b.text:
            problems.append('texto visible distinto')
        for img, _alt in b.images:
            if img.startswith('/') and not (OUT / img.lstrip('/')).exists():
                if img != '/wp-content/uploads/2023/03/Peritaje-de-vehiculos-a-domicilio-en-bogota.jpg':  # ya era 404 en WordPress
                    problems.append('imagen sin archivo: ' + img)
        status = 'OK ' if not problems else 'ERR'
        print('%s %s' % (status, route))
        for p in problems:
            print('     - ' + p)
        errors += bool(problems)
    print('\n%d páginas, %d con diferencias' % (len(PAGES), errors))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
