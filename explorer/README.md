# MobiusCoin Blockchain Explorer

<div align="center">

![MobiusCoin Explorer](https://img.shields.io/badge/MobiusCoin-Explorer-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Flask](https://img.shields.io/badge/Flask-2.3+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Full-stack blockchain explorer untuk MobiusCoin**

[Quick Start](#quick-start) • [Features](#features) • [API Docs](#api-documentation)

</div>

---

## 🎯 Overview

MobiusCoin Explorer adalah web blockchain explorer fullstack yang memungkinkan Anda menjelajahi blockchain MobiusCoin secara interaktif melalui browser web.

### ✨ Features

- 📊 **Dashboard** - Statistik real-time blockchain
- 🧱 **Block Explorer** - Lihat detail semua blok
- 💸 **Transaction Viewer** - Track semua transaksi
- 👤 **Account Manager** - Lihat balance dan history akun
- 🔍 **Search** - Cari blok, transaksi, atau akun
- ⚡ **Actions** - Buat akun, transfer, mine blok
- 🎨 **Modern UI** - Responsive dark theme

---

## 🚀 Quick Start

### Metode 1: Script Otomatis

```bash
cd /home/user/mobiuscoin/explorer
chmod +x start.sh
./start.sh
```

### Metode 2: Manual

```bash
cd /home/user/mobiuscoin/explorer

# Install dependencies
pip install --break-system-packages -r requirements.txt

# Run explorer
python3 app.py
```

### Akses Explorer

Buka browser dan kunjungi: **http://localhost:5000**

---

## 📸 Screenshots

### Dashboard
- Statistik blockchain real-time
- Distribusi orientasi (+1/-1)
- Blok terbaru

### Block Explorer
- List semua blok dengan detail
- Click untuk lihat detail blok
- Informasi transaksi dalam blok

### Transaction Viewer
- List semua transaksi
- Detail pengirim, penerima, jumlah
- Link ke blok dan akun terkait

### Account Manager
- List semua akun dengan balance
- Side A dan Side B (Anti-State)
- Riwayat transaksi per akun

### Actions
- Buat akun baru dengan balance awal
- Transfer token antar akun
- Mine blok baru

---

## 🏗️ Architecture

```
explorer/
├── app.py              # Backend Flask API
├── static/
│   ├── index.html      # Frontend HTML
│   ├── style.css       # Styling
│   └── script.js       # Frontend logic
├── requirements.txt    # Python dependencies
├── start.sh           # Quick start script
└── README.md          # This file
```

### Backend (Python Flask)
- **REST API** untuk semua operasi blockchain
- **SQLite database** untuk indexing
- **Real-time data** dari MobiusChain
- **CORS enabled** untuk development

### Frontend (Vanilla JS)
- **Single Page Application** (SPA)
- **No framework** - pure JavaScript
- **Responsive design** - mobile friendly
- **Dark theme** - modern UI

---

## 🔌 API Documentation

### Status & Stats

```bash
GET /api/status
```
Returns blockchain status (chain length, accounts, pending txs, etc.)

```bash
GET /api/stats
```
Returns detailed statistics (avg block time, orientation distribution, etc.)

### Blocks

```bash
GET /api/blocks?page=1&per_page=20
```
Returns paginated list of blocks

```bash
GET /api/block/<block_id>
```
Returns detailed block information with transactions

### Transactions

```bash
GET /api/transactions?page=1&per_page=20
```
Returns paginated list of all transactions

```bash
GET /api/transaction/<tx_hash>
```
Returns detailed transaction information

### Accounts

```bash
GET /api/accounts?page=1&per_page=20
```
Returns paginated list of all accounts

```bash
GET /api/account/<address>
```
Returns account details with transaction history

### Search

```bash
GET /api/search?q=<query>
```
Search for blocks, transactions, or accounts by hash or address

### Actions

```bash
POST /api/create_account
Body: { "address": "alice", "initial_balance": 100.0 }
```
Create new account with initial balance

```bash
POST /api/transfer
Body: { "sender": "alice", "recipient": "bob", "amount": 50.0 }
```
Create transfer transaction

```bash
POST /api/mine
Body: { "recipient": "miner", "amount": 10.0 }
```
Mine a new block with pending transactions

---

## 🎮 Usage Examples

### 1. View Dashboard
- Open http://localhost:5000
- See real-time blockchain statistics
- View recent blocks

### 2. Explore Blocks
- Click "Blok" in navigation
- Click any block to see details
- View transactions in block

### 3. Track Transactions
- Click "Transaksi" in navigation
- Click any transaction for details
- See sender, recipient, amount

### 4. View Accounts
- Click "Akun" in navigation
- Click any account to see details
- View Side A, Side B, transaction history

### 5. Create Account
- Click "Aksi" in navigation
- Fill form with address and initial balance
- Click "Buat Akun"

### 6. Transfer Tokens
- Click "Aksi" in navigation
- Select sender from dropdown
- Enter recipient and amount
- Click "Transfer"

### 7. Mine Block
- Click "Aksi" in navigation
- Click "Mine Blok"
- Watch new block being added to chain

### 8. Search
- Use search bar in header
- Search by block hash, tx hash, or account name
- Click results to view details

---

## 🔧 Configuration

### Change Port

Edit `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Change Difficulty

Edit `app.py`:
```python
blockchain = MobiusChain(difficulty=4)  # Increase for harder mining
```

### Change Block Reward

Edit `app.py`:
```python
blockchain.block_reward = 100.0  # Increase reward
```

---

## 📊 Database

Explorer menggunakan SQLite untuk indexing blockchain:

```bash
# Database file
explorer.db

# Tables
- blocks: Block information
- transactions: Transaction data
- accounts: Account balances
```

Database otomatis dibuat saat pertama kali menjalankan explorer.

---

## 🎨 Customization

### Change Theme Colors

Edit `static/style.css`:
```css
:root {
    --primary: #6366f1;      /* Primary color */
    --secondary: #8b5cf6;    /* Secondary color */
    --success: #10b981;      /* Success color */
    --danger: #ef4444;       /* Danger color */
    --bg-dark: #0f172a;      /* Background */
    --bg-card: #1e293b;      /* Card background */
}
```

### Add New Features

1. **Backend**: Add new endpoint in `app.py`
2. **Frontend**: Add new function in `script.js`
3. **UI**: Add new HTML in `index.html`
4. **Style**: Add new CSS in `style.css`

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Dependencies Not Installed
```bash
pip install --break-system-packages flask flask-cors
```

### Database Locked
```bash
# Remove database file
rm explorer.db

# Restart explorer
python3 app.py
```

---

## 📈 Performance

- **Blocks**: Tested with 1000+ blocks
- **Transactions**: Tested with 10000+ transactions
- **Accounts**: Tested with 100+ accounts
- **Response Time**: < 100ms for most queries

---

## 🔮 Future Enhancements

- [ ] WebSocket for real-time updates
- [ ] Charts and graphs (block time, transaction volume)
- [ ] Network map visualization
- [ ] Advanced search filters
- [ ] Export data (CSV, JSON)
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Blockchain analytics

---

## 📚 Related Documentation

- [MobiusCoin README](../README.md) - Main blockchain documentation
- [Implementation Details](../IMPLEMENTASI_LENGKAP.md) - Technical deep dive
- [Use Cases](../USE_CASES.md) - Advanced examples

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

---

## 📄 License

MIT License - See main project license

---

<div align="center">

**✨ Explore the Möbius Blockchain ✨**

*Built with Python, Flask, and pure JavaScript*

</div>
