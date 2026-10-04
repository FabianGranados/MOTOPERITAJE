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

	/* ---------- Botones de WhatsApp (plugin "WhatsApp for WordPress" de NinjaTeam) ----------
	 * Reproduce el marcado exacto que generaba el plugin (window.njtWhatsApp en el JS de LiteSpeed),
	 * para que su hoja de estilos original (whatsapp-for-wordpress/assets/dist/css/style.css) aplique igual.
	 * La configuración del botón flotante llega en window.MP_WHATSAPP (objeto njt_wa original). */
	var WA_I18N = { online: 'Online', offline: 'Offline' };

	function waHref(acc) {
		var n = String(acc.number || '');
		if (n.indexOf('chat.whatsapp.com') !== -1) return n;
		var text = (acc.predefinedText || '')
			.replace(/\[njwa_page_title\]/gi, encodeURIComponent(document.title))
			.replace(/\[njwa_page_url\]/gi, window.location.href)
			.replace(/\n/gi, '%0A');
		return 'https://api.whatsapp.com/send?phone=' + n.replace(/[^0-9]/g, '') + (acc.predefinedText ? '&text=' + text : '');
	}

	function el(tag, cls, html) {
		var e = document.createElement(tag);
		if (cls) e.className = cls;
		if (html !== undefined) e.innerHTML = html;
		return e;
	}

	function localUrl(u) {
		return String(u || '').replace(/^https?:\/\/motoperitaje\.com/, '');
	}

	function createWaButton(holder, data) {
		var info = data.info || {};
		var st = data.styles || {};
		var avatar = localUrl(data.avatar);
		var a = el('a', 'wa__button' + (st.type === 'round' ? ' wa__r_button' : ' wa__sq_button') + ' wa__stt_online' +
			(avatar ? ' wa__btn_w_img' : ' wa__btn_w_icon') + (data.name ? '' : ' wa__button_text_only'));
		a.setAttribute('target', '_blank');
		a.setAttribute('href', waHref(info));
		a.setAttribute('rel', 'nofollow noopener noreferrer');
		a.style.backgroundColor = st.backgroundColor;

		var img = el('div', avatar ? 'wa__cs_img' : 'wa__btn_icon');
		if (avatar) {
			var wrap = el('div', 'wa__cs_img_wrap');
			wrap.setAttribute('style', 'background: url(' + avatar + ') center center no-repeat; background-size: cover');
			img.appendChild(wrap);
		} else {
			var i = el('img');
			i.alt = 'img';
			i.src = localUrl(data.defaultAvatar);
			img.appendChild(i);
		}
		var white = st.textColor === '#fff' || st.textColor === '#ffffff';
		var txt = el('div', 'wa__btn_txt');
		if (data.name) {
			var csInfo = el('div', 'wa__cs_info');
			var name = el('div', 'wa__cs_name', escapeHtml(data.name));
			name.setAttribute('style', 'color: ' + (white ? '#d5f0d9' : st.textColor) + '; opacity: ' + (white ? 1 : 0.8));
			csInfo.appendChild(name);
			csInfo.appendChild(el('div', 'wa__cs_status', WA_I18N.online));
			txt.appendChild(csInfo);
		}
		var title = el('div', 'wa__btn_title', st.label || '');
		title.setAttribute('style', 'color: ' + st.textColor);
		txt.appendChild(title);
		a.appendChild(img);
		a.appendChild(txt);
		holder.innerHTML = '';
		holder.appendChild(a);
	}

	function createWaWidget(holder, cfg) {
		var s = cfg.options.styles;
		holder.classList.add('wa__widget_container');

		var label = el('div', 'wa__btn_popup_txt');
		label.appendChild(el('span', '', s.btnLabel));
		label.style.display = s.isShowBtnLabel === 'ON' ? 'block' : 'none';
		label.style.left = s.btnPosition === 'left' ? '100%' : 'unset';
		label.style.right = s.btnPosition === 'right' ? '100%' : 'unset';
		label.style.marginRight = s.btnPosition === 'right' ? '7px' : '0px';
		label.style.marginLeft = s.btnPosition === 'left' ? '7px' : '0px';
		label.style.width = s.btnLabelWidth + 'px';
		var icon = el('div', 'wa__btn_popup_icon');
		icon.style.background = s.backgroundColor;
		var btn = el('div', 'wa__btn_popup');
		btn.appendChild(label);
		btn.appendChild(icon);
		btn.style.left = s.btnPosition === 'left' ? parseInt(s.btnLeftDistance, 10) + 'px' : 'unset';
		btn.style.right = s.btnPosition === 'right' ? parseInt(s.btnRightDistance, 10) + 'px' : 'unset';
		btn.style.bottom = parseInt(s.btnBottomDistance, 10) + 'px';
		holder.appendChild(btn);

		var white = s.textColor === '#fff' || s.textColor === '#ffffff';
		var heading = el('div', 'wa__popup_heading');
		heading.style.background = s.backgroundColor;
		var title = el('div', 'wa__popup_title', s.title);
		title.style.color = s.textColor;
		title.style.fontSize = s.titleSize + 'px';
		var intro = el('div', 'wa__popup_intro', s.description.replace(/\r\n\r\n/gm, '<br/>'));
		intro.setAttribute('style', white ? 'color: #D9EBC6' : 'color: ' + s.textColor + '; opacity: 0.8');
		intro.style.fontSize = s.descriptionTextSize + 'px';
		heading.appendChild(title);
		heading.appendChild(intro);

		var content = el('div', 'wa__popup_content wa__popup_content_left');
		var notice = el('div', 'wa__popup_notice', s.responseText.replace(/\r\n\r\n/gm, '<br/>'));
		notice.style.fontSize = s.regularTextSize + 'px';
		content.appendChild(notice);
		var list = el('div', 'wa__popup_content_list');
		cfg.accounts.forEach(function (acc) {
			var avatar = localUrl(acc.avatar);
			var av = el('div', 'wa__popup_avatar' + (avatar ? '' : ' nta-default-avt'));
			if (avatar) {
				var w = el('div', 'wa__cs_img_wrap');
				w.setAttribute('style', 'background: url(' + avatar + ') center center no-repeat; background-size: cover;');
				av.appendChild(w);
			}
			var item = el('div', 'wa__popup_content_item');
			var link = el('a', 'wa__stt wa__stt_online');
			link.setAttribute('target', '_blank');
			link.setAttribute('href', waHref(acc));
			link.setAttribute('rel', 'nofollow noopener noreferrer');
			link.appendChild(av);
			link.appendChild(el('div', 'wa__popup_txt',
				'<div class="wa__member_name" style=\'font-size:' + s.accountNameSize + 'px\'>' + escapeHtml(acc.accountName) + '</div>' +
				'<div class="wa__member_duty" style=\'font-size:' + s.regularTextSize + 'px\'>' + escapeHtml(acc.title) + '</div>'));
			item.appendChild(link);
			list.appendChild(item);
		});
		content.appendChild(list);
		if (s.isShowScroll === 'ON') {
			content.style.maxHeight = parseInt(s.scrollHeight, 10) + 'px';
			content.style.overflow = 'auto';
		}
		var box = el('div', 'wa__popup_chat_box');
		box.appendChild(heading);
		box.appendChild(content);
		box.style.left = s.btnPosition === 'left' ? parseInt(s.btnLeftDistance, 10) + 'px' : 'unset';
		box.style.right = s.btnPosition === 'right' ? parseInt(s.btnRightDistance, 10) + 'px' : 'unset';
		box.style.bottom = parseInt(s.btnBottomDistance, 10) + 72 + 'px';
		holder.appendChild(box);

		var t1, t2;
		btn.addEventListener('click', function () {
			if (box.classList.contains('wa__active')) {
				box.classList.remove('wa__active');
				btn.classList.remove('wa__active');
				clearTimeout(t2);
				if (box.classList.contains('wa__lauch')) {
					t1 = setTimeout(function () { box.classList.remove('wa__pending', 'wa__lauch'); }, 400);
				}
			} else {
				box.classList.add('wa__pending', 'wa__active');
				btn.classList.add('wa__active');
				clearTimeout(t1);
				if (!box.classList.contains('wa__lauch')) {
					t2 = setTimeout(function () { box.classList.add('wa__lauch'); }, 100);
				}
			}
		});
	}

	function initWhatsApp() {
		document.querySelectorAll('.nta_wa_button[data-info]').forEach(function (holder) {
			try {
				createWaButton(holder, JSON.parse(holder.getAttribute('data-info')));
			} catch (e) { /* configuración inválida: se deja vacío como hacía el plugin */ }
		});
		var holder = document.getElementById('wa');
		if (holder && window.MP_WHATSAPP) createWaWidget(holder, window.MP_WHATSAPP);
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
