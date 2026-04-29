// Note: Shortcut handled in shared.js

let events = [], links = [];
let graphNetwork, timeline;

// Drag and drop UI handling
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
});

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
        fileInput.files = files;
        updateFileName(files[0].name);
    }
}

fileInput.addEventListener('change', function () {
    if (this.files.length) {
        updateFileName(this.files[0].name);
    }
});

function updateFileName(name) {
    fileNameDisplay.textContent = 'Selected: ' + name;
    fileNameDisplay.style.color = '#4caf50';
    fileNameDisplay.style.fontWeight = 'bold';
}

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    // Re-select fileInput here just to be safe, though declared above.
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const loading = document.getElementById('loading');
    const dashboard = document.getElementById('dashboard');
    loading.style.display = 'block';
    dashboard.style.display = 'none';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.error) {
            let msg = 'Error: ' + data.error;
            if (data.details) msg += '\n\n' + data.details;
            alert(msg);
            return;
        }
        events = data.events;
        links = data.links;
        try {
            localStorage.setItem('events', JSON.stringify(events));
            localStorage.setItem('links', JSON.stringify(links));
        } catch (err) {
            console.warn('Failed to cache timeline data:', err);
        }
        renderDashboard();
        dashboard.style.display = 'block';
    } catch (err) {
        alert('Upload failed: ' + err);
    } finally {
        loading.style.display = 'none';
    }
});

function renderDashboard() {
    const nodes = events.map(e => ({
        id: e.id,
        label: `${e.type}\n${truncate(e.description, 30)}`,
        title: e.description,
        group: e.type,
        details: e
    }));

    const edges = links.map(l => ({
        from: l.source,
        to: l.target,
        label: l.label,
        arrows: 'to',
        font: { align: 'middle', color: '#b0bec5' },
        color: { color: '#7f8c8d', highlight: '#e67e22' }
    }));

    const container = document.getElementById('graph');
    const graphData = { nodes, edges };
    const options = {
        layout: {
            improvedLayout: true,
            hierarchical: false // Ensure it stays free-form for floating
        },
        nodes: {
            shape: 'dot', // Dot looks more "network-y" and premium than boxes
            size: 25,
            font: {
                color: '#ccd6f6',
                size: 14,
                face: 'Outfit',
                vadjust: 5
            },
            borderWidth: 2,
            shadow: {
                enabled: true,
                color: 'rgba(100, 255, 218, 0.2)',
                size: 15,
                x: 0,
                y: 0
            }
        },
        edges: {
            width: 2,
            color: { color: 'rgba(136, 146, 176, 0.3)', highlight: '#64ffda' },
            smooth: { type: 'continuous' },
            arrows: { to: { enabled: true, scaleFactor: 0.5 } }
        },
        groups: {
            'TCP Connection': { color: { background: 'rgba(100, 181, 246, 0.8)', border: '#64b5f6' } },
            'DNS Query': { color: { background: 'rgba(80, 250, 123, 0.8)', border: '#50fa7b' } },
            'HTTP Request': { color: { background: 'rgba(255, 93, 143, 0.8)', border: '#ff5d8f' } },
            'TLS SNI': { color: { background: 'rgba(189, 147, 249, 0.8)', border: '#bd93f9' } },
            'ICMP': { color: { background: 'rgba(255, 184, 108, 0.8)', border: '#ffb86c' } }
        },
        interaction: {
            hover: true,
            navigationButtons: true,
            multiselect: true,
            dragNodes: true,
            hideEdgesOnDrag: false, // Keep edges visible during drag for "pulling" feel
            tooltipDelay: 200
        },
        physics: {
            enabled: true,
            solver: 'barnesHut',
            barnesHut: {
                gravitationalConstant: -3000, // Stronger repulsion for floating
                centralGravity: 0.3,
                springLength: 150,
                springConstant: 0.05, // Elasticity
                damping: 0.09,
                avoidOverlap: 0.5
            },
            stabilization: {
                enabled: true,
                iterations: 150,
                updateInterval: 25
            }
        }
    };
    graphNetwork = new vis.Network(container, graphData, options);

    graphNetwork.once('stabilizationIterationsDone', function () {
        // We NO LONGER disable physics here. We keep it enabled for floating.
        graphNetwork.fit({
            animation: { duration: 1000, easingFunction: 'easeInOutQuad' },
            padding: 50
        });
    });

    // Add visual feedback during drag
    graphNetwork.on('dragStart', function () {
        // Make springs stiffer during drag for a heavier, more tactile feel
        graphNetwork.setOptions({ physics: { barnesHut: { springConstant: 0.2 } } });
    });

    graphNetwork.on('dragEnd', function () {
        // Return to soft floating springs
        graphNetwork.setOptions({ physics: { barnesHut: { springConstant: 0.05 } } });
    });

    graphNetwork.on('click', function (params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const event = events.find(e => e.id === nodeId);
            if (event) showDetails(event);
        }
    });
}

// Note: truncate and syntaxHighlight moved to shared.js
function init() {
    // Check if user wants a fresh start (via brand link click)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('new')) {
        localStorage.removeItem('events');
        localStorage.removeItem('links');
        // Clear server side data too
        fetch('/api/clear', { method: 'POST' }).catch(e => console.error("Server reset failed", e));
        // Clean URL without refresh
        window.history.replaceState({}, document.title, "/");
    }

    const savedEvents = localStorage.getItem('events');
    const savedLinks = localStorage.getItem('links');

    if (savedEvents && savedLinks) {
        console.info("Restoring previous analysis from session...");
        events = JSON.parse(savedEvents);
        links = JSON.parse(savedLinks);

        const loading = document.getElementById('loading');
        const dashboard = document.getElementById('dashboard');
        const dropArea = document.getElementById('drop-area');

        if (loading) loading.style.display = 'none';
        if (dashboard) dashboard.style.display = 'block';
        if (dropArea) dropArea.style.display = 'none';
        renderDashboard();
    }
}

// Start the app
init();
