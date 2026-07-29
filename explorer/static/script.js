// MobiusCoin Explorer - Frontend JavaScript
// ===========================================

const API_BASE = '/api';
let currentPage = {};

// ============================================================================
// UTILITIES
// ============================================================================

async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification('Gagal terhubung ke server', 'error');
        return null;
    }
}

function formatTimestamp(ts) {
    const date = new Date(ts * 1000);
    return date.toLocaleString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function timeAgo(ts) {
    const now = Date.now() / 1000;
    const diff = now - ts;
    
    if (diff < 60) return `${Math.floor(diff)} detik lalu`;
    if (diff < 3600) return `${Math.floor(diff / 60)} menit lalu`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} jam lalu`;
    return `${Math.floor(diff / 86400)} hari lalu`;
}

function shortHash(hash) {
    if (!hash) return '';
    return `${hash.substring(0, 10)}...${hash.substring(hash.length - 8)}`;
}

function showNotification(message, type = 'info') {
    const notif = document.getElementById('notification');
    notif.textContent = message;
    notif.className = `notification ${type} show`;
    
    setTimeout(() => {
        notif.classList.remove('show');
    }, 3000);
}

// ============================================================================
// PAGE NAVIGATION
// ============================================================================

function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    // Show selected page
    const page = document.getElementById(pageId);
    if (page) {
        page.classList.add('active');
    }
    
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.textContent.toLowerCase().includes(pageId)) {
            btn.classList.add('active');
        }
    });
    
    // Load data for the page
    switch (pageId) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'blocks':
            loadBlocks(1);
            break;
        case 'transactions':
            loadTransactions(1);
            break;
        case 'accounts':
            loadAccounts(1);
            break;
        case 'actions':
            loadSenderOptions();
            break;
    }
}

// ============================================================================
// DASHBOARD
// ============================================================================

async function loadDashboard() {
    const [status, stats] = await Promise.all([
        apiCall('/status'),
        apiCall('/stats')
    ]);
    
    if (stats) {
        document.getElementById('totalBlocks').textContent = stats.total_blocks;
        document.getElementById('totalTransactions').textContent = stats.total_transactions;
        document.getElementById('totalAccounts').textContent = stats.total_accounts;
        document.getElementById('avgBlockTime').textContent = 
            stats.average_block_time.toFixed(1) + 's';
        
        const positive = stats.orientation_distribution.positive;
        const negative = stats.orientation_distribution.negative;
        const total = positive + negative;
        
        document.getElementById('positiveCount').textContent = positive;
        document.getElementById('negativeCount').textContent = negative;
        document.getElementById('orientationPositive').style.width = 
            `${(positive / total) * 100}%`;
        document.getElementById('orientationNegative').style.width = 
            `${(negative / total) * 100}%`;
    }
    
    if (status) {
        document.getElementById('chainValid').textContent = '✓ Valid';
        document.getElementById('chainValid').className = 'badge badge-success';
        document.getElementById('difficulty').textContent = status.difficulty;
        document.getElementById('blockReward').textContent = status.block_reward + ' MBC';
        
        if (status.latest_block) {
            document.getElementById('latestBlock').textContent = 
                `#${status.latest_block.index}`;
        }
    }
    
    // Load recent blocks
    const blocksData = await apiCall('/blocks?per_page=5');
    if (blocksData) {
        const container = document.getElementById('recentBlocks');
        container.innerHTML = blocksData.blocks.map(block => `
            <div class="list-item" onclick="showBlockDetail(${block.index})">
                <div class="list-item-header">
                    <span class="list-item-title">Blok #${block.index}</span>
                    <span class="meta-item">${timeAgo(block.timestamp)}</span>
                </div>
                <div class="list-item-meta">
                    <span class="meta-item">Hash: <strong class="hash">${shortHash(block.hash)}</strong></span>
                    <span class="meta-item">Orientasi: <strong>${block.orientation > 0 ? '+1' : '-1'}</strong></span>
                    <span class="meta-item">Transaksi: <strong>${block.num_transactions}</strong></span>
                </div>
            </div>
        `).join('');
    }
}

// ============================================================================
// BLOCKS
// ============================================================================

