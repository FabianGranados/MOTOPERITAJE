/*
 * Moto Peritaje — comportamiento del sitio estático.
 * Reemplaza el JavaScript que antes cargaban WordPress, Elementor, Elementor Pro y los plugins
 * (Cookie Notice, WhatsApp for WordPress, WPForms, Bookly). Sin dependencias, salvo Swiper
 * (solo en páginas con carrusel).
 */
(function () {
	'use strict';

	var WHATSAPP_PRINCIPAL = '573022507384';

	function parseSettings(el) {
		try {
			return JSON.parse(el.getAttribute('data-settings') || '{}');
		} catch (e) {
			return {};
		}
	}

	function waLink(number, text) {
		var n = String(number).replace(/[^0-9]/g, '');
		return 'https://api.whatsapp.com/send?phone=' + n + (text ? '&text=' + encodeURIComponent(text) : '');
	}

	function escapeHtml(s) {
		return String(s).replace(/[&<>"']/g, function (c) {
			return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
		});
	}

	/* ---------- Animaciones de entrada (Elementor "Motion effects") ---------- */
	function initAnimations() {
		var els = document.querySelectorAll('.elementor-invisible');
		if (!els.length) return;
		function show(el) {
			var s = parseSettings(el);
			var anim = s._animation || s.animation;
			el.classList.remove('elementor-invisible');
			if (anim && anim !== 'none') el.classList.add('animated', anim);
		}
		if (!('IntersectionObserver' in window)) {
			els.forEach(show);
			return;
		}
		var io = new IntersectionObserver(function (entries) {
			entries.forEach(function (e) {
				if (e.isIntersecting) {
					show(e.target);
					io.unobserve(e.target);
				}
			});
		});
		els.forEach(function (el) { io.observe(el); });
	}

	/* ---------- Menú (Elementor Pro nav-menu) ---------- */
	function initNavMenus() {
		document.querySelectorAll('.elementor-widget-nav-menu').forEach(function (widget) {
			var toggle = widget.querySelector('.elementor-menu-toggle');
			var dropdown = widget.querySelector('.elementor-nav-menu--dropdown');
			if (!toggle || !dropdown) return;
			function set(open) {
				toggle.classList.toggle('elementor-active', open);
				toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
				dropdown.setAttribute('aria-hidden', open ? 'false' : 'true');
				dropdown.querySelectorAll('a').forEach(function (a) {
					if (open) a.removeAttribute('tabindex');
					else a.setAttribute('tabindex', '-1');
				});
			}
			toggle.addEventListener('click', function () {
				set(!toggle.classList.contains('elementor-active'));
			});
			toggle.addEventListener('keydown', function (e) {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					toggle.click();
				}
			});
			dropdown.addEventListener('click', function (e) {
				if (e.target.closest('a')) set(false);
			});
		});
	}

	/* ---------- Pestañas, acordeones y toggles (Elementor) ---------- */
	function initTabs() {
		document.querySelectorAll('.elementor-widget-tabs').forEach(function (widget) {
			var titles = widget.querySelectorAll('.elementor-tab-title');
			var contents = widget.querySelectorAll('.elementor-tab-content');
			function activate(n) {
				titles.forEach(function (t) {
					var on = t.getAttribute('data-tab') === n;
					t.classList.toggle('elementor-active', on);
					t.setAttribute('aria-selected', on ? 'true' : 'false');
					t.setAttribute('aria-expanded', on ? 'true' : 'false');
					t.setAttribute('tabindex', on ? '0' : '-1');
				});
				contents.forEach(function (c) {
					var on = c.getAttribute('data-tab') === n;
					c.classList.toggle('elementor-active', on);
					c.style.display = on ? 'block' : '';
					if (on) c.removeAttribute('hidden');
					else c.setAttribute('hidden', 'hidden');
				});
			}
			titles.forEach(function (t) {
				t.addEventListener('click', function () {
					activate(t.getAttribute('data-tab'));
				});
				t.addEventListener('keydown', function (e) {
					if (e.key === 'Enter' || e.key === ' ') {
						e.preventDefault();
						t.click();
					}
				});
			});
			activate('1');
		});

		function initCollapsible(selector, openFirst) {
			document.querySelectorAll(selector).forEach(function (widget) {
				var titles = widget.querySelectorAll('.elementor-tab-title');
				titles.forEach(function (t) {
					var content = widget.querySelector('#' + t.getAttribute('aria-controls')) || t.nextElementSibling;
					function set(open) {
						t.classList.toggle('elementor-active', open);
						t.setAttribute('aria-expanded', open ? 'true' : 'false');
						if (!content) return;
						content.classList.toggle('elementor-active', open);
						content.style.display = open ? 'block' : 'none';
						if (open) content.removeAttribute('hidden');
						else content.setAttribute('hidden', 'hidden');
					}
					t._set = set;
					t.addEventListener('click', function () {
						var open = !t.classList.contains('elementor-active');
						if (openFirst && open) {
							titles.forEach(function (o) { if (o !== t && o._set) o._set(false); });
						}
						set(open);
					});
					t.addEventListener('keydown', function (e) {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							t.click();
						}
					});
				});
				// El acordeón de Elementor abre el primer elemento al cargar; el toggle no.
				if (openFirst && titles[0] && titles[0]._set) titles[0]._set(true);
			});
		}
		initCollapsible('.elementor-widget-accordion', true);
		initCollapsible('.elementor-widget-toggle', false);
	}

	/* ---------- Carruseles de imágenes (Elementor image-carousel + Swiper 8) ---------- */
	function initCarousels() {
		if (typeof window.Swiper === 'undefined') return;
		document.querySelectorAll('.elementor-widget-image-carousel').forEach(function (widget) {
			var s = parseSettings(widget);
			var container = widget.querySelector('.elementor-image-carousel-wrapper');
			if (!container) return;
			var slidesCount = container.querySelectorAll('.swiper-slide').length;
			var desktop = +s.slides_to_show || 3;
			var single = desktop === 1;
			var tablet = +s.slides_to_show_tablet || (single ? 1 : 2);
			var mobile = +s.slides_to_show_mobile || 1;
			function spacing(key, fallback) {
				var v = s[key];
				return v && v.size !== '' && v.size !== undefined ? +v.size : fallback;
			}
			var spaceDesktop = spacing('image_spacing_custom', 20);
			var spaceTablet = spacing('image_spacing_custom_tablet', spaceDesktop);
			var spaceMobile = spacing('image_spacing_custom_mobile', spaceTablet);
			var scroll = function (n, key) { return +s[key] || (s.slides_to_scroll ? Math.min(+s.slides_to_scroll, n) : 1); };

			var config = {
				slidesPerView: mobile,
				slidesPerGroup: scroll(mobile, 'slides_to_scroll_mobile'),
				spaceBetween: spaceMobile,
				loop: s.infinite === 'yes' && slidesCount > desktop,
				speed: +s.speed || 500,
				grabCursor: true,
				handleElementorBreakpoints: true,
				breakpoints: {
					768: { slidesPerView: tablet, slidesPerGroup: scroll(tablet, 'slides_to_scroll_tablet'), spaceBetween: spaceTablet },
					1025: { slidesPerView: desktop, slidesPerGroup: s.slides_to_scroll ? +s.slides_to_scroll : 1, spaceBetween: spaceDesktop }
				}
			};
			if (s.autoplay === 'yes') {
				config.autoplay = {
					delay: +s.autoplay_speed || 5000,
					disableOnInteraction: s.pause_on_interaction === 'yes',
					pauseOnMouseEnter: s.pause_on_hover === 'yes'
				};
			}
			var nav = s.navigation || 'both';
			if (nav === 'both' || nav === 'arrows') {
				config.navigation = {
					prevEl: widget.querySelector('.elementor-swiper-button-prev'),
					nextEl: widget.querySelector('.elementor-swiper-button-next')
				};
			}
			if (nav === 'both' || nav === 'dots') {
				config.pagination = { el: widget.querySelector('.swiper-pagination'), type: 'bullets', clickable: true };
			}
			new window.Swiper(container, config);
		});
	}

	/* ---------- Aviso de cookies (Cookie Notice) ---------- */
	function initCookieNotice() {
		var notice = document.getElementById('cookie-notice');
		if (!notice) return;
		var name = 'cookie_notice_accepted';
		var accepted = document.cookie.split('; ').some(function (c) { return c.indexOf(name + '=') === 0; });
		function setBodyState(isSet) {
			document.body.classList.toggle('cookies-set', isSet);
			document.body.classList.toggle('cookies-not-set', !isSet);
		}
		if (accepted) {
			setBodyState(true);
			return;
		}
		notice.classList.remove('cookie-notice-hidden');
		notice.classList.add('cookie-notice-visible', 'cn-animated', 'cn-effect-fade');
		notice.querySelectorAll('[data-cookie-set]').forEach(function (btn) {
			btn.addEventListener('click', function (e) {
				e.preventDefault();
				var value = btn.getAttribute('data-cookie-set') === 'accept' ? 'true' : 'false';
				var expires = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toUTCString();
				document.cookie = name + '=' + value + ';expires=' + expires + ';path=/;SameSite=Lax' + (location.protocol === 'https:' ? ';secure' : '');
				notice.classList.remove('cookie-notice-visible');
				notice.classList.add('cookie-notice-hidden');
				setBodyState(true);
			});
		});
	}

	/* ---------- Botones de WhatsApp (WhatsApp for WordPress) ---------- */
	function accountButton(info, extraClass) {
		var i = info.info || {};
		var st = info.styles || {};
		var a = document.createElement('a');
		a.href = waLink(i.number, i.predefinedText || '');
		a.target = '_blank';
		a.rel = 'nofollow noopener';
		a.className = 'wa__button ' + (st.type === 'square' ? 'wa__sq_button' : 'wa__r_button') + ' wa__stt_online wa__btn_w_img' + (extraClass ? ' ' + extraClass : '');
		if (!extraClass) {
			a.style.backgroundColor = st.backgroundColor || '#2DB742';
			a.style.color = st.textColor || '#fff';
			if (st.width) a.style.width = st.width + 'px';
			if (st.height) a.style.minHeight = st.height + 'px';
		}
		var avatar = info.avatar || info.defaultAvatar || '';
		a.innerHTML =
			'<div class="wa__cs_img"><div class="wa__cs_img_wrap" style="background:url(\'' + escapeHtml(avatar) + '\') center center no-repeat;background-size:cover"></div></div>' +
			'<div class="wa__btn_txt"><div class="wa__cs_info"><div class="wa__cs_name">' + escapeHtml(info.name || '') + '</div><div class="wa__cs_status">Online</div></div>' +
			'<div class="wa__btn_title">' + escapeHtml(extraClass ? (i.title || st.label || '') : (st.label || i.title || '')) + '</div></div>';
		return a;
	}

	function initWhatsApp() {
		var accounts = [];
		document.querySelectorAll('.nta_wa_button[data-info]').forEach(function (el) {
			var info;
			try {
				info = JSON.parse(el.getAttribute('data-info'));
			} catch (e) {
				return;
			}
			if (info.avatar) info.avatar = info.avatar.replace(/^https?:\/\/motoperitaje\.com/, '');
			el.innerHTML = '';
			el.appendChild(accountButton(info));
		});

		// Botón flotante (widget global del plugin)
		var holder = document.getElementById('wa');
		var data = window.MP_WHATSAPP_WIDGET;
		if (!holder || !data) return;
		accounts = data.accounts || [];
		var widget = document.createElement('div');
		widget.className = 'wa__widget';
		widget.innerHTML =
			'<div class="wa__popup_chat_box" role="dialog" aria-label="' + escapeHtml(data.title) + '">' +
			'<div class="wa__popup_heading"><div class="wa__popup_title">' + escapeHtml(data.title) + '</div>' +
			'<div class="wa__popup_intro">' + escapeHtml(data.description) + '</div>' +
			'<button type="button" class="wa__popup_close" aria-label="Cerrar">&times;</button></div>' +
			'<div class="wa__popup_content"><div class="wa__popup_notice">' + escapeHtml(data.notice || '') + '</div></div></div>' +
			'<div class="wa__btn_popup" role="button" tabindex="0" aria-label="WhatsApp">' +
			(data.label ? '<div class="wa__btn_popup_txt" style="width:' + (data.labelWidth || 156) + 'px">' + data.label + '</div>' : '') +
			'<div class="wa__btn_popup_icon"></div></div>';
		var content = widget.querySelector('.wa__popup_content');
		accounts.forEach(function (acc) { content.appendChild(accountButton(acc, 'wa__popup_account')); });
		var box = widget.querySelector('.wa__popup_chat_box');
		var btn = widget.querySelector('.wa__btn_popup');
		btn.addEventListener('click', function () { box.classList.toggle('wa__active'); });
		btn.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); btn.click(); } });
		widget.querySelector('.wa__popup_close').addEventListener('click', function () { box.classList.remove('wa__active'); });
		holder.appendChild(widget);
	}

	/* ---------- Formularios (antes WPForms / Bookly): se envían por WhatsApp ---------- */
	function initForms() {
		document.querySelectorAll('form.wpforms-form, form.mp-form-whatsapp').forEach(function (form) {
			form.addEventListener('submit', function (e) {
				e.preventDefault();
				if (!form.reportValidity()) return;
				var lines = [];
				form.querySelectorAll('.wpforms-field, .mp-campo').forEach(function (field) {
					var label = field.querySelector('label');
					var input = field.querySelector('input, textarea, select');
					if (!label || !input || !input.value) return;
					lines.push(label.textContent.replace('*', '').trim() + ': ' + input.value.trim());
				});
				var intro = form.getAttribute('data-wa-intro') || 'Hola, les escribo desde la página ' + document.title + ':';
				var number = form.getAttribute('data-wa-number') || WHATSAPP_PRINCIPAL;
				window.open(waLink(number, intro + '\n' + lines.join('\n')), '_blank');
				var container = form.closest('.wpforms-container') || form.parentNode;
				var ok = document.createElement('div');
				ok.className = 'wpforms-confirmation-container-full';
				ok.setAttribute('role', 'alert');
				ok.innerHTML = '<p>¡Gracias por contactarnos! Abrimos WhatsApp para que nos envíes tu mensaje. Si no se abrió, escríbenos al <a href="' + waLink(number) + '" target="_blank" rel="noopener">302 250 7384</a>.</p>';
				form.style.display = 'none';
				container.appendChild(ok);
			});
		});
	}

	function init() {
		initAnimations();
		initNavMenus();
		initTabs();
		initCarousels();
		initCookieNotice();
		initWhatsApp();
		initForms();
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
	else init();
})();
