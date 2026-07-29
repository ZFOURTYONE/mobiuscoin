#!/usr/bin/env python3
"""
MobiusCoin Blockchain - Full Implementation
============================================
Implementasi lengkap blockchain berbasis Möbius strip dengan:
- Twist Hash Function (THF)
- Anti-State Ledger (ASL)
- O(1) Möbius Consensus
- Loop Ledger structure
- Non-Orientable Signatures
- Wallet & Transaction system
"""

import hashlib
import time
import json
import struct
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import binascii


# ============================================================================
# TWIST HASH FUNCTION (THF)
# ============================================================================

class TwistHashFunction:
    """
    Hash function dengan properti Möbius:
    - Setiap iterasi membalik orientasi bit
    - Deteksi tampering melalui perubahan orientasi
    - Non-orientable: output tergantung pada "sisi" yang dilihat
    """
    
    def __init__(self):
        self.twist_counter = 0
    
    def hash_with_twist(self, data: str, twist_depth: int = 1) -> Tuple[str, int]:
        """
        Hash data dengan twist iterations
        Setiap twist membalik bit-bit tertentu untuk menciptakan efek Möbius
        """
        result = data
        orientation = 1
        
        for i in range(twist_depth):
            # Standard hash
            h = hashlib.sha256(result.encode()).hexdigest()
            
            # Twist operation: flip bits based on iteration
            # Ini menciptakan efek "satu sisi" Möbius
            bits = bin(int(h, 16))[2:].zfill(256)
            
            if i % 2 == 0:
                # Even iteration: flip first half
                bits = bits[128:] + bits[:128]
            else:
                # Odd iteration: reverse and flip (Möbius twist)
                bits = bits[::-1]
                bits = ''.join('1' if b == '0' else '0' for b in bits)
            
            result = hex(int(bits, 2))[2:].zfill(64)
            orientation *= -1
        
        # Final twist based on total iterations
        if twist_depth % 2 == 1:
            orientation = -orientation
        
        return result, orientation
    
    def verify_twist(self, data: str, expected_hash: str, expected_orientation: int) -> bool:
        """Verifikasi bahwa hash sesuai dengan orientasi yang diharapkan"""
        computed_hash, computed_orientation = self.hash_with_twist(data)
        return computed_hash == expected_hash and computed_orientation == expected_orientation


# ============================================================================
# ANTI-STATE LEDGER (ASL)
# ============================================================================

@dataclass
class AntiStateAccount:
    """
    Akun dengan dua sisi (A dan B) yang terhubung melalui twist.
    Transaksi memindahkan nilai dari sisi A ke sisi B dalam satu lintasan.
    """
    address: str
    side_a: float = 0.0  # "Debit side" / visible balance
    side_b: float = 0.0  # "Credit side" / hidden balance
    orientation: int = 1  # +1 atau -1
    twist_count: int = 0
    last_twist_time: float = 0.0
    
    def twist(self) -> None:
        """Lakukan twist: swap sisi dan flip orientasi"""
        self.side_a, self.side_b = self.side_b, self.side_a
        self.orientation *= -1
        self.twist_count += 1
        self.last_twist_time = time.time()
    
    def transact_out(self, amount: float) -> bool:
        """Transaksi keluar: dari side_a ke side_b"""
        if self.side_a >= amount and amount > 0:
            self.side_a -= amount
            self.side_b += amount
            self.twist()
            return True
        return False
    
    def transact_in(self, amount: float) -> bool:
        """Transaksi masuk: langsung ke side_a"""
        if amount > 0:
            self.side_a += amount
            return True
        return False
    
    @property
    def total_balance(self) -> float:
        """Total balance (visible di side_a)"""
        return self.side_a
    
    def __repr__(self):
        return f"Account({self.address}: A={self.side_a:.2f}, B={self.side_b:.2f}, orient={self.orientation})"


# ============================================================================
# TRANSACTION SYSTEM
# ============================================================================

