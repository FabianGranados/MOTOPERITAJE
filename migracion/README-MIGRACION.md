# Moto Peritaje (motoperitaje.com) — Paquete de migración WordPress → código

Extraído del sitio en vivo el 2026-10-04. Objetivo: **réplica exacta** del sitio actual (mismo contenido, URLs, SEO y aspecto), pero en código estático sin WordPress.

## Cómo está construido hoy
- WordPress + **Elementor** (todas las páginas y entradas usan la plantilla *Elementor Canvas*: el encabezado, menú y pie de página están **dentro** del contenido de cada página, no en el tema). Tema base: automobile-hub (casi no se ve).
- SEO: plugin **All in One SEO 4.9.8** (titles, descriptions, schema JSON-LD y sitemaps).
- Plugins visibles en el front: Call Now Button (botón flotante "Llama ya..." → tel:3022507384), botones de WhatsApp (wa.me/573022507384), **Trustindex** (widget de reseñas de Google, script cdn.trustindex.io/loader.js), Cookie Notice (banner de cookies), Elementor Pro (formularios, menú).
- Analítica: **G-K1BMVYM7ZX · GTM-WNWDNRD** (Google Tag / GA4 y Google Tag Manager). Hay un contenedor de Facebook Pixel (`fb-pxl-ajax-code`) pero no se encontró ID de píxel en el HTML.
- Teléfono / WhatsApp: **302 250 7384**. Direcciones que aparecen: Carrera 50 #2-49, B. Jazmín · Calle 134 # 46-35, Prado Veraniego (Bogotá). Horario: Lunes a Viernes 8:00 a.m.–4:00 p.m.; Sábados 8:00 a.m.–1:00 p.m. (verificar en paginas/*.md).

