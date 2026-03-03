/* ============================================================
   MAIN.JS — Global interactions
   ============================================================ */

// ---- Mobile nav toggle ----
(function () {
    const btn = document.getElementById('menuToggle');
    const nav = document.getElementById('mobileNav');
    if (!btn || !nav) return;

    btn.addEventListener('click', () => {
        const isOpen = nav.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', String(isOpen));
        nav.setAttribute('aria-hidden', String(!isOpen));

        // Animate hamburger to X
        const spans = btn.querySelectorAll('span');
        if (isOpen) {
            spans[0].style.transform = 'translateY(7px) rotate(45deg)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
        } else {
            spans[0].style.transform = '';
            spans[1].style.opacity = '';
            spans[2].style.transform = '';
        }
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!btn.contains(e.target) && !nav.contains(e.target)) {
            nav.classList.remove('is-open');
            nav.setAttribute('aria-hidden', 'true');
            btn.setAttribute('aria-expanded', 'false');
        }
    });
})();

// ---- Particle field ----
(function () {
    const field = document.getElementById('particles');
    if (!field) return;

    const COUNT = 18;
    for (let i = 0; i < COUNT; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 3 + 1;
        p.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${Math.random() * 100}%;
            --dur-p: ${Math.random() * 15 + 12}s;
            --dx: ${(Math.random() - 0.5) * 80}px;
            animation-delay: ${Math.random() * -20}s;
        `;
        field.appendChild(p);
    }
})();

// ---- Auto-dismiss messages after 5 s ----
(function () {
    const msgs = document.querySelectorAll('.message');
    msgs.forEach((m, i) => {
        setTimeout(() => {
            m.style.transition = 'opacity 0.4s, transform 0.4s';
            m.style.opacity = '0';
            m.style.transform = 'translateX(20px)';
            setTimeout(() => m.remove(), 400);
        }, 5000 + i * 400);
    });
})();

// ---- Search input focus effect ----
(function () {
    const input = document.querySelector('.search-input');
    if (!input) return;
    input.addEventListener('focus', () => {
        input.closest('.search-wrap')?.classList.add('search-wrap--focused');
    });
    input.addEventListener('blur', () => {
        input.closest('.search-wrap')?.classList.remove('search-wrap--focused');
    });
})();

// ---- Stagger card animations ----
(function () {
    const cards = document.querySelectorAll('.weather-card, .stat-card, .feature-card, .daily-card');
    cards.forEach((card, i) => {
        card.style.animationDelay = `${i * 0.06}s`;
        card.classList.add('fade-in');
    });
})();