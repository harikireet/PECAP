/**
 * PECAP — Capture Console
 * Upload + Attack Graph rendering.
 */

(function () {
    'use strict';

    let events = [], links = [];
    let graphNetwork;

    const dropEl = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileNameEl = document.getElementById('file-name');
    const dashboard = document.getElementById('dashboard');
    const captureSection = document.getElementById('capture-section');
    const loadingEl = document.getElementById('loading');
    const analyzeBtn = document.getElementById('analyze-btn');

    // Drag-and-drop
    if (dropEl) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(name => {
            dropEl.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        ['dragenter', 'dragover'].forEach(name => {
            dropEl.addEventListener(name, () => dropEl.classList.add('is-active'));
        });
        ['dragleave', 'drop'].forEach(name => {
            dropEl.addEventListener(name, () => dropEl.classList.remove('is-active'));
        });
        dropEl.addEventListener('drop', (e) => {
            const files = e.dataTransfer && e.dataTransfer.files;
            if (files && files.length) {
                fileInput.files = files;
                updateFileName(files[0].name);
            }
        });

        dropEl.addEventListener('submit', onSubmit);
    }

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) updateFileName(fileInput.files[0].name);
        });
    }

    function updateFileName(name) {
        if (!fileNameEl) return;
        fileNameEl.textContent = '> ' + name;
    }

    async function onSubmit(e) {
        e.preventDefault();
        const file = fileInput && fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        if (loadingEl) loadingEl.classList.remove('hidden');
        if (analyzeBtn) analyzeBtn.disabled = true;
        if (dashboard) dashboard.classList.add('hidden');

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const data = await response.json();
            if (data.error) {
                let msg = 'Error: ' + data.error;
                if (data.details) msg += '\n\n' + data.details;
                alert(msg);
                return;
            }
            events = data.events || [];
            links = data.links || [];
            try {
                localStorage.setItem('events', JSON.stringify(events));
                localStorage.setItem('links', JSON.stringify(links));
                localStorage.setItem('pecap-file', file.name);
                localStorage.setItem('pecap-captured', new Date().toLocaleString());
            } catch (err) {
                console.warn('Failed to cache timeline data:', err);
            }
            document.dispatchEvent(new CustomEvent('pecap:session'));
            showDashboard();
        } catch (err) {
            alert('Upload failed: ' + err);
        } finally {
            if (loadingEl) loadingEl.classList.add('hidden');
            if (analyzeBtn) analyzeBtn.disabled = false;
        }
    }

    function showDashboard() {
        if (captureSection) captureSection.classList.add('hidden');
        if (dashboard) dashboard.classList.remove('hidden');
        renderGraph();
    }

    function getCss(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }

    function renderGraph() {
        const container = document.getElementById('graph');
        if (!container) return;

        const phosphor = getCss('--phosphor');
        const amber = getCss('--amber');
        const ice = getCss('--ice');
        const signal = getCss('--signal');
        const fg = getCss('--fg');
        const fgSubtle = getCss('--paper-400');
        const surface = getCss('--surface');
        const hairline = getCss('--hairline');

        const groupColors = {
            'TCP Connection': ice,
            'DNS Query': phosphor,
            'HTTP Request': signal,
            'TLS SNI': '#9D7FFF',
            'ICMP': amber
        };

        const nodes = events.map(e => {
            const color = groupColors[e.type] || fg;
            return {
                id: e.id,
                label: `${e.type}\n${truncate(e.description, 28)}`,
                title: e.description,
                group: e.type,
                color: { background: surface, border: color, highlight: { background: color, border: color } },
                font: { color: fg, face: 'JetBrains Mono', size: 12 },
                shape: 'box',
                margin: 8,
                shapeProperties: { borderRadius: 0 }
            };
        });

        const edges = links.map(l => ({
            from: l.source,
            to: l.target,
            label: l.label || '',
            arrows: { to: { enabled: true, scaleFactor: 0.6, type: 'arrow' } },
            font: { align: 'middle', color: fgSubtle, face: 'JetBrains Mono', size: 10, background: 'rgba(0,0,0,0)' },
            color: { color: hairline, highlight: phosphor },
            smooth: { type: 'continuous' },
            width: 1
        }));

        const data = { nodes, edges };
        const options = {
            layout: { improvedLayout: true, hierarchical: false },
            nodes: {
                borderWidth: 1,
                widthConstraint: { maximum: 220 }
            },
            edges: { width: 1 },
            interaction: {
                hover: true,
                navigationButtons: false,
                multiselect: false,
                dragNodes: true,
                hideEdgesOnDrag: false,
                tooltipDelay: 200
            },
            physics: {
                enabled: true,
                solver: 'barnesHut',
                barnesHut: {
                    gravitationalConstant: -3500,
                    centralGravity: 0.25,
                    springLength: 160,
                    springConstant: 0.04,
                    damping: 0.12,
                    avoidOverlap: 0.6
                },
                stabilization: { enabled: true, iterations: 200, updateInterval: 25 }
            }
        };

        graphNetwork = new vis.Network(container, data, options);

        graphNetwork.once('stabilizationIterationsDone', () => {
            graphNetwork.fit({
                animation: { duration: 800, easingFunction: 'easeInOutQuad' },
                padding: 60
            });
        });

        graphNetwork.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const event = events.find(e => e.id === nodeId);
                if (event) openOverlay(event);
            }
        });
    }

    /* Detail overlay */
    const overlay = document.getElementById('detail-overlay');
    const overlayClose = document.getElementById('detail-close');
    function openOverlay(event) {
        if (!overlay) return;
        showDetails(event, 'details-content');
        overlay.classList.add('is-open');
    }
    if (overlayClose) overlayClose.addEventListener('click', () => overlay.classList.remove('is-open'));
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay && overlay.classList.contains('is-open')) {
            overlay.classList.remove('is-open');
        }
    });

    /* Bootstrap: handle ?new=true and restore prior session */
    function init() {
        const params = new URLSearchParams(window.location.search);
        if (params.has('new')) {
            localStorage.removeItem('events');
            localStorage.removeItem('links');
            localStorage.removeItem('pecap-file');
            localStorage.removeItem('pecap-captured');
            fetch('/api/clear', { method: 'POST' }).catch(() => { });
            window.history.replaceState({}, document.title, '/');
            document.dispatchEvent(new CustomEvent('pecap:session'));
            return;
        }
        const savedEvents = localStorage.getItem('events');
        const savedLinks = localStorage.getItem('links');
        if (savedEvents && savedLinks) {
            try {
                events = JSON.parse(savedEvents);
                links = JSON.parse(savedLinks);
                showDashboard();
            } catch (err) {
                console.warn('Failed to restore session', err);
            }
        }
    }

    init();
})();
