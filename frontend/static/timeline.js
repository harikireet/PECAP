/**
 * PECAP — Forensic Reel
 * vis-timeline rendering with re-themed items.
 */

(function () {
    'use strict';

    let events = [];
    let timeline;

    function loadTimelineData() {
        try {
            const stored = localStorage.getItem('events');
            if (stored) events = JSON.parse(stored);
        } catch (err) {
            console.warn('Failed to read timeline data:', err);
        }
    }

    function renderTimeline() {
        const empty = document.getElementById('timeline-empty');
        const dashboard = document.getElementById('timeline-dashboard');

        if (!events || events.length === 0) {
            if (empty) empty.classList.remove('hidden');
            if (dashboard) dashboard.classList.add('hidden');
            return;
        }
        if (empty) empty.classList.add('hidden');
        if (dashboard) dashboard.classList.remove('hidden');

        const container = document.getElementById('timeline');
        if (!container) return;

        const items = new vis.DataSet(
            events.map(e => ({
                id: e.id,
                content: `[${(e.type || '').toUpperCase()}] ${truncate(e.description || '', 60)}`,
                start: new Date(e.timestamp * 1000),
                group: e.type
            }))
        );

        const groups = new vis.DataSet(
            [...new Set(events.map(e => e.type))].map(type => ({
                id: type,
                content: `<span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em;">${type}</span>`
            }))
        );

        const options = {
            stack: true,
            showCurrentTime: true,
            height: '100%',
            groupOrder: 'content',
            editable: false,
            selectable: true,
            multiselect: false,
            tooltip: { followMouse: true },
            verticalScroll: true,
            cluster: {
                maxItems: 5,
                clusterForm: 'cluster',
                titleTemplate: 'Cluster of {count} events'
            },
            margin: { item: 8, axis: 6 },
            zoomMin: 1000 * 5,
            zoomMax: 1000 * 60 * 60 * 24,
            zoomFriction: 20,
            orientation: { axis: 'bottom' }
        };

        timeline = new vis.Timeline(container, items, groups, options);

        timeline.on('select', (props) => {
            if (props.items.length > 0) {
                const id = props.items[0];
                const ev = events.find(e => e.id === id);
                if (ev) {
                    showDetails(ev, 'details-content');
                    renderSummary(ev);
                }
            }
        });
    }

    function renderSummary(ev) {
        const sum = document.getElementById('selected-summary');
        if (!sum) return;
        const ts = ev.timestamp ? new Date(ev.timestamp * 1000).toLocaleString() : '—';
        sum.innerHTML = `
            <div class="stack-3">
                <div>
                    <span class="label">Type</span>
                    <div class="text-mono text-accent" style="font-size: var(--fs-20); margin-top: var(--sp-1);">${escapeHtml(ev.type || '')}</div>
                </div>
                <div>
                    <span class="label">Captured</span>
                    <div class="text-mono" style="font-size: var(--fs-14); margin-top: var(--sp-1);">${escapeHtml(ts)}</div>
                </div>
                <div>
                    <span class="label">Source &rarr; Destination</span>
                    <div class="text-mono" style="font-size: var(--fs-14); margin-top: var(--sp-1);">
                        ${escapeHtml(ev.source_ip || ev.src_ip || 'internal')}
                        <span class="text-subtle"> &rarr; </span>
                        ${escapeHtml(ev.dest_ip || ev.dst_ip || 'internal')}
                    </div>
                </div>
                <div>
                    <span class="label">Description</span>
                    <p style="margin-top: var(--sp-1); line-height: var(--lh-base);">${escapeHtml(ev.description || '')}</p>
                </div>
            </div>
        `;
    }

    document.addEventListener('DOMContentLoaded', () => {
        loadTimelineData();
        renderTimeline();
    });
})();
