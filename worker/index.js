/**
 * Worker de Cloudflare para motoperitaje.com.
 *
 * Sirve el sitio estático de ./public (binding ASSETS) y replica las redirecciones que hacía
 * WordPress, todas como 301 para no perder posicionamiento:
 *   - www.motoperitaje.com -> motoperitaje.com
 *   - URLs sin slash final -> con slash final (/contactanos -> /contactanos/)
 *   - Atajos de WordPress  /?p=ID y /?page_id=ID -> URL definitiva
 *   - Feeds y rutas de administración de WordPress
 */
import atajos from './atajos.json';

const DOMINIO = 'motoperitaje.com';

const PERMANENTES = [
	[/^\/index\.php$/, '/'],
	[/^\/(comments\/)?feed\/?$/, '/blog/'],
	[/^\/(.+?)\/feed\/?$/, '/$1/'],
	[/^\/home\/?$/, '/'],
];

const TEMPORALES = [
	[/^\/(wp-admin(\/.*)?|wp-login\.php)$/, '/'],
];

function redirigir(url, path, status) {
	return Response.redirect(new URL(path, url).toString(), status);
}

export default {
	async fetch(request, env) {
		const url = new URL(request.url);

		if (url.hostname === 'www.' + DOMINIO) {
			url.hostname = DOMINIO;
			url.protocol = 'https:';
			return Response.redirect(url.toString(), 301);
		}

		if (url.pathname === '/') {
			const id = url.searchParams.get('p') || url.searchParams.get('page_id');
			if (id && atajos[id]) return redirigir(url, atajos[id], 301);
		}

		for (const [re, destino] of PERMANENTES) {
			if (re.test(url.pathname)) return redirigir(url, url.pathname.replace(re, destino), 301);
		}
		for (const [re, destino] of TEMPORALES) {
			if (re.test(url.pathname)) return redirigir(url, destino, 302);
		}

		// Slash final obligatorio en las páginas (no en archivos con extensión), igual que WordPress.
		const ultimo = url.pathname.split('/').pop();
		if (ultimo && !ultimo.includes('.')) {
			url.pathname += '/';
			return Response.redirect(url.toString(), 301);
		}

		const respuesta = await env.ASSETS.fetch(request);
		if (url.pathname.startsWith('/wp-content/') && respuesta.ok) {
			const r = new Response(respuesta.body, respuesta);
			r.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
			return r;
		}
		return respuesta;
	},
};
