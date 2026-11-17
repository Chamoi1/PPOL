/* ==========================================================================
   PPOL KINETIC SILK INTERACTION ENGINE
   ========================================================================== */
(function () {
  'use strict';

  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ------------------------------------------------------------------------
  // 1. Theme & Zen Mode Initialization
  // ------------------------------------------------------------------------
  const THEME_KEY = 'ppol_theme';
  const ZEN_KEY = 'ppol_zen';

  function applyTheme(theme) {
    const html = document.documentElement;
    if (theme === 'twilight') {
      html.setAttribute('data-theme', 'twilight');
    } else {
      html.removeAttribute('data-theme');
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === 'twilight' ? '#0b1120' : '#f2f5fa';

    const btn = document.getElementById('ppol-theme-toggle');
    if (btn) {
      const icon = btn.querySelector('i');
      const label = btn.querySelector('.theme-label');
      if (icon) icon.className = theme === 'twilight' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
      if (label) label.textContent = theme === 'twilight' ? 'Día' : 'Noche';
    }
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') === 'twilight' ? 'twilight' : 'daylight';
    const next = current === 'twilight' ? 'daylight' : 'twilight';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  }

  function applyZen(enabled) {
    document.body.classList.toggle('zen-mode', !!enabled);
    localStorage.setItem(ZEN_KEY, enabled ? '1' : '0');
  }

  window.ppolToggleTheme = toggleTheme;
  window.ppolToggleZen = function () {
    applyZen(!document.body.classList.contains('zen-mode'));
  };

  // Apply immediately
  applyTheme(localStorage.getItem(THEME_KEY) || 'daylight');

  // ------------------------------------------------------------------------
  // 2. Ambient Silk Constellation Canvas
  // ------------------------------------------------------------------------
  function initAmbientCanvas() {
    const canvas = document.getElementById('ppol-ambient-canvas');
    if (!canvas || prefersReduced) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let dpr = Math.min(window.devicePixelRatio || 1, 2);
    let particles = [];
    let pointer = { x: -9999, y: -9999, active: false };
    let rafId = null;

    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const count = Math.min(34, Math.max(14, Math.floor((width * height) / 48000)));
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.28,
        vy: (Math.random() - 0.5) * 0.28,
        r: Math.random() * 2.2 + 1.2,
        hue: Math.random() > 0.5 ? '59, 130, 246' : '16, 185, 129',
      }));
    }

    window.addEventListener('resize', resize, { passive: true });
    window.addEventListener('mousemove', (e) => {
      pointer.x = e.clientX;
      pointer.y = e.clientY;
      pointer.active = true;
    }, { passive: true });
    window.addEventListener('mouseleave', () => { pointer.active = false; });

    function tick() {
      if (document.hidden || document.body.classList.contains('zen-mode')) {
        rafId = requestAnimationFrame(tick);
        return;
      }
      ctx.clearRect(0, 0, width, height);
      const isDark = document.documentElement.getAttribute('data-theme') === 'twilight';
      const dotAlpha = isDark ? 0.38 : 0.28;
      const lineAlpha = isDark ? 0.12 : 0.08;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        if (pointer.active) {
          const dx = pointer.x - p.x;
          const dy = pointer.y - p.y;
          const dist = Math.hypot(dx, dy);
          if (dist < 170 && dist > 1) {
            p.x += (dx / dist) * 0.16;
            p.y += (dy / dist) * 0.16;
          }
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.hue}, ${dotAlpha})`;
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j];
          const d = Math.hypot(p.x - q.x, p.y - q.y);
          if (d < 135) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = `rgba(99, 102, 241, ${(1 - d / 135) * lineAlpha})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      rafId = requestAnimationFrame(tick);
    }

    resize();
    rafId = requestAnimationFrame(tick);
  }

  // ------------------------------------------------------------------------
  // 3. Cursor-Tracking Spotlight on Cards & KPIs
  // ------------------------------------------------------------------------
  function initCardSpotlight() {
    document.addEventListener('mousemove', (e) => {
      const card = e.target.closest('.card.interactive, .kpi-card');
      if (!card) return;
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty('--mx', `${x}px`);
      card.style.setProperty('--my', `${y}px`);
    }, { passive: true });
  }

  // ------------------------------------------------------------------------
  // 4. Staggered Scroll-Reveal & KPI Number Count-Up
  // ------------------------------------------------------------------------
  function initScrollRevealAndCounters() {
    const targets = document.querySelectorAll(
      'main .card, main .kpi-card, main .search-box-card, main .empty-state, main .history-shell'
    );
    if (!targets.length) return;

    if (prefersReduced || document.body.classList.contains('zen-mode') || !('IntersectionObserver' in window)) {
      targets.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    let batchIndex = 0;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const delay = Math.min((batchIndex % 8) * 55, 385);
        batchIndex++;
        el.style.setProperty('--reveal-delay', `${delay}ms`);
        el.classList.add('is-visible');
        observer.unobserve(el);

        // Animate KPI numbers inside this element
        el.querySelectorAll('.kpi-card b, b[data-count]').forEach(animateCounter);
        if (el.classList.contains('kpi-card')) {
          const b = el.querySelector('b');
          if (b) animateCounter(b);
        }
      });
    }, { threshold: 0.06, rootMargin: '0px 0px -20px 0px' });

    targets.forEach((el) => {
      el.classList.add('ppol-reveal');
      observer.observe(el);
    });
  }

  function animateCounter(el) {
    if (el.dataset.counted) return;
    const raw = el.textContent.trim();
    if (!/^\d+$/.test(raw)) return;
    const target = parseInt(raw, 10);
    if (target === 0) return;
    el.dataset.counted = '1';

    const duration = 680;
    const start = performance.now();
    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(target * eased);
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  }

  // ------------------------------------------------------------------------
  // 5. Top Progress Bar, Header Scroll Shadow & Back-to-Top
  // ------------------------------------------------------------------------
  function initScrollChrome() {
    const header = document.querySelector('header.site-header');
    const bar = document.getElementById('ppol-top-progress');
    const backTop = document.getElementById('ppol-back-top');

    function onScroll() {
      const y = window.scrollY || document.documentElement.scrollTop;
      if (header) header.classList.toggle('scrolled', y > 10);
      if (backTop) backTop.classList.toggle('visible', y > 320);

      if (bar && !bar.dataset.navigating) {
        const docH = document.documentElement.scrollHeight - window.innerHeight;
        const pct = docH > 40 ? Math.min(100, (y / docH) * 100) : 0;
        bar.style.width = `${pct}%`;
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    if (backTop) {
      backTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // Show subtle loading bar on internal link navigation
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href]');
      if (!a) return;
      const href = a.getAttribute('href');
      if (!href || href.startsWith('#') || href.startsWith('javascript:') || a.target === '_blank' || e.ctrlKey || e.metaKey) return;
      if (bar) {
        bar.dataset.navigating = '1';
        bar.style.width = '72%';
      }
    });
  }

  // ------------------------------------------------------------------------
  // 6. Spotlight Command Palette (Ctrl+K / Cmd+K)
  // ------------------------------------------------------------------------
  function initCommandPalette() {
    const backdrop = document.getElementById('ppol-cmd-backdrop');
    const input = document.getElementById('ppol-cmd-input');
    const list = document.getElementById('ppol-cmd-list');
    const trigger = document.getElementById('ppol-cmd-trigger');
    if (!backdrop || !input || !list) return;

    let selectedIdx = 0;

    function buildCommands() {
      const cmds = [];
      // Collect nav links from header
      document.querySelectorAll('header .nav-link-custom[href]').forEach((a) => {
        const href = a.getAttribute('href');
        if (!href || href === '#') return;
        const iconEl = a.querySelector('i');
        const icon = iconEl ? iconEl.className : 'bi bi-arrow-right-circle';
        const text = a.textContent.replace(/\s+/g, ' ').trim() || 'Notificaciones';
        cmds.push({
          group: 'Navegación rápida',
          label: text,
          icon,
          hint: a.target === '_blank' ? 'Nueva pestaña' : 'Ir a sección',
          action: () => {
            if (a.target === '_blank') window.open(href, '_blank');
            else window.location.href = href;
          },
        });
      });

      // Utility actions
      cmds.push({
        group: 'Apariencia y confort',
        label: document.documentElement.getAttribute('data-theme') === 'twilight'
          ? 'Cambiar a tema Seda Diurna (Claro)'
          : 'Cambiar a tema Crepúsculo Suave (Oscuro)',
        icon: 'bi bi-circle-half',
        hint: 'Tema visual',
        action: () => { toggleTheme(); closePalette(); },
      });

      cmds.push({
        group: 'Apariencia y confort',
        label: document.body.classList.contains('zen-mode')
          ? 'Desactivar Modo Zen (Activar animaciones)'
          : 'Activar Modo Zen (Sin animaciones)',
        icon: 'bi bi-wind',
        hint: 'Confort visual',
        action: () => { window.ppolToggleZen(); closePalette(); },
      });

      cmds.push({
        group: 'Acciones de página',
        label: 'Volver al inicio de la página',
        icon: 'bi bi-arrow-up-circle',
        hint: 'Scroll',
        action: () => { window.scrollTo({ top: 0, behavior: 'smooth' }); closePalette(); },
      });

      return cmds;
    }

    function render(filter = '') {
      const q = filter.toLowerCase().trim();
      const cmds = buildCommands().filter((c) => !q || c.label.toLowerCase().includes(q) || c.group.toLowerCase().includes(q));
      selectedIdx = 0;

      if (!cmds.length) {
        list.innerHTML = `<div style="padding:28px;text-align:center;color:var(--muted);font-size:13.5px;">No se encontraron comandos para "<strong>${escapeHtml(filter)}</strong>"</div>`;
        return;
      }

      const groups = {};
      cmds.forEach((c) => {
        if (!groups[c.group]) groups[c.group] = [];
        groups[c.group].push(c);
      });

      let html = '';
      let globalIdx = 0;
      const flat = [];
      Object.keys(groups).forEach((g) => {
        html += `<div class="ppol-cmd-group-title">${escapeHtml(g)}</div>`;
        groups[g].forEach((c) => {
          flat.push(c);
          html += `
            <button type="button" class="cmd-item ${globalIdx === 0 ? 'selected' : ''}" data-cmd-idx="${globalIdx}">
              <span class="cmd-item-left"><i class="${escapeHtml(c.icon)}"></i><span>${escapeHtml(c.label)}</span></span>
              <span class="cmd-item-hint">${escapeHtml(c.hint)}</span>
            </button>`;
          globalIdx++;
        });
      });

      list.innerHTML = html;
      list.querySelectorAll('.cmd-item').forEach((btn, idx) => {
        btn.addEventListener('click', () => flat[idx].action());
      });
      list._flat = flat;
    }

    function openPalette() {
      render('');
      input.value = '';
      backdrop.classList.add('open');
      setTimeout(() => input.focus(), 40);
    }

    function closePalette() {
      backdrop.classList.remove('open');
    }

    if (trigger) trigger.addEventListener('click', openPalette);
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) closePalette();
    });

    input.addEventListener('input', () => render(input.value));

    input.addEventListener('keydown', (e) => {
      const items = list.querySelectorAll('.cmd-item');
      if (!items.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        items[selectedIdx]?.classList.remove('selected');
        selectedIdx = (selectedIdx + 1) % items.length;
        items[selectedIdx]?.classList.add('selected');
        items[selectedIdx]?.scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        items[selectedIdx]?.classList.remove('selected');
        selectedIdx = (selectedIdx - 1 + items.length) % items.length;
        items[selectedIdx]?.classList.add('selected');
        items[selectedIdx]?.scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        e.preventDefault();
        list._flat?.[selectedIdx]?.action();
      }
    });

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (backdrop.classList.contains('open')) closePalette();
        else openPalette();
      } else if (e.key === 'Escape' && backdrop.classList.contains('open')) {
        closePalette();
      }
    });
  }

  // ------------------------------------------------------------------------
  // 7. Glassmorphic Confirmation Modal (Replaces native window.confirm)
  // ------------------------------------------------------------------------
  function initGlassConfirm() {
    const backdrop = document.getElementById('ppol-confirm-backdrop');
    const msgEl = document.getElementById('ppol-confirm-msg');
    const okBtn = document.getElementById('ppol-confirm-ok');
    const cancelBtn = document.getElementById('ppol-confirm-cancel');
    if (!backdrop || !msgEl || !okBtn || !cancelBtn) return;

    let pendingForm = null;

    function openConfirm(msg, form) {
      pendingForm = form;
      msgEl.textContent = msg || '¿Deseas continuar con esta acción?';
      backdrop.classList.add('open');
      okBtn.focus();
    }

    function closeConfirm() {
      backdrop.classList.remove('open');
      pendingForm = null;
    }

    cancelBtn.addEventListener('click', closeConfirm);
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) closeConfirm();
    });
    okBtn.addEventListener('click', () => {
      if (pendingForm) {
        const formToSubmit = pendingForm;
        closeConfirm();
        formToSubmit.dataset.confirmed = '1';
        formToSubmit.submit();
      }
    });

    // Upgrade inline onsubmit="return confirm('...')" forms seamlessly
    document.querySelectorAll('form[onsubmit*="confirm("]').forEach((form) => {
      const attr = form.getAttribute('onsubmit') || '';
      const match = attr.match(/confirm\((['"])(.*?)\1\)/);
      if (match && match[2]) {
        form.setAttribute('data-confirm', match[2]);
        form.removeAttribute('onsubmit');
      }
    });

    document.addEventListener('submit', (e) => {
      const form = e.target.closest('form[data-confirm]');
      if (!form || form.dataset.confirmed === '1') return;
      e.preventDefault();
      openConfirm(form.getAttribute('data-confirm'), form);
    });
  }

  // ------------------------------------------------------------------------
  // 8. Floating Glass Toasts (Auto-dismiss with hover pause)
  // ------------------------------------------------------------------------
  function initToasts() {
    document.querySelectorAll('.ppol-toast').forEach((toast) => {
      if (toast.classList.contains('is-error')) return;
      let timer = setTimeout(() => dismissToast(toast), 5800);
      toast.addEventListener('mouseenter', () => clearTimeout(timer));
      toast.addEventListener('mouseleave', () => {
        timer = setTimeout(() => dismissToast(toast), 2400);
      });
    });
  }

  function dismissToast(toast) {
    toast.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(24px) scale(0.96)';
    setTimeout(() => toast.remove(), 360);
  }

  window.ppolToast = function (text, type = 'good') {
    let stack = document.querySelector('.ppol-toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'ppol-toast-stack';
      document.body.appendChild(stack);
    }
    const toast = document.createElement('div');
    toast.className = `ppol-toast is-${type}`;
    const icon = type === 'error' ? 'bi-exclamation-triangle-fill' : type === 'warning' ? 'bi-info-circle-fill' : 'bi-check-circle-fill';
    toast.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;font-size:13.5px;font-weight:500;">
        <i class="bi ${icon} fs-5" style="color:var(--${type === 'error' ? 'bad' : type === 'warning' ? 'warn' : 'good'});"></i>
        <span>${escapeHtml(text)}</span>
      </div>
      <button type="button" aria-label="Cerrar aviso" style="background:transparent;border:none;color:inherit;font-size:18px;cursor:pointer;padding:0 4px;opacity:0.65;">&times;</button>
      <div class="ppol-toast-bar"></div>
    `;
    toast.querySelector('button').addEventListener('click', () => dismissToast(toast));
    stack.appendChild(toast);
    setTimeout(() => dismissToast(toast), 5600);
  };

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (m) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[m]));
  }

  // ------------------------------------------------------------------------
  // Boot Everything on DOMContentLoaded
  // ------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem(ZEN_KEY) === '1') {
      document.body.classList.add('zen-mode');
    }
    applyTheme(localStorage.getItem(THEME_KEY) || 'daylight');

    const themeBtn = document.getElementById('ppol-theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    initAmbientCanvas();
    initCardSpotlight();
    initScrollRevealAndCounters();
    initScrollChrome();
    initCommandPalette();
    initGlassConfirm();
    initToasts();
  });
})();
