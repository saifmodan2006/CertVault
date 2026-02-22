// ─── Theme ────────────────────────────────────────────────────
const THEME_KEY = 'certvault-theme';
const html = document.documentElement;

function applyTheme(t) {
  html.setAttribute('data-theme', t);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.className = t === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
}

(function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(saved);
})();

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem(THEME_KEY, next);
    });
  }

  // Navbar scroll effect
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 10);
    });
  }

  // Sidebar toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Auto-dismiss flash toasts
  document.querySelectorAll('[data-auto-dismiss]').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(100%)';
      el.style.transition = 'all 0.4s ease';
      setTimeout(() => el.remove(), 400);
    }, 4500);
  });

  // Animate elements on scroll
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-fade-up').forEach(el => {
    el.style.animationPlayState = 'paused';
    observer.observe(el);
  });

  // Bootstrap tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // Confirm delete
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

  // Tag input enhancement
  const tagsInput = document.getElementById('tagsInput');
  if (tagsInput) {
    tagsInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (!tagsInput.value.endsWith(',')) tagsInput.value += ',';
        updateTagPills(tagsInput.value);
      }
    });
  }

  // Smooth anchor scrolls
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
  });

  // Table row click
  document.querySelectorAll('[data-row-link]').forEach(tr => {
    tr.style.cursor = 'pointer';
    tr.addEventListener('click', () => window.location.href = tr.dataset.rowLink);
  });
});

// ─── Helpers ─────────────────────────────────────────────────

function showToast(msg, type = 'info') {
  const container = document.getElementById('flashContainer') ||
    (() => { const d = document.createElement('div'); d.id='flashContainer'; d.className='flash-container'; document.body.appendChild(d); return d; })();
  const toast = document.createElement('div');
  toast.className = `flash-toast flash-${type} show`;
  const icons = { success: 'check-circle', danger: 'x-circle', warning: 'exclamation-triangle', info: 'info-circle' };
  toast.innerHTML = `<div class="d-flex align-items-center gap-2"><i class="bi bi-${icons[type]||icons.info}"></i><span>${msg}</span><button class="btn-close btn-close-sm ms-auto" onclick="this.closest('.flash-toast').remove()"></button></div>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

function togglePassword(id) {
  const input = document.getElementById(id);
  const icon = document.getElementById(`${id}-icon`);
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    if (icon) icon.className = 'bi bi-eye-slash';
  } else {
    input.type = 'password';
    if (icon) icon.className = 'bi bi-eye';
  }
}

function updateTagPills(value) {
  const pills = document.getElementById('tagPills');
  if (!pills) return;
  const tags = value.split(',').map(t => t.trim()).filter(Boolean);
  pills.innerHTML = tags.map(t => `<span class="badge badge-tag">${t}</span>`).join('');
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard! 📋', 'success'));
}

// ─── Ripple Effect on Buttons ─────────────────────────────────
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn-primary-gradient');
  if (!btn) return;
  const circle = document.createElement('span');
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  circle.style.cssText = `
    position:absolute; width:${size}px; height:${size}px;
    border-radius:50%; background:rgba(255,255,255,0.25);
    left:${e.clientX-rect.left-size/2}px; top:${e.clientY-rect.top-size/2}px;
    transform:scale(0); animation:ripple 0.6s linear; pointer-events:none;
  `;
  if (!document.getElementById('rippleStyle')) {
    const s = document.createElement('style');
    s.id = 'rippleStyle';
    s.textContent = '@keyframes ripple{to{transform:scale(2.5);opacity:0}}';
    document.head.appendChild(s);
  }
  btn.appendChild(circle);
  setTimeout(() => circle.remove(), 600);
});

// ─── Number Counter Animation ─────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.textContent) || 0;
  if (!target) return;
  let start = 0;
  const duration = 800;
  const step = Math.ceil(target / (duration / 16));
  const timer = setInterval(() => {
    start = Math.min(start + step, target);
    el.textContent = start;
    if (start >= target) clearInterval(timer);
  }, 16);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.stat-value').forEach(el => {
    const text = el.textContent.trim();
    if (/^\d+$/.test(text)) {
      el.textContent = '0';
      setTimeout(() => animateCounter(el), 300);
    }
  });
});

// ─── Keyboard Shortcuts ───────────────────────────────────────
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey) {
    if (e.key === 'k') { e.preventDefault(); document.querySelector('[name="q"]')?.focus(); }
    if (e.key === 'u') { e.preventDefault(); window.location.href = '/upload'; }
  }
  if (e.key === 'Escape') { document.querySelector('.sidebar')?.classList.remove('open'); }
});