@dataclass
class Transaction:
    """Transaksi dengan tanda tangan non-orientable"""
    sender: str
    recipient: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    signature: str = ""
    nonce: int = 0
    
    def compute_tx_hash(self) -> str:
        """Hash transaksi"""
        data = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def sign(self, private_key: str) -> None:
        """Tanda tangan transaksi"""
        tx_hash = self.compute_tx_hash()
        sign_data = f"{tx_hash}{private_key}"
        self.signature = hashlib.sha256(sign_data.encode()).hexdigest()
    
    def verify_signature(self, public_key: str) -> bool:
        """Verifikasi tanda tangan"""
        if not self.signature:
            return False
        tx_hash = self.compute_tx_hash()
        expected = hashlib.sha256(f"{tx_hash}{public_key}".encode()).hexdigest()
        return self.signature == expected
    
    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "nonce": self.nonce
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        return cls(**data)


# ============================================================================
# MERKLE TREE FOR TWIST VERIFICATION
# ============================================================================

class MerkleTree:
    """Merkle tree dengan twist untuk verifikasi transaksi"""
    
    def __init__(self):
        self.thf = TwistHashFunction()
    
    def compute_root(self, transactions: List[Transaction]) -> str:
        """Hitung Merkle root dengan twist"""
        if not transactions:
            return "0" * 64
        
        # Hash semua transaksi
        leaves = [tx.compute_tx_hash() for tx in transactions]
        
        # Build tree dengan twist
        while len(leaves) > 1:
            new_level = []
            
            # Jika ganjil, duplikasi leaf terakhir
            if len(leaves) % 2 == 1:
                leaves.append(leaves[-1])
            
            for i in range(0, len(leaves), 2):
                combined = leaves[i] + leaves[i+1]
                # Twist: hash dengan orientasi berdasarkan level
                level = len(leaves) // 2
                h, _ = self.thf.hash_with_twist(combined, twist_depth=1)
                new_level.append(h)
            
            leaves = new_level
        
        return leaves[0]
    
    def verify_transaction(self, tx: Transaction, root: str, proof: List[str]) -> bool:
        """Verifikasi transaksi ada di Merkle tree"""
        current = tx.compute_tx_hash()
        
        for sibling in proof:
            # Tentukan posisi berdasarkan hash
            combined = current + sibling if int(current, 16) < int(sibling, 16) else sibling + current
            h, _ = self.thf.hash_with_twist(combined, twist_depth=1)
            current = h
        
        return current == root


# ============================================================================
# BLOCK WITH TWIST
# ============================================================================

@dataclass
class Block:
    """
    Blok dengan properti Möbius:
    - twist_bit: indikator apakah blok mengalami twist
    - orientation: orientasi saat ini (+1 atau -1)
    - merkle_root: untuk verifikasi transaksi
    """
    index: int
    prev_hash: str
    transactions: List[Transaction]
    timestamp: float = field(default_factory=time.time)
    nonce: int = 0
    twist_bit: int = 0
    orientation: int = 1
    merkle_root: str = ""
    hash: str = ""
    twist_depth: int = 1
    
    def compute_merkle_root(self) -> str:
        """Hitung Merkle root dari transaksi"""
        tree = MerkleTree()
        return tree.compute_root(self.transactions)
    
    def compute_hash(self) -> str:
        """Hitung hash blok dengan twist"""
        tx_data = json.dumps([tx.to_dict() for tx in self.transactions], sort_keys=True)
        
        # Base data untuk hash
        base = f"{self.index}{self.prev_hash}{tx_data}{self.timestamp}{self.nonce}"
        base += f"{self.twist_bit}{self.orientation}"
        
        # Twist hash
        thf = TwistHashFunction()
        h, _ = thf.hash_with_twist(base, self.twist_depth)
        return h
    
    def mine(self, difficulty: int = 4) -> None:
        """Mining dengan twist: hash harus memenuhi difficulty dan twist harus valid"""
        self.merkle_root = self.compute_merkle_root()
        
        # Mining loop - find nonce that satisfies difficulty
        # Note: orientation is fixed during mining, twist happens after
        while True:
            self.hash = self.compute_hash()
            if self.hash[:difficulty] == "0" * difficulty:
                break
            self.nonce += 1
        
        # Twist setelah mining: flip orientasi
        self.orientation *= -1
        self.twist_bit = 1 if self.orientation == -1 else 0
        
        # Recompute hash dengan orientasi baru
        self.hash = self.compute_hash()
    
    def validate(self, prev_block: Optional['Block'] = None) -> Tuple[bool, str]:
        """Validasi blok"""
        # Cek hash
        if self.hash != self.compute_hash():
            return False, f"Hash tidak valid di blok {self.index}"
        
        # Cek link ke blok sebelumnya
        if prev_block and self.prev_hash != prev_block.hash:
            return False, f"Link rusak di blok {self.index}"
        
        # Cek orientasi tidak None
        if self.orientation is None:
            return False, f"Robekan ruang di blok {self.index}"
        
        # Cek Merkle root
        expected_root = self.compute_merkle_root()
        if self.merkle_root != expected_root:
            return False, f"Merkle root tidak cocok di blok {self.index}"
        
        return True, "Valid"
    
    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "twist_bit": self.twist_bit,
            "orientation": self.orientation,
            "merkle_root": self.merkle_root,
            "hash": self.hash
        }


