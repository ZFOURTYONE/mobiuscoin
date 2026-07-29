# MobiusCoin - Blockchain Berbasis Möbius Strip

<div align="center">

![MobiusCoin](https://img.shields.io/badge/Möbius-Blockchain-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Blockchain revolusioner dengan konsep topologi Möbius strip**

[Analisis Lengkap](#analisis-algoritma) • [Dokumentasi](#dokumentasi) • [Quick Start](#quick-start) • [Contoh](#contoh-penggunaan)

</div>

---

## 🎯 Overview

MobiusCoin adalah implementasi blockchain novel yang menerapkan konsep matematis **Möbius strip** dalam arsitektur blockchain. Berbeda dengan blockchain tradisional yang menggunakan Proof of Work (PoW) atau Proof of Stake (PoS), MobiusCoin menggunakan **Möbius Consensus** - validasi berbasis integritas topologi dalam waktu O(1) per blok.

### ✨ Fitur Utama

- 🔀 **Twist Hash Function** - Hash dengan properti Möbius (orientasi-dependent)
- ⚡ **O(1) Consensus** - Validasi blok dalam waktu konstan
- 🔄 **Anti-State Ledger** - Akun dengan dua sisi yang terhubung melalui twist
- 🔗 **Loop Ledger** - Struktur blockchain siklik tanpa fork
- 🛡️ **Topological Security** - Keamanan berbasis integritas ruang topologi

---

## 📊 Perbandingan dengan Blockchain Lain

| Aspek | Bitcoin | Ethereum | **MobiusCoin** |
|-------|---------|----------|----------------|
| Consensus | PoW | PoS | **Möbius O(1)** |
| Hash Function | SHA-256 | Keccak-256 | **Twist Hash** |
| Fork Handling | Longest chain | Gas-based | **No forks (topology)** |
| Account Model | UTXO | Account-based | **Anti-State Ledger** |
| Validation Time | O(N) voting | O(N) voting | **O(1) per block** |
| Orientation | None | None | **+1/-1 alternating** |
| Energy Usage | High | Medium | **Low** |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Tidak ada dependensi eksternal (pure Python!)

### Instalasi

```bash
# Clone repository
git clone https://github.com/ZFOURTYONE/mobiuscoin.git
cd mobiuscoin

# Jalankan demo
python3 mobius_blockchain.py
```

### Contoh Sederhana

```python
from mobius_blockchain import MobiusChain, Wallet

# 1. Buat blockchain
chain = MobiusChain(difficulty=4)

# 2. Buat wallets
alice = Wallet("alice")
bob = Wallet("bob")

# 3. Fund alice dengan 1000 koin
chain._ensure_account("alice").transact_in(1000.0)

# 4. Buat transaksi
tx = alice.create_transaction("bob", 100.0)
chain.add_transaction(tx)

# 5. Mine blok
chain.mine_pending_transactions()

# 6. Validasi chain
valid, msg = chain.validate_chain()
print(f"Chain valid: {valid}")
print(f"Message: {msg}")

# 7. Cek balance
print(f"Alice: {chain.get_balance('alice')}")
print(f"Bob: {chain.get_balance('bob')}")
```

---

## 📖 Dokumentasi

### 🧮 Analisis Algoritma

#### Konsep Möbius Strip

Möbius strip adalah permukaan topologi dengan properti unik:
- **Satu sisi, satu batas**: Tidak ada perbedaan antara "atas" dan "bawah"
- **Non-orientable**: Tidak dapat didefinisikan orientasi global
- **Twist**: Setiap loop penuh membalik orientasi

#### Penerapan dalam Blockchain

```
┌─────────────────────────────────────────┐
│     Möbius Strip Properties             │
├─────────────────────────────────────────┤
│                                         │
│  Satu Sisi    →  Tidak ada fork         │
│  Twist        →  Orientasi bergantian   │
│  Non-orient   →  No hierarchy           │
│  Loop         →  Siklik structure       │
│  Robekan      →  Tamper detection       │
│                                         │
└─────────────────────────────────────────┘
```

### 🔬 Komponen Utama

#### 1. Twist Hash Function (THF)

Hash function dengan properti Möbius:

```python
from mobius_blockchain import TwistHashFunction

thf = TwistHashFunction()

# Hash dengan twist depth
hash_result, orientation = thf.hash_with_twist("data", twist_depth=3)
print(f"Hash: {hash_result}")
print(f"Orientation: {orientation}")  # +1 atau -1
```

**Properti**:
- Setiap iterasi membalik orientasi bit
- Output tergantung pada twist depth
- Tamper detection melalui perubahan orientasi

#### 2. Anti-State Ledger (ASL)

Akun dengan dua sisi yang terhubung melalui twist:

```python
from mobius_blockchain import AntiStateAccount

account = AntiStateAccount("user1")
account.transact_in(100.0)

print(f"Initial: {account}")
# Output: Account(user1: A=100.00, B=0.00, orient=1)

account.transact_out(30.0)
print(f"After tx: {account}")
# Output: Account(user1: A=20.00, B=80.00, orient=-1)
#         ^^^^ TWIST! Orientasi flip, sisi swap
```

**Mekanisme**:
- Transaksi keluar: `side_a → side_b` + twist
- Transaksi masuk: langsung ke `side_a`
- Setiap transaksi keluar membalik orientasi

#### 3. Block Structure

Blok dengan properti Möbius:

```python
from mobius_blockchain import Block, Transaction

# Buat transaksi
tx = Transaction("alice", "bob", 50.0)

# Buat blok
block = Block(
    index=1,
    prev_hash="0" * 64,
    transactions=[tx],
    orientation=1
)

# Mining
block.mine(difficulty=4)

print(f"Hash: {block.hash}")
print(f"Orientation: {block.orientation}")  # -1 (twisted!)
print(f"Twist bit: {block.twist_bit}")       # 1
```

#### 4. O(1) Consensus

Validasi dalam waktu konstan per blok:

```python
from mobius_blockchain import MobiusChain

chain = MobiusChain()

# Tambah beberapa blok...
chain.mine_pending_transactions()

# Validasi
valid, message = chain.validate_chain()
print(f"Valid: {valid}")
print(f"Message: {message}")
```

**Algoritma**:
1. Check hash valid: O(1)
2. Check link ke previous: O(1)
3. Check orientation ≠ null: O(1)
4. Check twist bit consistency: O(1)

**Total**: O(1) per blok, O(N) untuk N blok

### 📊 Contoh Output

#### Demo 1: Twist Hash Function
```
Data: "Hello Möbius"
  Twist depth 1: hash=76bbc3d08c589753... | orient=1
  Twist depth 2: hash=e13328576beb9fe3... | orient=1
  Twist depth 3: hash=e898f46202123fcd... | orient=1
  Twist depth 4: hash=3cf4ee377012da58... | orient=1
```

#### Demo 2: Anti-State Ledger
```
Initial:         side_a=100.00, side_b=0.00,  orient=+1
After tx 1:      side_a=20.00,  side_b=80.00, orient=-1  (twist!)
After tx 2:      side_a=100.00, side_b=0.00,  orient=+1  (twist!)
After tx 3:      side_a=20.00,  side_b=80.00, orient=-1  (twist!)
```

#### Demo 3: Loop Ledger
```
Orientasi sequence: [1, -1, 1, -1, 1, -1]
Pattern: 1 → -1 → 1 → -1 → 1 → -1

⤸ Belum loop lengkap: orientasi terbalik (seperti Möbius!)
```

---

## 🎓 Contoh Penggunaan

### Contoh 1: Transaksi Sederhana

```python
from mobius_blockchain import MobiusChain, Wallet

# Setup
chain = MobiusChain(difficulty=2)
alice = Wallet("alice")
bob = Wallet("bob")

# Fund alice
chain._ensure_account("alice").transact_in(500.0)

# Alice kirim ke Bob
tx1 = alice.create_transaction("bob", 100.0)
tx2 = alice.create_transaction("bob", 50.0)

chain.add_transaction(tx1)
chain.add_transaction(tx2)

# Mine
chain.mine_pending_transactions()

# Cek balance
print(f"Alice: {chain.get_balance('alice')}")  # 350.0
print(f"Bob: {chain.get_balance('bob')}")      # 150.0
```

### Contoh 2: Inspecting Blockchain

```python
# Print chain status
chain.print_chain_status()

# Output:
# ============================================================
# MOBIUS BLOCKCHAIN STATUS
# ============================================================
# Panjang chain: 2 blok
# Akun aktif: 3
# Transaksi pending: 0
# 
# Blok-blok:
#   #0: hash=a19f27d67f95e6dd | orient=1 | twist=0 | tx=0
#   #1: hash=7b6868a517c445ae | orient=-1 | twist=1 | tx=2
# 
# Akun:
#   mobius_miner: A=100.00 | B=0.00 | orient=1
#   alice: A=350.00 | B=150.00 | orient=1
#   bob: A=150.00 | B=0.00 | orient=1
# ============================================================
```

### Contoh 3: Chain Validation

```python
# Validasi chain
valid, msg = chain.validate_chain()

if valid:
    print("✅ Chain valid!")
    print(f"Message: {msg}")
else:
    print("❌ Chain invalid!")
    print(f"Error: {msg}")

# Output:
# ✅ Chain valid!
# Message: Ruang utuh — konsensus O(1) diterima (2 blok)
```

### Contoh 4: Multiple Blocks

```python
chain = MobiusChain(difficulty=2)

# Mine 10 blok
for i in range(10):
    chain._ensure_account("user").transact_in(10.0)
    tx = Transaction("user", "recipient", 5.0)
    chain.add_transaction(tx)
    chain.mine_pending_transactions()

# Cek pola orientasi
orientations = [block.orientation for block in chain.chain]
print(f"Orientations: {orientations}")
# Output: [1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1]

# Validasi
valid, msg = chain.validate_chain()
print(f"Valid: {valid} | {msg}")
```

### Contoh 5: Anti-State Behavior

```python
from mobius_blockchain import AntiStateAccount

account = AntiStateAccount("demo")
account.transact_in(100.0)

print("Initial state:")
print(f"  Side A: {account.side_a:.2f}")
print(f"  Side B: {account.side_b:.2f}")
print(f"  Orientation: {account.orientation}")
print(f"  Twist count: {account.twist_count}")

# Transaksi 1
account.transact_out(30.0)
print("\nAfter tx 1 (30 units out):")
print(f"  Side A: {account.side_a:.2f}")
print(f"  Side B: {account.side_b:.2f}")
print(f"  Orientation: {account.orientation}")
print(f"  Twist count: {account.twist_count}")

# Transaksi 2
account.transact_out(20.0)
print("\nAfter tx 2 (20 units out):")
print(f"  Side A: {account.side_a:.2f}")
print(f"  Side B: {account.side_b:.2f}")
print(f"  Orientation: {account.orientation}")
print(f"  Twist count: {account.twist_count}")

print("\n💡 Note: Setiap transaksi keluar menyebabkan TWIST!")
print("   Side A dan B swap, orientasi flip (+1 ↔ -1)")
```

---

## 🧪 Testing

Jalankan semua demo:

```bash
python3 mobius_blockchain.py
```

Output akan menampilkan:
1. Twist Hash Function demo
2. Anti-State Ledger demo
3. Basic blockchain demo
4. Loop ledger demo

---

## 📚 Dokumentasi Lengkap

Untuk analisis mendalam dan dokumentasi teknis lengkap, lihat:

- [IMPLEMENTASI_LENGKAP.md](IMPLEMENTASI_LENGKAP.md) - Analisis matematis dan arsitektur
- [ANALISIS_MOBIUS.md](ANALISIS_MOBIUS.md) - Konsep awal algoritma
- [MOBIUS_CONSENSUS_O1.md](MOBIUS_CONSENSUS_O1.md) - Teori O(1) consensus

---

## 🔮 Roadmap

### Phase 1: Core (✅ Done)
- [x] Twist Hash Function
- [x] Anti-State Ledger
- [x] Block structure dengan twist
- [x] O(1) consensus validator
- [x] Transaction system
- [x] Wallet & signatures

### Phase 2: Network (🚧 In Progress)
- [ ] P2P network layer
- [ ] Node discovery
- [ ] Block propagation
- [ ] Transaction relay

### Phase 3: Advanced Features
- [ ] Smart contracts
- [ ] Merkle tree optimization
- [ ] Byzantine fault tolerance
- [ ] Cross-chain bridges

### Phase 4: Production
- [ ] Security audit
- [ ] Performance optimization
- [ ] Mainnet deployment
- [ ] Documentation & tutorials

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgments

- August Ferdinand Möbius - Penemu Möbius strip (1858)
- Satoshi Nakamoto - Pencipta Bitcoin dan konsep blockchain
- Vitalik Buterin - Pencipta Ethereum dan smart contracts

---

## 📧 Contact

Untuk pertanyaan dan diskusi:
- GitHub Issues: [ZFOURTYONE/mobiuscoin/issues](https://github.com/ZFOURTYONE/mobiuscoin/issues)

---

<div align="center">

**Dibuat dengan ❤️ untuk eksplorasi topologi dalam blockchain**

⭐ Star this repo jika Anda menemukan proyek ini menarik!

</div>
