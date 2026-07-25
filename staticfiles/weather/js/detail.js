/* ============================================================
   DETAIL.JS — City detail page interactions
   ============================================================ */

// ---- Temperature history chart ----
(function () {
    const canvas = document.getElementById('tempChart');
    if (!canvas || typeof chartLabels === 'undefined' || !chartLabels.length) return;

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Temperature (°C)',
                data: chartTemps,
                borderColor: '#4fc3f7',
                backgroundColor: 'rgba(79, 195, 247, 0.08)',
                borderWidth: 2,
                pointBackgroundColor: '#4fc3f7',
                pointBorderColor: '#0a0f1e',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(13,26,53,0.95)',
                    borderColor: 'rgba(79,195,247,0.3)',
                    borderWidth: 1,
                    titleColor: '#7d99bd',
                    bodyColor: '#e8edf5',
                    padding: 10,
                    callbacks: {
                        label: ctx => ` ${ctx.parsed.y}°C`,
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(79,195,247,0.06)' },
                    ticks: { color: '#7d99bd', font: { size: 11 } },
                },
                y: {
                    grid: { color: 'rgba(79,195,247,0.06)' },
                    ticks: {
                        color: '#7d99bd',
                        font: { size: 11 },
                        callback: v => `${v}°`,
                    },
                }
            }
        }
    });
})();

// ---- °C / °F unit toggle ----
(function () {
    if (typeof tempVal === 'undefined' || tempVal === null) return;

    const tempEl   = document.querySelector('.cw-temp');
    const feelsEl  = document.querySelector('.cw-feels');
    const btnC     = document.querySelector('.unit-btn[data-unit="c"]');
    const btnF     = document.querySelector('.unit-btn[data-unit="f"]');

    if (!tempEl || !btnC || !btnF) return;

    const origTemp   = tempVal;
    const origFeels  = feelsVal;

    function toF(c) { return Math.round(c * 9 / 5 + 32); }

    btnF.addEventListener('click', () => {
        tempEl.textContent = toF(origTemp) + '°';
        if (feelsEl) feelsEl.textContent = `Feels like ${toF(origFeels)}°`;
        btnF.classList.add('unit-btn--active');
        btnF.setAttribute('aria-pressed', 'true');
        btnC.classList.remove('unit-btn--active');
        btnC.setAttribute('aria-pressed', 'false');
    });

    btnC.addEventListener('click', () => {
        tempEl.textContent = Math.round(origTemp) + '°';
        if (feelsEl) feelsEl.textContent = `Feels like ${Math.round(origFeels)}°`;
        btnC.classList.add('unit-btn--active');
        btnC.setAttribute('aria-pressed', 'true');
        btnF.classList.remove('unit-btn--active');
        btnF.setAttribute('aria-pressed', 'false');
    });
})();

// ---- Favourite button AJAX toggle ----
(function () {
    const favBtn = document.getElementById('favBtn');
    if (!favBtn) return;

    favBtn.closest('form')?.addEventListener('submit', async (e) => {
        const form = e.target;
        const action = form.action;

        // Check if fetch is available (progressive enhancement)
        if (!window.fetch) return; // let normal form submit happen

        e.preventDefault();
        const fd = new FormData(form);

        try {
            const res = await fetch(action, {
                method: 'POST',
                body: fd,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });
            if (!res.ok) throw new Error();
            const data = await res.json();
            const isFav = data.is_favorite;
            favBtn.textContent = isFav ? '★ Favourited' : '☆ Favourite';
            favBtn.classList.toggle('action-btn--active', isFav);
            favBtn.setAttribute('aria-label', isFav ? 'Remove from favourites' : 'Add to favourites');
        } catch (_) {
            // fallback: let form submit normally
            form.submit();
        }
    });
})();