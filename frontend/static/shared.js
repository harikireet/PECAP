/**
 * PCAP StoryTeller - Shared Frontend Utilities
 * Centralizes common logic used across all forensic views.
 */

// Global Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+F or Ctrl+K for Search
    if (e.ctrlKey && (e.key === 'f' || e.key === 'k')) {
        e.preventDefault();
        window.open('/search', '_blank');
    }
});

/**
 * Truncate long strings with ellipses
 */
function truncate(str, len) {
    if (!str) return '';
    if (str.length <= len) return str;
    return str.substr(0, len) + '…';
}

/**
 * Common event detail viewer with syntax highlighting
 */
function showDetails(event, targetId = 'details-content') {
    const pre = document.getElementById(targetId);
    if (!pre) return;
    pre.innerHTML = syntaxHighlight(event);
}

/**
 * Generates beautiful HTML structure for network event JSON
 */
function syntaxHighlight(event) {
    // Deep clone to avoid modifying original
    const data = JSON.parse(JSON.stringify(event));

    let html = '<div class="json-viewer">';

    // Header identification
    html += `<div class="detail-row"><span class="key">ID:</span> <span class="number">#${data.id}</span></div>`;
    html += `<div class="detail-row"><span class="key">Type:</span> <span class="hl-type">${data.type}</span></div>`;
    html += `<div class="detail-row"><span class="key">Timestamp:</span> <span class="string">${new Date(data.timestamp * 1000).toLocaleString()}</span></div>`;

    // IP Context
    if (data.source_ip || data.src_ip) {
        html += `<div class="detail-row"><span class="key">Source IP:</span> <span class="hl-ip">${data.source_ip || data.src_ip}</span></div>`;
    }
    if (data.dest_ip || data.dst_ip) {
        html += `<div class="detail-row"><span class="key">Dest IP:</span> <span class="hl-ip">${data.dest_ip || data.dst_ip}</span></div>`;
    }

    // Description
    html += `<div class="detail-row"><span class="key">Description:</span> <span class="string">"${data.description}"</span></div>`;

    // Protocol Specific Details
    if (data.details && Object.keys(data.details).length > 0) {
        html += `<div class="detail-row" style="margin-top: 10px;"><span class="key">Protocol Data:</span></div>`;
        html += '<div style="margin-left: 20px; border-left: 1px solid rgba(100, 255, 218, 0.1); padding-left: 15px;">';

        for (const [key, value] of Object.entries(data.details)) {
            let valClass = 'string';
            let formattedVal = value;

            if (typeof value === 'number') valClass = 'number';
            if (['sport', 'dport', 'port', 'type', 'code'].includes(key.toLowerCase())) valClass = 'hl-port';
            if (['query', 'sni', 'domain', 'host', 'url'].includes(key.toLowerCase())) valClass = 'hl-domain';
            if (['ip', 'address'].includes(key.toLowerCase())) valClass = 'hl-ip';

            html += `<div class="detail-row"><span class="key">${key}:</span> <span class="${valClass}">${formattedVal}</span></div>`;
        }
        html += '</div>';
    }

    html += '</div>';
    return html;
}
