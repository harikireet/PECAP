/**
 * PECAP — Forensic Console
 * Shared frontend runtime: theme, command bar, meta ticker, JSON viewer, motion.
 */

(function () {
    'use strict';

    /* ----------------------------- Theme ----------------------------- */
    const THEME_KEY = 'pecap-theme';
    const themeToggle = document.getElementById('theme-toggle');

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem(THEME_KEY, theme); } catch (e) { }
        document.dispatchEvent(new CustomEvent('pecap:theme', { detail: theme }));
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    /* --------------------------- Route sweep ------------------------- */
    const sweep = document.getElementById('route-sweep');
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a[href]');
        if (!link) return;
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || link.target === '_blank') return;
        if (href.startsWith('http') && !href.includes(window.location.host)) return;
        if (sweep) {
            sweep.classList.remove('run');
            void sweep.offsetWidth;
            sweep.classList.add('run');
        }
    });

    /* --------------------------- Meta ticker ------------------------- */
    function updateTicker() {
        const ticker = document.getElementById('meta-ticker');
        if (!ticker) return;

        const file = localStorage.getItem('pecap-file') || '—';
        const eventsRaw = localStorage.getItem('events');
        const time = localStorage.getItem('pecap-captured') || '—';
        let events = [];
        try { events = eventsRaw ? JSON.parse(eventsRaw) : []; } catch (e) { events = []; }

        const isIdle = !eventsRaw || events.length === 0;
        const status = isIdle ? 'Idle' : 'Active';

        ticker.classList.toggle('ticker--idle', isIdle);
        const setText = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };
        setText('ticker-status', status);
        setText('ticker-file', file);
        setText('ticker-events', events.length.toLocaleString());
        setText('ticker-time', time);
    }
    updateTicker();
    window.addEventListener('storage', updateTicker);
    document.addEventListener('pecap:session', updateTicker);

    /* --------------------------- Command bar ------------------------- */
    const cmdk = document.getElementById('cmdk');
    const cmdkInput = document.getElementById('cmdk-input');
    const cmdkList = document.getElementById('cmdk-list');
    const cmdkTrigger = document.getElementById('cmdk-trigger');

    const NAV_ITEMS = [
        { type: 'page', label: 'Home', href: '/', code: '01' },
        { type: 'page', label: 'Analytics', href: '/analytics', code: '02' },
        { type: 'page', label: 'Threats', href: '/threats', code: '03' },
        { type: 'page', label: 'Search', href: '/search', code: '04' },
        { type: 'page', label: 'Map', href: '/geolocation', code: '05' },
        { type: 'page', label: 'Timeline', href: '/timeline', code: '06' },
        { type: 'page', label: 'Report', href: '/report', code: '07' },
        { type: 'action', label: 'Clear session', action: 'clear' },
        { type: 'action', label: 'Toggle theme', action: 'theme' },
    ];

    function openCmdk() {
        if (!cmdk) return;
        cmdk.classList.add('is-open');
        cmdkInput.value = '';
        renderCmdkList('');
        setTimeout(() => cmdkInput.focus(), 20);
    }

    function closeCmdk() {
        if (!cmdk) return;
        cmdk.classList.remove('is-open');
    }

    let cmdkFocusIndex = 0;

    function renderCmdkList(query) {
        if (!cmdkList) return;
        const q = query.trim().toLowerCase();
        const sections = [];

        const navResults = NAV_ITEMS.filter(i => i.type === 'page' && (!q || i.label.toLowerCase().includes(q) || (i.code || '').includes(q)));
        const actionResults = NAV_ITEMS.filter(i => i.type === 'action' && (!q || i.label.toLowerCase().includes(q)));

        let eventResults = [];
        if (q) {
            try {
                const events = JSON.parse(localStorage.getItem('events') || '[]');
                eventResults = events.filter(e => {
                    const blob = `${e.type || ''} ${e.description || ''} ${e.source_ip || ''} ${e.dest_ip || ''}`.toLowerCase();
                    return blob.includes(q);
                }).slice(0, 8);
            } catch (e) { }
        }

        let html = '';
        if (navResults.length) {
            html += `<div class="cmdk__group-label">Pages</div>`;
            html += navResults.map(i => `
                <div class="cmdk__item" data-href="${i.href}">
                    <span><span class="text-subtle">${i.code}</span> &nbsp; ${i.label}</span>
                    <span class="cmdk__item-arrow">↵</span>
                </div>`).join('');
        }
        if (actionResults.length) {
            html += `<div class="cmdk__group-label">Actions</div>`;
            html += actionResults.map(i => `
                <div class="cmdk__item" data-action="${i.action}">
                    <span>${i.label}</span>
                    <span class="cmdk__item-arrow">↵</span>
                </div>`).join('');
        }
        if (eventResults.length) {
            html += `<div class="cmdk__group-label">Events (${eventResults.length})</div>`;
            html += eventResults.map(e => `
                <div class="cmdk__item" data-href="/search?q=${encodeURIComponent(q)}">
                    <span><span class="text-subtle">#${e.id}</span> &nbsp; ${escapeHtml(truncate(e.description || e.type, 60))}</span>
                    <span class="cmdk__item-arrow">↵</span>
                </div>`).join('');
        }
        if (!html) {
            html = `<div class="cmdk__group-label">No matches</div>`;
        }

        cmdkList.innerHTML = html;
        cmdkFocusIndex = 0;
        updateCmdkFocus();

        cmdkList.querySelectorAll('.cmdk__item').forEach((el, i) => {
            el.addEventListener('mouseenter', () => { cmdkFocusIndex = i; updateCmdkFocus(); });
            el.addEventListener('click', () => activateCmdkItem(el));
        });
    }

    function updateCmdkFocus() {
        if (!cmdkList) return;
        const items = cmdkList.querySelectorAll('.cmdk__item');
        items.forEach((el, i) => el.classList.toggle('is-focused', i === cmdkFocusIndex));
        const focused = items[cmdkFocusIndex];
        if (focused) focused.scrollIntoView({ block: 'nearest' });
    }

    function activateCmdkItem(el) {
        if (!el) return;
        const href = el.getAttribute('data-href');
        const action = el.getAttribute('data-action');
        if (href) {
            closeCmdk();
            window.location.href = href;
            return;
        }
        if (action === 'clear') {
            localStorage.removeItem('events');
            localStorage.removeItem('links');
            localStorage.removeItem('pecap-file');
            localStorage.removeItem('pecap-captured');
            fetch('/api/clear', { method: 'POST' }).catch(() => { });
            updateTicker();
            closeCmdk();
            window.location.href = '/';
        } else if (action === 'theme') {
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            setTheme(current === 'dark' ? 'light' : 'dark');
            closeCmdk();
        }
    }

    if (cmdkTrigger) cmdkTrigger.addEventListener('click', openCmdk);
    if (cmdkInput) cmdkInput.addEventListener('input', () => renderCmdkList(cmdkInput.value));
    if (cmdk) {
        cmdk.addEventListener('click', (e) => {
            if (e.target === cmdk) closeCmdk();
        });
    }

    document.addEventListener('keydown', (e) => {
        const isMod = e.ctrlKey || e.metaKey;
        if (isMod && (e.key.toLowerCase() === 'k' || e.key.toLowerCase() === 'f')) {
            e.preventDefault();
            openCmdk();
            return;
        }
        if (!cmdk || !cmdk.classList.contains('is-open')) return;

        if (e.key === 'Escape') {
            e.preventDefault();
            closeCmdk();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            const items = cmdkList.querySelectorAll('.cmdk__item');
            cmdkFocusIndex = Math.min(items.length - 1, cmdkFocusIndex + 1);
            updateCmdkFocus();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            const items = cmdkList.querySelectorAll('.cmdk__item');
            cmdkFocusIndex = Math.max(0, cmdkFocusIndex - 1);
            updateCmdkFocus();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const items = cmdkList.querySelectorAll('.cmdk__item');
            activateCmdkItem(items[cmdkFocusIndex]);
        }
    });

    /* --------------------------- Utilities --------------------------- */
    window.truncate = function (str, len) {
        if (!str) return '';
        if (str.length <= len) return str;
        return str.substr(0, len) + '…';
    };

    window.escapeHtml = function (str) {
        if (str == null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    };

    /* ------------------------ Number ticker -------------------------- */
    window.tickerCount = function (el, target, durationMs = 500) {
        if (!el) return;
        const start = performance.now();
        const end = Number(target) || 0;
        function step(now) {
            const t = Math.min(1, (now - start) / durationMs);
            const eased = 1 - Math.pow(1 - t, 3);
            el.textContent = Math.round(end * eased).toLocaleString();
            if (t < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    };

    /* ------------------------ JSON viewer ---------------------------- */
    window.showDetails = function (event, targetId = 'details-content') {
        const target = document.getElementById(targetId);
        if (!target) return;
        target.innerHTML = renderJsonView(event);
    };

    function classifyValue(key, value) {
        const k = String(key).toLowerCase();
        if (typeof value === 'number') {
            if (['port', 'sport', 'dport'].includes(k)) return 'port';
            return 'num';
        }
        if (['source_ip', 'src_ip', 'dest_ip', 'dst_ip', 'ip', 'address'].includes(k)) return 'ip';
        if (['query', 'sni', 'domain', 'host', 'url'].includes(k)) return 'domain';
        if (['type', 'method'].includes(k)) return 'type';
        return '';
    }

    function row(key, value) {
        if (value === null || value === undefined) return '';
        const cls = classifyValue(key, value);
        return `<div class="json-view__row">
            <span class="json-view__key">${escapeHtml(key)}</span>
            <span class="json-view__val ${cls ? 'json-view__val--' + cls : ''}">${escapeHtml(value)}</span>
        </div>`;
    }

    function renderJsonView(event) {
        if (!event) return '';
        const data = event;
        let html = '<div class="json-view">';

        html += row('id', '#' + data.id);
        html += row('type', data.type);
        if (data.timestamp) {
            html += row('timestamp', new Date(data.timestamp * 1000).toLocaleString());
        }
        if (data.source_ip || data.src_ip) {
            html += row('source_ip', data.source_ip || data.src_ip);
        }
        if (data.dest_ip || data.dst_ip) {
            html += row('dest_ip', data.dest_ip || data.dst_ip);
        }
        if (data.description) {
            html += row('description', data.description);
        }

        if (data.details && Object.keys(data.details).length) {
            html += `<div class="json-view__group">
                <div class="json-view__group-label">Protocol Data</div>`;
            for (const [k, v] of Object.entries(data.details)) {
                html += row(k, v);
            }
            html += `</div>`;
        }

        html += '</div>';
        return html;
    }

    /* ------------------------ Empty-state helper --------------------- */
    window.renderEmpty = function (title, hint, ascii) {
        return `<div class="empty">
            ${ascii ? `<pre class="empty__ascii">${escapeHtml(ascii)}</pre>` : ''}
            <h3 class="empty__title">${escapeHtml(title)}</h3>
            <p class="empty__hint">${escapeHtml(hint || '')}</p>
        </div>`;
    };
})();