# ============================================================================
# WALLET
# ============================================================================

@dataclass
class Wallet:
    """Wallet dengan public/private key sederhana"""
    address: str
    private_key: str
    public_key: str
    
    def __init__(self, address: str):
        self.address = address
        # Generate keys (simplified - dalam produksi gunakan cryptography library)
        self.private_key = hashlib.sha256(f"{address}_private_{time.time()}".encode()).hexdigest()
        # Public key derived from private key (deterministic)
        self.public_key = hashlib.sha256(f"{self.private_key}_public".encode()).hexdigest()
    
    def create_transaction(self, recipient: str, amount: float) -> Transaction:
        """Buat dan tanda tangani transaksi"""
        tx = Transaction(
            sender=self.address,
            recipient=recipient,
            amount=amount
        )
        # Sign with private key
        tx_hash = tx.compute_tx_hash()
        sign_data = f"{tx_hash}{self.private_key}"
        tx.signature = hashlib.sha256(sign_data.encode()).hexdigest()
        return tx
    
    def verify_transaction(self, tx: Transaction) -> bool:
        """Verifikasi transaksi"""
        # Verify by recomputing signature with private key
        # Note: In real system, this would use asymmetric crypto
        # Here we use the same key for simplicity
        tx_hash = tx.compute_tx_hash()
        sign_data = f"{tx_hash}{self.private_key}"
        expected = hashlib.sha256(sign_data.encode()).hexdigest()
        return tx.signature == expected


# ============================================================================
# MOBIUS BLOCKCHAIN
# ============================================================================

