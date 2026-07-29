# 🚀 MobiusCoin - Quick Reference Card

## ⚡ Quick Start Commands

### Run Web Explorer
```bash
cd /home/user/mobiuscoin/explorer
./start.sh
# Open: http://localhost:5000
```

### Run Blockchain Demo
```bash
cd /home/user/mobiuscoin
python3 mobius_blockchain.py
```

### Run Tests
```bash
cd /home/user/mobiuscoin
python3 test_mobius.py
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `mobius_blockchain.py` | Core blockchain implementation |
| `explorer/app.py` | Web explorer backend |
| `test_mobius.py` | Test suite (9 tests) |
| `README.md` | Main documentation |
| `EXPLORER_GUIDE.md` | Explorer usage guide |
| `IMPLEMENTASI_LENGKAP.md` | Technical deep dive |

---

## 🎯 Key Features

### Blockchain
- ✅ Twist Hash Function
- ✅ Anti-State Ledger (2-sided accounts)
- ✅ O(1) Consensus
- ✅ Loop Ledger Structure
- ✅ Non-Orientable Signatures

### Explorer
- 📊 Dashboard dengan statistik
- 🧱 Block explorer
- 💸 Transaction viewer
- 👤 Account manager
- 🔍 Search functionality
- ⚡ Interactive actions (create, transfer, mine)

---

## 📊 Test Results

```
✅ Twist Hash Function
✅ Anti-State Ledger
✅ Transaction System
✅ Merkle Tree
✅ Block Structure
✅ Wallet System
✅ MobiusChain
✅ Orientation Pattern
✅ Topological Integrity

Total: 9/9 tests passed (100%)
```

---

## 🔌 API Quick Reference

### Read Data
```bash
# Status
curl http://localhost:5000/api/status

# Blocks
curl http://localhost:5000/api/blocks

# Transactions
curl http://localhost:5000/api/transactions

# Accounts
curl http://localhost:5000/api/accounts

# Search
curl "http://localhost:5000/api/search?q=alice"
```

### Write Data
```bash
# Create account
curl -X POST http://localhost:5000/api/create_account \
  -H "Content-Type: application/json" \
  -d '{"address": "alice", "initial_balance": 1000}'

# Transfer
curl -X POST http://localhost:5000/api/transfer \
  -H "Content-Type: application/json" \
  -d '{"sender": "alice", "recipient": "bob", "amount": 50}'

# Mine block
curl -X POST http://localhost:5000/api/mine \
  -H "Content-Type: application/json" \
  -d '{"recipient": "miner", "amount": 10}'
```

---

## 🎨 Explorer Pages

1. **Dashboard** (`/`) - Stats & overview
2. **Blocks** (`#blocks`) - All blocks
3. **Transactions** (`#transactions`) - All transactions
4. **Accounts** (`#accounts`) - All accounts
5. **Actions** (`#actions`) - Create/Transfer/Mine
6. **Search** - Find anything

---

## 📚 Documentation Guide

| Need | Read |
|------|------|
| Getting started | `README.md` |
| Using explorer | `EXPLORER_GUIDE.md` |
| Technical details | `IMPLEMENTASI_LENGKAP.md` |
| Advanced examples | `USE_CASES.md` |
| Project summary | `RINGKASAN.md` |
| Complete list | `DELIVERABLES.md` |

---

## 🔧 Common Tasks

### Change Port
Edit `explorer/app.py`:
```python
app.run(host='0.0.0.0', port=8080)
```

### Change Difficulty
Edit `explorer/app.py`:
```python
blockchain = MobiusChain(difficulty=4)
```

### Reset Database
```bash
cd explorer
rm explorer.db
python3 app.py
```

### View Logs
```bash
tail -f /tmp/explorer.log
```

---

## 📈 Project Stats

```
Total Files: 12
Code Lines: 4,500+
Tests: 9/9 passed
API Endpoints: 12
Documentation: 2,000+ lines
Features: 20+
```

---

## 🎓 Learning Path

1. **Start**: Read `README.md`
2. **Explore**: Run `./start.sh` in explorer/
3. **Understand**: Read `IMPLEMENTASI_LENGKAP.md`
4. **Experiment**: Try actions in explorer
5. **Extend**: Read `USE_CASES.md`
6. **Contribute**: Modify code & test

---

## 🐛 Troubleshooting

### Port in use
```bash
lsof -i :5000
kill -9 <PID>
```

### Dependencies missing
```bash
pip install --break-system-packages flask flask-cors
```

### Database issues
```bash
rm explorer/explorer.db
```

---

## 📞 Quick Help

```bash
# View main docs
cat README.md

# View explorer guide
cat EXPLORER_GUIDE.md

# View technical docs
cat IMPLEMENTASI_LENGKAP.md

# Run tests
python3 test_mobius.py

# Check API status
curl http://localhost:5000/api/status
```

---

<div align="center">

**✨ MobiusCoin - Blockchain Berbasis Möbius Strip ✨**

*Complete Implementation + Full-Stack Explorer*

### 🚀 Ready to Use!

```bash
cd /home/user/mobiuscoin/explorer
./start.sh
```

</div>