## URLs indexadas (conservar EXACTAS, con slash final)
| Tipo | Ruta | <title> | meta description |
| --- | --- | --- | --- |
| Página | / | Peritaje de Motos en Bogotá - Avalúo Profesional y Preciso | Peritaje y avalúo de motos en Bogotá con tecnología avanzada: escáneres, analizador de gases y más. ¡Agenda tu cita ahora! 3022507384 |
| Página | /precio-peritaje-moto/ | Peritaje de Motos en Bogotá \| Precios, Avalúo y Servicio Profesional | Realiza tu peritaje de moto en Bogotá con expertos. Inspección precisa, avalúo confiable y asesoría profesional. ¡Agenda por WhatsApp 3022507384! |
| Página | /peritaje-de-motos-a-domicilio-en-bogota/ | Peritaje de Motos a Domicilio en Bogotá \| Compra Segura | Peritaje de moto a domicilio en Bogotá. Revisamos la moto antes de comprarla y te entregamos informe técnico completo. Agenda hoy mismo 301 9262267. |
| Página | /contactanos/ | Contáctanos \| peritaje profesional de motos en bogotá | Motoperitaje Bogotá. Estamos ubicados en Puente Aranda Carrera 50 #2-49. B. Jazmín. Te puedes comunicar con nuestra asesora comercial al 302 2507384. |
| Página | /agendar-en-linea/ | Agendar en Línea \| Peritaje de Motos HOY en Bogotá, Sin Cita Previa \| Motoperitaje | PERITAJE PROFESIONAL DE MOTOS EN BOGOTÁ ¡TU ALIADO EXPERTO ANTES DE COMPRAR! ESTAMOS UBICADOS EN Carrera 50 #2-49. B. Jazmín Calle 134 # 46-35 - Prado Veraniego HORARIOS DE ATENCIÓN Lunes a Viernes: 8:00 a.m. a 4:00 p.m.Sábados: 8:00 a.m. a 1:00 p.m. Copyright 2025 © Moto Peritaje \| Todos los derechos reservados |
| Página | /blog/ | Blog Especializado en Peritaje de Motos - Moto Peritaje | Bienvenid@ al blog de MOTOPERITAJE tu fuente de información confiable y actualizada sobre evaluación y peritaje de motos. |
| Página | /politica-de-tratamiento-de-datos/ | Política de tratamiento de datos \| Motoperitaje | Política de tratamiento de datos personales, como empresa debemos garantizar que nuestros clientes conozcan y autoricen el manejo de su información. |
| Entrada blog | /todo-lo-que-necesitas-saber-sobre-el-peritaje-de-motos/ | Peritaje de motos: Todo lo que debes saber antes de comprar o vender | Descubre por qué el peritaje de motos es clave al comprar o vender una usada. Conoce cómo se realiza, qué revisan los expertos y evita fraudes. |
| Entrada blog | /como-el-peritaje-revela-su-verdadero-precio-en-el-mercado-de-las-motos/ | Cómo el peritaje revela su verdadero precio en el mercado de las motos | Cuando se trata de comprar o vender una moto, determinar su valor real en el mercado puede ser un desafío. ¡Descubre más!. |
| Entrada blog | /importancia-del-peritaje-de-motos-en-casos-de-accidentes/ | Importancia del peritaje de motos en accidentes: Guía esencial | Conoce por qué el peritaje de motos es clave tras un accidente. Ayuda a determinar causas, responsabilidades y obtener una evaluación técnica confiable. |
| Entrada blog | /que-documentacion-necesito-para-realizar-un-peritaje-de-motos-en-bogota/ | Documentos para peritaje de motos en Bogotá: Guía rápida 2026 | Descubre qué documentos necesitas para realizar un peritaje de motos en Bogotá. Ahorra tiempo y evita retrasos con esta guía práctica paso a paso. |
| Entrada blog | /que-tipo-de-informacion-se-recopila-durante-un-peritaje-de-motos/ | ¿Qué se analiza en un peritaje de motos? Información clave 2026 | Descubre qué datos se recopilan en un peritaje de motos: estado mecánico, chasis, documentos y más. Entiende cada parte del proceso paso a paso. |
| Entrada blog | /las-marcas-de-motos-mas-populares/ | Las marcas de motos más populares y confiables en 2026 \| Motoperitaje | Conoce las marcas de motos más populares del mundo. Descubre su historia, modelos destacados y cuál se adapta mejor a tu estilo de conducción. |
| Entrada blog | /como-preparar-tu-moto-para-un-viaje-seguro-consejos-esenciales/ | Cómo preparar tu moto para un viaje seguro: Guía práctica 2026 | Descubre cómo preparar tu moto antes de viajar. Revisa frenos, llantas y equipaje con estos consejos esenciales para un viaje seguro y sin imprevistos. |
| Entrada blog | /iluminando-el-camino-luces-led-para-motos/ | Luces LED para motos: Más visibilidad y seguridad en la vía | Conoce las ventajas de las luces LED para motos. Mejora tu visibilidad, ahorra energía y viaja con mayor seguridad en cualquier camino. |
| Entrada blog | /historia-de-las-motos/ | Historia de las Motocicletas | Sumérgete en un viaje fascinante a través de la historia de las motocicletas. Desde los primeros intentos de motorizar bicicletas hasta las icónicas máquinas que dominan las carreteras de hoy. |
| Entrada blog | /importancia-del-equipo-de-proteccion-para-motociclistas/ | Equipo de protección para motociclistas \| Moto Peritaje | Descubre la importancia del casco, chaqueta y guantes. Aprende cómo el equipo de protección mantiene tu seguridad al conducir motocicleta. |
| Entrada blog | /mejores-accesorios-para-motociclistas/ | Mejores Accesorios para Motociclistas \| Moto Peritaje | Encuentra los mejores accesorios para motociclistas: cascos, guantes, chaquetas y gadgets. Mejora tu estilo y seguridad en cada viaje. |
| Entrada blog | /guia-de-mantenimiento-preventivo-para-motos-usadas/ | Guía de Mantenimiento Preventivo para Motos Usadas \| Moto Peritaje | Aprende el mantenimiento preventivo para motos usadas: checklist, consejos y cuidados para alargar la vida de tu moto y ahorrar en reparaciones. |
| Entrada blog | /que-revisar-antes-de-comprar-una-moto-usada-en-bogota/ | Qué revisar antes de comprar una moto usada en Bogotá | Guía para comprar moto usada en Bogotá: revisa documentos, mecánica, historial y señales de alerta. Aprende a elegir una moto segura y sin riesgos. |
| Categoría | /category/uncategorized/ | Uncategorized \| Peritaje de Motos HOY en Bogotá, Sin Cita Previa \| Motoperitaje |  |