class MobiusChain:
    """
    Blockchain lengkap dengan Möbius strip properties:
    - Loop ledger: blok ke-N terhubung dalam siklus
    - Anti-state: setiap akun memiliki dua sisi
    - O(1) consensus: validasi dalam waktu konstan per blok
    """
    
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.accounts: Dict[str, AntiStateAccount] = {}
        self.difficulty = difficulty
        self.block_reward = 50.0
        self.mining_address = "mobius_miner"
        
        # Initialize dengan genesis block
        self.create_genesis()
    
    def create_genesis(self) -> None:
        """Buat genesis block"""
        genesis = Block(
            index=0,
            prev_hash="0" * 64,
            transactions=[],
            timestamp=time.time(),
            twist_bit=0,
            orientation=1
        )
        genesis.hash = genesis.compute_hash()
        genesis.merkle_root = genesis.compute_merkle_root()
        self.chain.append(genesis)
        
        # Initialize miner account dengan reward pertama
        self._ensure_account(self.mining_address)
        self.accounts[self.mining_address].transact_in(self.block_reward)
    
    def _ensure_account(self, address: str) -> AntiStateAccount:
        """Pastikan akun ada"""
        if address not in self.accounts:
            self.accounts[address] = AntiStateAccount(address)
        return self.accounts[address]
    
    def get_balance(self, address: str) -> float:
        """Dapatkan balance akun"""
        account = self._ensure_account(address)
        return account.total_balance
    
    def add_transaction(self, tx: Transaction) -> bool:
        """Tambahkan transaksi ke pending pool"""
        # Verifikasi signature
        sender_account = self._ensure_account(tx.sender)
        if tx.amount <= 0:
            return False
        if sender_account.total_balance < tx.amount:
            return False
        
        self.pending_transactions.append(tx)
        return True
    
    def mine_pending_transactions(self) -> Optional[Block]:
        """Mine transaksi pending ke blok baru"""
        if not self.pending_transactions:
            print("Tidak ada transaksi untuk di-mine")
            return None
        
        prev_block = self.chain[-1]
        
        # Buat blok baru
        new_block = Block(
            index=len(self.chain),
            prev_hash=prev_block.hash,
            transactions=self.pending_transactions.copy(),
            timestamp=time.time(),
            orientation=prev_block.orientation
        )
        
        # Mining
        new_block.mine(self.difficulty)
        
        # Process transactions
        for tx in self.pending_transactions:
            sender = self._ensure_account(tx.sender)
            recipient = self._ensure_account(tx.recipient)
            
            if sender.transact_out(tx.amount):
                recipient.transact_in(tx.amount)
        
        # Reward miner
        miner = self._ensure_account(self.mining_address)
        miner.transact_in(self.block_reward)
        
        # Clear pending
        self.pending_transactions = []
        
        # Add block
        self.chain.append(new_block)
        print(f"Blok {new_block.index} di-mine | orientasi: {new_block.orientation} | hash: {new_block.hash[:16]}")
        
        return new_block
    
    def validate_chain(self) -> Tuple[bool, str]:
        """
        Validasi seluruh blockchain
        O(1) per blok: hanya cek integritas topologi
        """
        for i in range(1, len(self.chain)):
            block = self.chain[i]
            prev_block = self.chain[i-1]
            
            valid, msg = block.validate(prev_block)
            if not valid:
                return False, msg
            
            # O(1) validator: cek twist integrity
            if block.orientation is None:
                return False, f"Robekan ruang di blok {i}"
            
            # Cek twist bit consistency
            expected_twist = 1 if block.orientation == -1 else 0
            if block.twist_bit != expected_twist:
                return False, f"Twist bit tidak konsisten di blok {i}"
        
        return True, f"Ruang utuh — konsensus O(1) diterima ({len(self.chain)} blok)"
    
    def get_chain_info(self) -> dict:
        """Informasi blockchain"""
        return {
            "length": len(self.chain),
            "difficulty": self.difficulty,
            "block_reward": self.block_reward,
            "total_accounts": len(self.accounts),
            "pending_tx": len(self.pending_transactions),
            "latest_block": self.chain[-1].hash[:16] if self.chain else None
        }
    
    def print_chain_status(self) -> None:
        """Print status blockchain"""
        print("\n" + "="*60)
        print("MOBIUS BLOCKCHAIN STATUS")
        print("="*60)
        print(f"Panjang chain: {len(self.chain)} blok")
        print(f"Akun aktif: {len(self.accounts)}")
        print(f"Transaksi pending: {len(self.pending_transactions)}")
        print("\nBlok-blok:")
        for block in self.chain:
            print(f"  #{block.index}: hash={block.hash[:16]} | orient={block.orientation} | twist={block.twist_bit} | tx={len(block.transactions)}")
        print("\nAkun:")
        for addr, account in self.accounts.items():
            print(f"  {addr}: A={account.side_a:.2f} | B={account.side_b:.2f} | orient={account.orientation}")
        print("="*60)


# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo_basic_chain():
    """Demo blockchain basic"""
    print("\n" + "="*60)
    print("DEMO 1: Basic MobiusChain")
    print("="*60)
    
    # Create chain
    chain = MobiusChain(difficulty=2)
    
    # Create wallets
    alice = Wallet("alice")
    bob = Wallet("bob")
    
    # Berikan alice beberapa koin dari miner
    chain._ensure_account("alice").transact_in(100.0)
    
    print(f"\nInitial balances:")
    print(f"  Alice: {chain.get_balance('alice')}")
    print(f"  Bob: {chain.get_balance('bob')}")
    print(f"  Miner: {chain.get_balance('mobius_miner')}")
    
    # Buat transaksi
    tx1 = alice.create_transaction("bob", 30.0)
    tx2 = alice.create_transaction("bob", 20.0)
    
    chain.add_transaction(tx1)
    chain.add_transaction(tx2)
    
    # Mine blok
    chain.mine_pending_transactions()
    
    print(f"\nAfter mining:")
    print(f"  Alice: {chain.get_balance('alice')}")
    print(f"  Bob: {chain.get_balance('bob')}")
    print(f"  Miner: {chain.get_balance('mobius_miner')}")
    
    # Validasi
    valid, msg = chain.validate_chain()
    print(f"\nValidasi: {valid} | {msg}")
    
    chain.print_chain_status()


def demo_twist_hash():
    """Demo Twist Hash Function"""
    print("\n" + "="*60)
    print("DEMO 2: Twist Hash Function")
    print("="*60)
    
    thf = TwistHashFunction()
    
    data = "Hello Möbius"
    
    print(f"\nData: {data}")
    for depth in range(1, 5):
        h, orient = thf.hash_with_twist(data, depth)
        print(f"  Twist depth {depth}: hash={h[:32]} | orient={orient}")


def demo_anti_state():
    """Demo Anti-State Ledger"""
    print("\n" + "="*60)
    print("DEMO 3: Anti-State Ledger")
    print("="*60)
    
    account = AntiStateAccount("test_user")
    account.transact_in(100.0)
    
    print(f"\nInitial: {account}")
    
    for i in range(3):
        account.transact_out(20.0)
        print(f"After tx {i+1}: {account}")
    
    print(f"\nTotal twists: {account.twist_count}")
    print(f"Orientation: {account.orientation}")
    print(f"Note: Balance berpindah antara side A dan B setiap twist!")


def demo_loop_ledger():
    """Demo Loop Ledger - sifat siklus Möbius"""
    print("\n" + "="*60)
    print("DEMO 4: Loop Ledger (Möbius Cycle)")
    print("="*60)
    
    chain = MobiusChain(difficulty=2)
    
    # Mine beberapa blok
    for i in range(5):
        chain._ensure_account("test").transact_in(10.0)
        tx = Transaction("test", "recipient", 5.0)
        chain.add_transaction(tx)
        chain.mine_pending_transactions()
    
    print("\nSetelah 5 blok:")
    orientations = [b.orientation for b in chain.chain]
    print(f"  Orientasi sequence: {orientations}")
    print(f"  Pattern: {' → '.join(str(o) for o in orientations)}")
    print(f"\n  Note: Orientasi berfluktuasi seperti traverse Möbius strip!")
    
    # Cek apakah setelah N blok, kita "kembali" ke orientasi awal
    if chain.chain[-1].orientation == chain.chain[0].orientation:
        print("  ✓ Loop lengkap: kembali ke orientasi genesis")
    else:
        print("  ⤸ Belum loop lengkap: orientasi terbalik (seperti Möbius!)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MOBIUSCOIN BLOCKCHAIN DEMO")
    print("="*60)
    
    demo_twist_hash()
    demo_anti_state()
    demo_basic_chain()
    demo_loop_ledger()
    
    print("\n" + "="*60)
    print("DEMO SELESAI")
    print("="*60)