async function loadBlocks(page = 1) {
    currentPage.blocks = page;
    const container = document.getElementById('blocksList');
    container.innerHTML = '<div class="loading">Memuat</div>';
    
    const data = await apiCall(`/blocks?page=${page}&per_page=20`);
    
    if (!data || data.blocks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🧱</div>
                <p>Belum ada blok</p>
            </div>`;
        return;
    }
    
    container.innerHTML = data.blocks.map(block => `
        <div class="list-item" onclick="showBlockDetail(${block.index})">
            <div class="list-item-header">
                <span class="list-item-title">Blok #${block.index}</span>
                <span class="meta-item">${timeAgo(block.timestamp)}</span>
            </div>
            <div class="hash">${block.hash}</div>
            <div class="list-item-meta" style="margin-top: 10px;">
                <span class="meta-item">Prev: <strong class="hash">${shortHash(block.prev_hash)}</strong></span>
                <span class="meta-item">Nonce: <strong>${block.nonce}</strong></span>
                <span class="meta-item">Orientasi: <strong>${block.orientation > 0 ? '+1' : '-1'}</strong></span>
                <span class="meta-item">Twist: <strong>${block.twist_bit}</strong></span>
                <span class="meta-item">Transaksi: <strong>${block.num_transactions}</strong></span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('blocksPage').textContent = `Halaman ${page}`;
}

async function showBlockDetail(blockId) {
    const data = await apiCall(`/block/${blockId}`);
    if (!data) return;
    
    document.getElementById('blockDetailContent').innerHTML = `
        <div class="detail-section">
            <h3>Informasi Blok</h3>
            <div class="detail-grid">
                <span class="detail-label">Index:</span>
                <span class="detail-value">${data.index}</span>
                
                <span class="detail-label">Hash:</span>
                <span class="detail-value hash">${data.hash}</span>
                
                <span class="detail-label">Previous Hash:</span>
                <span class="detail-value hash">${data.prev_hash}</span>
                
                <span class="detail-label">Timestamp:</span>
                <span class="detail-value">${formatTimestamp(data.timestamp)}</span>
                
                <span class="detail-label">Nonce:</span>
                <span class="detail-value">${data.nonce}</span>
                
                <span class="detail-label">Orientasi:</span>
                <span class="detail-value">${data.orientation > 0 ? '+1 (Positif)' : '-1 (Negatif)'}</span>
                
                <span class="detail-label">Twist Bit:</span>
                <span class="detail-value">${data.twist_bit}</span>
                
                <span class="detail-label">Merkle Root:</span>
                <span class="detail-value hash">${data.merkle_root}</span>
                
                <span class="detail-label">Jumlah Transaksi:</span>
                <span class="detail-value">${data.transactions.length}</span>
            </div>
        </div>
        
        <div class="detail-section">
            <h3>Transaksi (${data.transactions.length})</h3>
            ${data.transactions.length === 0 ? '<p style="color: var(--text-secondary)">Tidak ada transaksi (Genesis Block)</p>' :
            data.transactions.map((tx, i) => `
                <div class="list-item" onclick="showTransactionDetail('${tx.hash}')" style="margin-bottom: 10px;">
                    <div class="list-item-header">
                        <span class="list-item-title">Transaksi #${i + 1}</span>
                        <span class="meta-item">${timeAgo(tx.timestamp)}</span>
                    </div>
                    <div class="list-item-meta">
                        <span class="meta-item">Dari: <strong onclick="event.stopPropagation(); showAccountDetail('${tx.sender}')">${tx.sender}</strong></span>
                        <span class="meta-item">Ke: <strong onclick="event.stopPropagation(); showAccountDetail('${tx.recipient}')">${tx.recipient}</strong></span>
                        <span class="meta-item">Jumlah: <strong>${tx.amount} MBC</strong></span>
                    </div>
                    <div class="hash" style="margin-top: 8px;">${tx.hash}</div>
                </div>
            `).join('')}
        </div>
    `;
    
    showPage('blockDetail');
}

// ============================================================================
// TRANSACTIONS
// ============================================================================

async function loadTransactions(page = 1) {
    currentPage.transactions = page;
    const container = document.getElementById('transactionsList');
    container.innerHTML = '<div class="loading">Memuat</div>';
    
    const data = await apiCall(`/transactions?page=${page}&per_page=20`);
    
    if (!data || data.transactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">💸</div>
                <p>Belum ada transaksi</p>
            </div>`;
        return;
    }
    
    container.innerHTML = data.transactions.map(tx => `
        <div class="list-item" onclick="showTransactionDetail('${tx.hash}')">
            <div class="list-item-header">
                <span class="list-item-title">${tx.amount} MBC</span>
                <span class="meta-item">${timeAgo(tx.timestamp)}</span>
            </div>
            <div class="list-item-meta">
                <span class="meta-item">Dari: <strong>${tx.sender}</strong></span>
                <span class="meta-item">→</span>
                <span class="meta-item">Ke: <strong>${tx.recipient}</strong></span>
                <span class="meta-item">Blok: <strong>#${tx.block_id}</strong></span>
            </div>
            <div class="hash" style="margin-top: 8px;">${tx.hash}</div>
        </div>
    `).join('');
    
    document.getElementById('transactionsPage').textContent = `Halaman ${page}`;
}

async function showTransactionDetail(txHash) {
    const data = await apiCall(`/transaction/${txHash}`);
    if (!data) return;
    
    document.getElementById('transactionDetailContent').innerHTML = `
        <div class="detail-section">
            <h3>Informasi Transaksi</h3>
            <div class="detail-grid">
                <span class="detail-label">Hash:</span>
                <span class="detail-value hash">${data.hash}</span>
                
                <span class="detail-label">Blok:</span>
                <span class="detail-value">
                    <a href="#" onclick="showBlockDetail(${data.block_id}); return false;" style="color: var(--primary);">
                        Blok #${data.block_id}
                    </a>
                </span>
                
                <span class="detail-label">Pengirim:</span>
                <span class="detail-value">
                    <a href="#" onclick="showAccountDetail('${data.sender}'); return false;" style="color: var(--primary);">
                        ${data.sender}
                    </a>
                </span>
                
                <span class="detail-label">Penerima:</span>
                <span class="detail-value">
                    <a href="#" onclick="showAccountDetail('${data.recipient}'); return false;" style="color: var(--primary);">
                        ${data.recipient}
                    </a>
                </span>
                
                <span class="detail-label">Jumlah:</span>
                <span class="detail-value" style="color: var(--success); font-weight: bold;">${data.amount} MBC</span>
                
                <span class="detail-label">Timestamp:</span>
                <span class="detail-value">${formatTimestamp(data.timestamp)}</span>
                
                <span class="detail-label">Nonce:</span>
                <span class="detail-value">${data.nonce}</span>
                
                <span class="detail-label">Signature:</span>
                <span class="detail-value hash">${data.signature}</span>
            </div>
        </div>
    `;
    
    showPage('transactionDetail');
}

// ============================================================================
// ACCOUNTS
// ============================================================================

async function loadAccounts(page = 1) {
    currentPage.accounts = page;
    const container = document.getElementById('accountsList');
    container.innerHTML = '<div class="loading">Memuat</div>';
    
    const data = await apiCall(`/accounts?page=${page}&per_page=20`);
    
    if (!data || data.accounts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">👤</div>
                <p>Belum ada akun</p>
            </div>`;
        return;
    }
    
    container.innerHTML = data.accounts.map(acc => `
        <div class="list-item" onclick="showAccountDetail('${acc.address}')">
            <div class="list-item-header">
                <span class="list-item-title">${acc.address}</span>
                <span class="meta-item" style="color: var(--success); font-weight: bold;">${acc.side_a.toFixed(2)} MBC</span>
            </div>
            <div class="list-item-meta">
                <span class="meta-item">Side A: <strong>${acc.side_a.toFixed(2)}</strong></span>
                <span class="meta-item">Side B: <strong>${acc.side_b.toFixed(2)}</strong></span>
                <span class="meta-item">Orientasi: <strong>${acc.orientation > 0 ? '+1' : '-1'}</strong></span>
                <span class="meta-item">Twist Count: <strong>${acc.twist_count}</strong></span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('accountsPage').textContent = `Halaman ${page}`;
}

async function showAccountDetail(address) {
    const data = await apiCall(`/account/${address}`);
    if (!data) return;
    
    document.getElementById('accountDetailContent').innerHTML = `
        <div class="detail-section">
            <h3>Informasi Akun</h3>
            <div class="detail-grid">
                <span class="detail-label">Alamat:</span>
                <span class="detail-value">${data.address}</span>
                
                <span class="detail-label">Total Balance:</span>
                <span class="detail-value" style="color: var(--success); font-weight: bold; font-size: 1.2rem;">${data.total_balance.toFixed(2)} MBC</span>
                
                <span class="detail-label">Side A (Visible):</span>
                <span class="detail-value">${data.side_a.toFixed(2)} MBC</span>
                
                <span class="detail-label">Side B (Hidden):</span>
                <span class="detail-value">${data.side_b.toFixed(2)} MBC</span>
                
                <span class="detail-label">Orientasi:</span>
                <span class="detail-value">${data.orientation > 0 ? '+1 (Positif)' : '-1 (Negatif)'}</span>
                
                <span class="detail-label">Twist Count:</span>
                <span class="detail-value">${data.twist_count}</span>
            </div>
        </div>
        
        <div class="detail-section">
            <h3>Riwayat Transaksi (${data.transactions.length})</h3>
            ${data.transactions.length === 0 ? '<p style="color: var(--text-secondary)">Belum ada transaksi</p>' :
            data.transactions.map(tx => `
                <div class="list-item" onclick="showTransactionDetail('${tx.hash}')" style="margin-bottom: 10px;">
                    <div class="list-item-header">
                        <span class="list-item-title">
                            <span class="tx-type ${tx.type === 'sent' ? 'tx-sent' : 'tx-received'}">
                                ${tx.type === 'sent' ? '↑ TERKIRIM' : '↓ DITERIMA'}
                            </span>
                            ${tx.amount} MBC
                        </span>
                        <span class="meta-item">${timeAgo(tx.timestamp)}</span>
                    </div>
                    <div class="list-item-meta">
                        ${tx.type === 'sent' ? 
                            `<span class="meta-item">Ke: <strong>${tx.recipient}</strong></span>` :
                            `<span class="meta-item">Dari: <strong>${tx.sender}</strong></span>`
                        }
                        <span class="meta-item">Blok: <strong>#${tx.block_id}</strong></span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    showPage('accountDetail');
}

// ============================================================================
// ACTIONS
// ============================================================================

async function loadSenderOptions() {
    const data = await apiCall('/accounts');
    if (!data) return;
    
    const select = document.getElementById('transferSender');
    select.innerHTML = data.accounts.map(acc => 
        `<option value="${acc.address}">${acc.address} (${acc.side_a.toFixed(2)} MBC)</option>`
    ).join('');
}

async function createAccount(event) {
    event.preventDefault();
    
    const address = document.getElementById('newAccountAddress').value;
    const balance = parseFloat(document.getElementById('newAccountBalance').value);
    
    const result = await apiCall('/create_account', {
        method: 'POST',
        body: JSON.stringify({ address, initial_balance: balance })
    });
    
    if (result && result.success) {
        showNotification(`Akun "${address}" berhasil dibuat!`, 'success');
        event.target.reset();
        loadDashboard();
    } else {
        showNotification(result?.error || 'Gagal membuat akun', 'error');
    }
}

async function transfer(event) {
    event.preventDefault();
    
    const sender = document.getElementById('transferSender').value;
    const recipient = document.getElementById('transferRecipient').value;
    const amount = parseFloat(document.getElementById('transferAmount').value);
    
    const result = await apiCall('/transfer', {
        method: 'POST',
        body: JSON.stringify({ sender, recipient, amount })
    });
    
    if (result && result.success) {
        showNotification(`Transfer ${amount} MBC berhasil!`, 'success');
        event.target.reset();
        loadDashboard();
    } else {
        showNotification(result?.error || 'Gagal transfer', 'error');
    }
}

async function mineBlock(event) {
    event.preventDefault();
    
    showNotification('Mining blok baru...', 'info');
    
    const result = await apiCall('/mine', {
        method: 'POST',
        body: JSON.stringify({ recipient: 'miner', amount: 10.0 })
    });
    
    if (result && result.success) {
        showNotification(`Blok #${result.block.index} berhasil di-mine!`, 'success');
        loadDashboard();
    } else {
        showNotification(result?.error || 'Gagal mining blok', 'error');
    }
}

// ============================================================================
// SEARCH
// ============================================================================

async function search() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;
    
    const results = await apiCall(`/search?q=${encodeURIComponent(query)}`);
    if (!results) return;
    
    const container = document.getElementById('searchResultsContent');
    
    let html = '';
    
    // Blocks
    if (results.blocks.length > 0) {
        html += `<div class="search-section">
            <h3>🧱 Blok (${results.blocks.length})</h3>
            ${results.blocks.map(b => `
                <div class="list-item" onclick="showBlockDetail(${b.index})">
                    <span class="list-item-title">Blok #${b.index}</span>
                    <div class="hash">${b.hash}</div>
                </div>
            `).join('')}
        </div>`;
    }
    
    // Transactions
    if (results.transactions.length > 0) {
        html += `<div class="search-section">
            <h3>💸 Transaksi (${results.transactions.length})</h3>
            ${results.transactions.map(tx => `
                <div class="list-item" onclick="showTransactionDetail('${tx.hash}')">
                    <span class="list-item-title">${tx.sender} → ${tx.recipient}</span>
                    <div class="hash">${tx.hash}</div>
                </div>
            `).join('')}
        </div>`;
    }
    
    // Accounts
    if (results.accounts.length > 0) {
        html += `<div class="search-section">
            <h3>👤 Akun (${results.accounts.length})</h3>
            ${results.accounts.map(acc => `
                <div class="list-item" onclick="showAccountDetail('${acc.address}')">
                    <span class="list-item-title">${acc.address}</span>
                </div>
            `).join('')}
        </div>`;
    }
    
    if (!html) {
        html = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <p>Tidak ada hasil untuk "${query}"</p>
            </div>`;
    }
    
    container.innerHTML = html;
    showPage('searchResults');
}

// Search on Enter key
document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') search();
});

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    
    // Auto-refresh dashboard every 10 seconds
    setInterval(() => {
        if (document.getElementById('dashboard').classList.contains('active')) {
            loadDashboard();
        }
    }, 10000);
});