Sitemaps originales en `sitemaps/` (AIOSEO: sitemap.xml índice → page-sitemap, post-sitemap, category-sitemap, addl-sitemap; además sitemap.rss).

## Menú principal (igual en todas las páginas)
Inicio · Precio Peritaje Motos · Precios a Domicilio · Peritaje Carros · Contáctanos · Blog
Enlaces: Inicio → / · Precio Peritaje Motos → /precio-peritaje-moto/ · Precios a Domicilio → /peritaje-de-motos-a-domicilio-en-bogota/ · **Peritaje Carros → https://granautos.com.co/precio-peritaje-carro/ (externo)** · Contáctanos → /contactanos/ · Blog → /blog/

## Diseño (valores medidos en el navegador, viewport 1920x945)
- Tipografías: **Roboto** (cuerpo y la mayoría de títulos) y **Roboto Slab** (variables globales de Elementor). Archivos woff2 en `fuentes/`.
- Color de marca principal: **#6E0000** (rgb 110,0,0 — botones y acentos). Rojo secundario: **#DD1414**. Texto gris: **#676767**. Negro #000 y blanco #FFF.
- Botón tipo: fondo #6E0000, texto blanco, Roboto 15px/500, padding 12px 24px, borde 3px double #FFF, radio 3px.
- Variables globales de Elementor (kit) y medidas detalladas: `diseno.json`.
- Estilos exactos por elemento: `css-original/post-<ID>.css` (selector `.elementor-element-<id>`; el id de cada bloque aparece como `[sección …]` en paginas/*.md y en html-original/).
- No se pudieron generar capturas de pantalla automáticas; el HTML original + CSS permiten reconstruir el aspecto exacto. Si se requiere, tomar capturas manuales del sitio antes de apagarlo.

## Logos
En `logos/` (copias) — el logo del encabezado es **Motoperitaje.com_.webp** (versión recortada por Elementor: `Motoperitaje.com_-qoz5…webp`). Favicon/ícono del sitio: **cropped-Moto-Peritaje-Bogota.png** (512×512).

## Estructura del paquete
- `paginas/` — una ficha .md por página/entrada con SEO, todo el texto en orden, botones con su enlace, imágenes (alt) y formularios; .json con los mismos datos estructurados.
- `imagenes/` — 108 imágenes originales (nombre original de WordPress). `imagenes/_manifest.csv` indica en qué páginas se usa cada una.
- `logos/`, `fuentes/`, `diseno.json`
- `html-original/` — HTML completo de cada URL tal como lo sirve WordPress hoy.
- `css-original/` — CSS de Elementor (kit global post-5.css + uno por página) y del tema.
- `sitemaps/` — sitemaps y robots.txt originales.

## Notas / pendientes
- Imágenes que el HTML referencia pero ya dan 404 en el servidor (no incluidas): 2023/03/Peritaje-de-vehiculos-a-domicilio-en-bogota.jpg y dos miniaturas de Elementor en 2024/05/elementor/thumbs/.
- La categoría /category/uncategorized/ está indexada; decidir si se mantiene o se redirige 301 a /blog/.
- Los formularios de las entradas del blog son de comentarios/Elementor: en un sitio estático hay que reemplazarlos (WhatsApp o un servicio de formularios).
