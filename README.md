# motoperitaje.com — sitio estático (migración desde WordPress)

Réplica exacta del sitio WordPress + Elementor de **motoperitaje.com**, sin WordPress.
Mismas URLs (con slash final), mismos `<title>`, metas, canonical, Open Graph, schema JSON-LD,
textos, imágenes y diseño.

## Estructura

| Carpeta | Qué es |
| --- | --- |
| `public/` | **El sitio listo para publicar.** Es lo que se sube al hosting. Se genera, no se edita a mano. |
| `migracion/` | Paquete extraído del WordPress en vivo: HTML original de cada URL, CSS de Elementor, imágenes, fuentes, sitemaps. Es la fuente de verdad. |
| `src/assets/js/sitio.js` | JavaScript propio que reemplaza a WordPress/Elementor/plugins: menú móvil, pestañas, acordeones, carruseles, aviso de cookies, botones de WhatsApp y formularios. |
| `src/reconstruido/` | CSS que **no venía** en el paquete, reconstruido a mano en su ruta original. Si se consigue el original, se pone en `migracion/wp-originales/<misma ruta>` y gana sobre el reconstruido. |
| `src/raiz/` | `vercel.json` y `.htaccess` base (redirecciones, slash final, caché). |
| `vendor/` | Librerías tomadas de npm en la versión que usaba el sitio (Font Awesome 5.15.3, Swiper 8.4.5, Bootstrap 4 del tema, animate.css). |
| `scripts/` | `build.py` (genera `public/`) y `verificar_seo.py` (compara original vs. generado). |

## Generar y verificar

```bash
pip install -r scripts/requirements.txt
python3 scripts/build.py          # genera public/
python3 scripts/verificar_seo.py  # debe terminar en "0 con diferencias"
python3 -m http.server -d public 8000   # vista local en http://localhost:8000
```

## Publicar

- **Hosting actual (Apache/LiteSpeed, cPanel):** subir el contenido de `public/` (incluido `.htaccess`) a `public_html` en lugar de WordPress.
- **Vercel:** proyecto con *Output Directory* = `public` y sin comando de build (`public/vercel.json` ya trae slash final y redirecciones).

## Qué cambió respecto a WordPress (a propósito)

- Las imágenes cargan directo (`src`) en lugar del lazy-load por JavaScript de Smush; se usa `loading="lazy"` nativo.
- Analítica: se conserva Google Analytics `G-K1BMVYM7ZX`, Google Tag Manager `GTM-WNWDNRD` y el Meta Pixel `1200120341805655`, cargados una sola vez (antes MonsterInsights y Site Kit cargaban gtag por duplicado).
- Formularios: el de contacto (WPForms) y el de agendar (Bookly) no tienen servidor; al enviarlos abren WhatsApp (302 250 7384) con los datos escritos.
- `/?p=ID` (enlaces cortos de WordPress) redirigen 301 a la URL definitiva.
- Archivos por fecha, autor y la página 2 de la categoría no venían en el paquete: redirigen temporalmente (302) a `/blog/` o a la categoría.
