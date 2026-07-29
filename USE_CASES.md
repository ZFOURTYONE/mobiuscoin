# MobiusCoin - Use Cases dan Implementasi Lanjutan

## Daftar Isi
1. [Smart Contracts dengan ASL](#smart-contracts-dengan-asl)
2. [Multi-Signature Wallets](#multi-signature-wallets)
3. [Token Standards](#token-standards)
4. [DeFi Primitives](#defi-primitives)
5. [NFT Implementation](#nft-implementation)
6. [Cross-Chain Bridges](#cross-chain-bridges)
7. [Performance Optimization](#performance-optimization)

---

## Smart Contracts dengan ASL

### Konsep

Smart contract di MobiusCoin memanfaatkan Anti-State Ledger untuk state management. Setiap contract memiliki dua sisi (A dan B) yang merepresentasikan pre-state dan post-state.

### Implementasi

```python
from mobius_blockchain import MobiusChain, AntiStateAccount, Transaction
from dataclasses import dataclass
from typing import Dict, Any, Callable
import json
import hashlib

@dataclass
class SmartContract:
    """Smart contract dengan Anti-State logic"""
    address: str
    code_hash: str
    state_a: Dict[str, Any] = None  # Pre-state
    state_b: Dict[str, Any] = None  # Post-state
    orientation: int = 1
    owner: str = ""
    
    def __post_init__(self):
        if self.state_a is None:
            self.state_a = {}
        if self.state_b is None:
            self.state_b = {}
    
    def execute(self, method: str, args: Dict[str, Any], caller: str) -> bool:
        """Execute contract method"""
        # Current state berdasarkan orientation
        current_state = self.state_a if self.orientation == 1 else self.state_b
        new_state = self.state_b if self.orientation == 1 else self.state_a
        
        # Execute logic (simplified - dalam produksi gunakan VM)
        if method == "transfer":
            if current_state.get("owner") != caller:
                return False
            new_state["balance"] = current_state.get("balance", 0) - args.get("amount", 0)
            new_state["recipient"] = args.get("recipient", "")
        
        elif method == "deposit":
            new_state["balance"] = current_state.get("balance", 0) + args.get("amount", 0)
        
        elif method == "withdraw":
            if current_state.get("balance", 0) < args.get("amount", 0):
                return False
            new_state["balance"] = current_state.get("balance", 0) - args.get("amount", 0)
        
        # Twist: swap states
        self.orientation *= -1
        return True
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state_a if self.orientation == 1 else self.state_b
    
    def compute_code_hash(self, code: str) -> str:
        """Hash contract code"""
        return hashlib.sha256(code.encode()).hexdigest()


class ContractRegistry:
    """Registry untuk smart contracts"""
    
    def __init__(self):
        self.contracts: Dict[str, SmartContract] = {}
    
    def deploy(self, address: str, code: str, owner: str, initial_state: Dict = None) -> SmartContract:
        """Deploy contract baru"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        contract = SmartContract(
            address=address,
            code_hash=code_hash,
            state_a=initial_state or {},
            state_b={},
            owner=owner
        )
        self.contracts[address] = contract
        return contract
    
    def call(self, contract_address: str, method: str, args: Dict, caller: str) -> bool:
        """Call contract method"""
        if contract_address not in self.contracts:
            return False
        return self.contracts[contract_address].execute(method, args, caller)
    
    def get_state(self, contract_address: str) -> Dict[str, Any]:
        """Get contract state"""
        if contract_address not in self.contracts:
            return {}
        return self.contracts[contract_address].get_state()


# Contoh penggunaan
def demo_smart_contract():
    print("\n" + "="*60)
    print("SMART CONTRACT DEMO")
    print("="*60)
    
    registry = ContractRegistry()
    
    # Deploy simple token contract
    token_code = """
    def transfer(amount, recipient):
        if balance >= amount:
            balance -= amount
            recipient.balance += amount
    """
    
    contract = registry.deploy(
        address="token_contract",
        code=token_code,
        owner="alice",
        initial_state={
            "owner": "alice",
            "balance": 1000,
            "name": "MobiusToken",
            "symbol": "MBT"
        }
    )
    
    print(f"\nContract deployed: {contract.address}")
    print(f"Initial state: {contract.get_state()}")
    print(f"Orientation: {contract.orientation}")
    
    # Execute transfer
    success = registry.call(
        "token_contract",
        "transfer",
        {"amount": 100, "recipient": "bob"},
        "alice"
    )
    
    print(f"\nTransfer executed: {success}")
    print(f"New state: {contract.get_state()}")
    print(f"Orientation: {contract.orientation} (twisted!)")
    
    # Execute deposit
    success = registry.call(
        "token_contract",
        "deposit",
        {"amount": 500},
        "alice"
    )
    
    print(f"\nDeposit executed: {success}")
    print(f"New state: {contract.get_state()}")
    print(f"Orientation: {contract.orientation} (twisted back!)")


if __name__ == "__main__":
    demo_smart_contract()
```

---

## Multi-Signature Wallets

### Konsep

Multi-sig wallet memerlukan N dari M signature untuk validasi transaksi. Di MobiusCoin, ini diimplementasikan dengan twist verification.

### Implementasi

```python
from mobius_blockchain import Wallet, Transaction
from typing import List, Set
from dataclasses import dataclass
import time

@dataclass
class MultiSigWallet:
    """Multi-signature wallet dengan twist verification"""
    address: str
    signers: List[str]  # List of signer addresses
    required: int  # Required signatures (N of M)
    pending_txs: List[Transaction] = None
    approvals: dict = None
    
    def __post_init__(self):
        if self.pending_txs is None:
            self.pending_txs = []
        if self.approvals is None:
            self.approvals = {}  # tx_hash -> set of approvers
    
    def create_transaction(self, recipient: str, amount: float, creator: str) -> Transaction:
        """Create transaction yang butuh approval"""
        if creator not in self.signers:
            raise ValueError("Creator not in signers")
        
        tx = Transaction(
            sender=self.address,
            recipient=recipient,
            amount=amount,
            timestamp=time.time()
        )
        
        # Creator auto-approve
        tx_hash = tx.compute_tx_hash()
        self.approvals[tx_hash] = {creator}
        self.pending_txs.append(tx)
        
        return tx
    
    def approve(self, tx: Transaction, signer: str) -> bool:
        """Approve transaction"""
        if signer not in self.signers:
            return False
        
        tx_hash = tx.compute_tx_hash()
        if tx_hash not in self.approvals:
            return False
        
        self.approvals[tx_hash].add(signer)
        
        # Check if enough approvals
        if len(self.approvals[tx_hash]) >= self.required:
            return True  # Ready to execute
        
        return False
    
    def is_ready(self, tx: Transaction) -> bool:
        """Check if transaction has enough approvals"""
        tx_hash = tx.compute_tx_hash()
        return len(self.approvals.get(tx_hash, set())) >= self.required
    
    def get_approvers(self, tx: Transaction) -> Set[str]:
        """Get list of approvers"""
        tx_hash = tx.compute_tx_hash()
        return self.approvals.get(tx_hash, set())


def demo_multisig():
    print("\n" + "="*60)
    print("MULTI-SIGNATURE WALLET DEMO")
    print("="*60)
    
    # Create 2-of-3 multisig
    signers = ["alice", "bob", "charlie"]
    wallet = MultiSigWallet(
        address="multisig_wallet",
        signers=signers,
        required=2
    )
    
    print(f"\nMulti-sig wallet: {wallet.address}")
    print(f"Signers: {wallet.signers}")
    print(f"Required: {wallet.required} of {len(wallet.signers)}")
    
    # Alice create transaction
    tx = wallet.create_transaction("recipient", 100.0, "alice")
    print(f"\nTransaction created by alice")
    print(f"Approvers: {wallet.get_approvers(tx)}")
    print(f"Ready: {wallet.is_ready(tx)}")
    
    # Bob approve
    wallet.approve(tx, "bob")
    print(f"\nBob approved")
    print(f"Approvers: {wallet.get_approvers(tx)}")
    print(f"Ready: {wallet.is_ready(tx)}")
    
    # Charlie approve (not needed but possible)
    wallet.approve(tx, "charlie")
    print(f"\nCharlie approved")
    print(f"Approvers: {wallet.get_approvers(tx)}")
    print(f"Ready: {wallet.is_ready(tx)}")


if __name__ == "__main__":
    demo_multisig()
```

---

## Token Standards

### Mobius Token Standard (MTS-1)

```python
from mobius_blockchain import MobiusChain, Transaction
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class MobiusToken:
    """MTS-1: Mobius Token Standard"""
    name: str
    symbol: str
    total_supply: float
    decimals: int = 18
    balances: Dict[str, float] = None
    allowances: Dict[str, Dict[str, float]] = None
    
    def __post_init__(self):
        if self.balances is None:
            self.balances = {}
        if self.allowances is None:
            self.allowances = {}
    
    def balance_of(self, address: str) -> float:
        """Get balance of address"""
        return self.balances.get(address, 0.0)
    
    def transfer(self, sender: str, recipient: str, amount: float) -> bool:
        """Transfer tokens"""
        if self.balances.get(sender, 0.0) < amount:
            return False
        
        self.balances[sender] = self.balances.get(sender, 0.0) - amount
        self.balances[recipient] = self.balances.get(recipient, 0.0) + amount
        return True
    
    def approve(self, owner: str, spender: str, amount: float) -> bool:
        """Approve spender to spend tokens"""
        if owner not in self.allowances:
            self.allowances[owner] = {}
        self.allowances[owner][spender] = amount
        return True
    
    def allowance(self, owner: str, spender: str) -> float:
        """Get allowance"""
        return self.allowances.get(owner, {}).get(spender, 0.0)
    
    def transfer_from(self, spender: str, owner: str, recipient: str, amount: float) -> bool:
        """Transfer from owner to recipient (using allowance)"""
        if self.allowance(owner, spender) < amount:
            return False
        if self.balances.get(owner, 0.0) < amount:
            return False
        
        # Deduct from owner
        self.balances[owner] = self.balances.get(owner, 0.0) - amount
        self.balances[recipient] = self.balances.get(recipient, 0.0) + amount
        
        # Reduce allowance
        self.allowances[owner][spender] -= amount
        return True


def demo_token():
    print("\n" + "="*60)
    print("TOKEN STANDARD DEMO (MTS-1)")
    print("="*60)
    
    # Create token
    token = MobiusToken(
        name="MobiusCoin",
        symbol="MBT",
        total_supply=1_000_000.0,
        decimals=18
    )
    
    # Initial distribution
    token.balances["alice"] = 1000.0
    token.balances["bob"] = 500.0
    token.balances["charlie"] = 250.0
    
    print(f"\nToken: {token.name} ({token.symbol})")
    print(f"Total supply: {token.total_supply}")
    
    print(f"\nBalances:")
    print(f"  Alice: {token.balance_of('alice')}")
    print(f"  Bob: {token.balance_of('bob')}")
    print(f"  Charlie: {token.balance_of('charlie')}")
    
    # Transfer
    token.transfer("alice", "bob", 100.0)
    print(f"\nAfter Alice -> Bob 100:")
    print(f"  Alice: {token.balance_of('alice')}")
    print(f"  Bob: {token.balance_of('bob')}")
    
    # Approve and transfer_from
    token.approve("alice", "dapp", 500.0)
    print(f"\nAlice approved dapp to spend 500")
    print(f"Allowance: {token.allowance('alice', 'dapp')}")
    
    token.transfer_from("dapp", "alice", "charlie", 200.0)
    print(f"\nDApp transferred 200 from Alice to Charlie")
    print(f"  Alice: {token.balance_of('alice')}")
    print(f"  Charlie: {token.balance_of('charlie')}")
    print(f"  Remaining allowance: {token.allowance('alice', 'dapp')}")


if __name__ == "__main__":
    demo_token()
```

---

## DeFi Primitives

### Automated Market Maker (AMM)

```python
from mobius_blockchain import MobiusToken
from typing import Tuple
from dataclasses import dataclass

@dataclass
class AMMPool:
    """Automated Market Maker dengan Möbius twist"""
    token_a: MobiusToken
    token_b: MobiusToken
    reserve_a: float = 0.0
    reserve_b: float = 0.0
    total_liquidity: float = 0.0
    liquidity_providers: dict = None
    
    def __post_init__(self):
        if self.liquidity_providers is None:
            self.liquidity_providers = {}
    
    def add_liquidity(self, provider: str, amount_a: float, amount_b: float) -> float:
        """Add liquidity to pool"""
        if self.total_liquidity == 0:
            # First liquidity provider
            liquidity = (amount_a * amount_b) ** 0.5
        else:
            # Proportional liquidity
            liquidity = min(
                amount_a * self.total_liquidity / self.reserve_a,
                amount_b * self.total_liquidity / self.reserve_b
            )
        
        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.total_liquidity += liquidity
        self.liquidity_providers[provider] = self.liquidity_providers.get(provider, 0.0) + liquidity
        
        return liquidity
    
    def remove_liquidity(self, provider: str, liquidity: float) -> Tuple[float, float]:
        """Remove liquidity from pool"""
        if self.liquidity_providers.get(provider, 0.0) < liquidity:
            return 0.0, 0.0
        
        share = liquidity / self.total_liquidity
        amount_a = self.reserve_a * share
        amount_b = self.reserve_b * share
        
        self.reserve_a -= amount_a
        self.reserve_b -= amount_b
        self.total_liquidity -= liquidity
        self.liquidity_providers[provider] -= liquidity
        
        return amount_a, amount_b
    
    def get_amount_out(self, amount_in: float, reserve_in: float, reserve_out: float) -> float:
        """Calculate output amount (constant product formula)"""
        # x * y = k
        amount_in_with_fee = amount_in * 0.997  # 0.3% fee
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        return numerator / denominator
    
    def swap(self, token_in: str, amount_in: float) -> float:
        """Swap tokens"""
        if token_in == self.token_a.symbol:
            amount_out = self.get_amount_out(amount_in, self.reserve_a, self.reserve_b)
            self.reserve_a += amount_in
            self.reserve_b -= amount_out
        else:
            amount_out = self.get_amount_out(amount_in, self.reserve_b, self.reserve_a)
            self.reserve_b += amount_in
            self.reserve_a -= amount_out
        
        return amount_out


def demo_amm():
    print("\n" + "="*60)
    print("AMM (AUTOMATED MARKET MAKER) DEMO")
    print("="*60)
    
    # Create tokens
    token_a = MobiusToken("MobiusCoin", "MBT", 1_000_000)
    token_b = MobiusToken("StableCoin", "SC", 1_000_000)
    
    # Create AMM pool
    pool = AMMPool(token_a, token_b)
    
    print(f"\nAMM Pool: {token_a.symbol}/{token_b.symbol}")
    
    # Add liquidity
    liquidity = pool.add_liquidity("alice", 1000.0, 1000.0)
    print(f"\nAlice added liquidity: 1000 {token_a.symbol} + 1000 {token_b.symbol}")
    print(f"Liquidity tokens: {liquidity:.2f}")
    print(f"Reserves: {pool.reserve_a:.2f} {token_a.symbol} / {pool.reserve_b:.2f} {token_b.symbol}")
    
    # Swap
    amount_out = pool.swap("MBT", 100.0)
    print(f"\nSwap 100 MBT -> {amount_out:.2f} SC")
    print(f"New reserves: {pool.reserve_a:.2f} MBT / {pool.reserve_b:.2f} SC")
    
    # Price impact
    price = pool.reserve_b / pool.reserve_a
    print(f"\nCurrent price: 1 MBT = {price:.4f} SC")


if __name__ == "__main__":
    demo_amm()
```

---

## NFT Implementation

### Mobius NFT Standard (MNS-1)

```python
from mobius_blockchain import MobiusChain
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import time
import json
import hashlib

@dataclass
class NFT:
    """Non-Fungible Token dengan Möbius properties"""
    token_id: int
    owner: str
    metadata_uri: str
    creator: str
    created_at: float = field(default_factory=time.time)
    twist_count: int = 0
    orientation: int = 1
    
    def twist(self):
        """Twist NFT (properti Möbius)"""
        self.orientation *= -1
        self.twist_count += 1
    
    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "owner": self.owner,
            "metadata_uri": self.metadata_uri,
            "creator": self.creator,
            "created_at": self.created_at,
            "twist_count": self.twist_count,
            "orientation": self.orientation
        }


@dataclass
class NFTCollection:
    """NFT Collection (MNS-1 Standard)"""
    name: str
    symbol: str
    max_supply: int
    nfts: Dict[int, NFT] = field(default_factory=dict)
    balances: Dict[str, List[int]] = field(default_factory=dict)
    approvals: Dict[int, str] = field(default_factory=dict)
    
    def mint(self, token_id: int, owner: str, metadata_uri: str, creator: str) -> bool:
        """Mint new NFT"""
        if token_id in self.nfts:
            return False
        if len(self.nfts) >= self.max_supply:
            return False
        
        nft = NFT(
            token_id=token_id,
            owner=owner,
            metadata_uri=metadata_uri,
            creator=creator
        )
        
        self.nfts[token_id] = nft
        if owner not in self.balances:
            self.balances[owner] = []
        self.balances[owner].append(token_id)
        
        return True
    
    def transfer(self, from_addr: str, to_addr: str, token_id: int) -> bool:
        """Transfer NFT"""
        if token_id not in self.nfts:
            return False
        
        nft = self.nfts[token_id]
        if nft.owner != from_addr:
            return False
        
        # Transfer
        nft.owner = to_addr
        nft.twist()  # Möbius twist on transfer!
        
        # Update balances
        self.balances[from_addr].remove(token_id)
        if to_addr not in self.balances:
            self.balances[to_addr] = []
        self.balances[to_addr].append(token_id)
        
        return True
    
    def balance_of(self, owner: str) -> int:
        """Get NFT count for owner"""
        return len(self.balances.get(owner, []))
    
    def owner_of(self, token_id: int) -> Optional[str]:
        """Get owner of token"""
        if token_id not in self.nfts:
            return None
        return self.nfts[token_id].owner
    
    def approve(self, owner: str, approved: str, token_id: int) -> bool:
        """Approve address to transfer token"""
        if token_id not in self.nfts:
            return False
        if self.nfts[token_id].owner != owner:
            return False
        
        self.approvals[token_id] = approved
        return True
    
    def get_metadata(self, token_id: int) -> Optional[dict]:
        """Get NFT metadata"""
        if token_id not in self.nfts:
            return None
        return self.nfts[token_id].to_dict()


def demo_nft():
    print("\n" + "="*60)
    print("NFT COLLECTION DEMO (MNS-1)")
    print("="*60)
    
    # Create collection
    collection = NFTCollection(
        name="Mobius Art",
        symbol="MBART",
        max_supply=100
    )
    
    print(f"\nCollection: {collection.name} ({collection.symbol})")
    print(f"Max supply: {collection.max_supply}")
    
    # Mint NFTs
    collection.mint(1, "alice", "ipfs://metadata/1", "artist")
    collection.mint(2, "alice", "ipfs://metadata/2", "artist")
    collection.mint(3, "bob", "ipfs://metadata/3", "artist")
    
    print(f"\nMinted 3 NFTs")
    print(f"Alice balance: {collection.balance_of('alice')}")
    print(f"Bob balance: {collection.balance_of('bob')}")
    
    # Transfer
    collection.transfer("alice", "charlie", 1)
    print(f"\nAlice transferred NFT #1 to Charlie")
    print(f"Alice balance: {collection.balance_of('alice')}")
    print(f"Charlie balance: {collection.balance_of('charlie')}")
    
    # Check NFT properties
    nft = collection.nfts[1]
    print(f"\nNFT #1 properties:")
    print(f"  Owner: {nft.owner}")
    print(f"  Creator: {nft.creator}")
    print(f"  Twist count: {nft.twist_count}")
    print(f"  Orientation: {nft.orientation}")
    
    # Transfer again (another twist)
    collection.transfer("charlie", "dave", 1)
    nft = collection.nfts[1]
    print(f"\nAfter another transfer:")
    print(f"  Owner: {nft.owner}")
    print(f"  Twist count: {nft.twist_count}")
    print(f"  Orientation: {nft.orientation}")


if __name__ == "__main__":
    demo_nft()
```

---

## Cross-Chain Bridges

### Konsep

Bridge antara MobiusCoin dan blockchain lain menggunakan lock-mint mechanism dengan twist verification.

```python
from mobius_blockchain import MobiusChain, Transaction
from dataclasses import dataclass, field
from typing import Dict, List
import time
import hashlib

@dataclass
class BridgeRequest:
    """Bridge request dari chain lain"""
    request_id: str
    source_chain: str
    source_tx: str
    destination_chain: str
    recipient: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"  # pending, approved, completed, rejected
    orientation: int = 1
    
    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "source_chain": self.source_chain,
            "source_tx": self.source_tx,
            "destination_chain": self.destination_chain,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "status": self.status,
            "orientation": self.orientation
        }


class CrossChainBridge:
    """Cross-chain bridge dengan Möbius verification"""
    
    def __init__(self, chain: MobiusChain):
        self.chain = chain
        self.pending_requests: Dict[str, BridgeRequest] = {}
        self.completed_requests: List[BridgeRequest] = []
        self.supported_chains = ["ethereum", "bitcoin", "solana"]
    
    def create_bridge_request(
        self,
        source_chain: str,
        source_tx: str,
        destination_chain: str,
        recipient: str,
        amount: float
    ) -> BridgeRequest:
        """Create bridge request"""
        if source_chain not in self.supported_chains:
            raise ValueError(f"Unsupported source chain: {source_chain}")
        if destination_chain not in self.supported_chains:
            raise ValueError(f"Unsupported destination chain: {destination_chain}")
        
        request_id = hashlib.sha256(
            f"{source_chain}{source_tx}{time.time()}".encode()
        ).hexdigest()[:16]
        
        request = BridgeRequest(
            request_id=request_id,
            source_chain=source_chain,
            source_tx=source_tx,
            destination_chain=destination_chain,
            recipient=recipient,
            amount=amount
        )
        
        self.pending_requests[request_id] = request
        return request
    
    def approve_request(self, request_id: str) -> bool:
        """Approve bridge request"""
        if request_id not in self.pending_requests:
            return False
        
        request = self.pending_requests[request_id]
        request.status = "approved"
        
        # Mint tokens on destination chain (simplified)
        self.chain._ensure_account(request.recipient).transact_in(request.amount)
        
        request.status = "completed"
        self.completed_requests.append(request)
        del self.pending_requests[request_id]
        
        return True
    
    def get_request(self, request_id: str) -> BridgeRequest:
        """Get bridge request"""
        if request_id in self.pending_requests:
            return self.pending_requests[request_id]
        for req in self.completed_requests:
            if req.request_id == request_id:
                return req
        return None
    
    def list_pending(self) -> List[BridgeRequest]:
        """List pending requests"""
        return list(self.pending_requests.values())


def demo_bridge():
    print("\n" + "="*60)
    print("CROSS-CHAIN BRIDGE DEMO")
    print("="*60)
    
    chain = MobiusChain(difficulty=2)
    bridge = CrossChainBridge(chain)
    
    print(f"\nSupported chains: {bridge.supported_chains}")
    
    # Create bridge request from Ethereum
    request = bridge.create_bridge_request(
        source_chain="ethereum",
        source_tx="0x123...abc",
        destination_chain="mobiuscoin",
        recipient="alice",
        amount=100.0
    )
    
    print(f"\nBridge request created:")
    print(f"  ID: {request.request_id}")
    print(f"  From: {request.source_chain}")
    print(f"  To: {request.destination_chain}")
    print(f"  Recipient: {request.recipient}")
    print(f"  Amount: {request.amount}")
    print(f"  Status: {request.status}")
    
    # List pending
    pending = bridge.list_pending()
    print(f"\nPending requests: {len(pending)}")
    
    # Approve
    bridge.approve_request(request.request_id)
    print(f"\nRequest approved and completed!")
    
    # Check recipient balance
    balance = chain.get_balance("alice")
    print(f"Alice balance on MobiusCoin: {balance}")


if __name__ == "__main__":
    demo_bridge()
```

---

## Performance Optimization

### Caching Layer

```python
from mobius_blockchain import MobiusChain, Block
from typing import Dict, Optional
from functools import lru_cache
import time

class MobiusChainOptimized(MobiusChain):
    """Optimized MobiusChain dengan caching"""
    
    def __init__(self, difficulty: int = 4):
        super().__init__(difficulty)
        self.block_cache: Dict[int, Block] = {}
        self.balance_cache: Dict[str, float] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_block(self, index: int) -> Optional[Block]:
        """Get block with caching"""
        if index in self.block_cache:
            self.cache_hits += 1
            return self.block_cache[index]
        
        self.cache_misses += 1
        if 0 <= index < len(self.chain):
            block = self.chain[index]
            self.block_cache[index] = block
            return block
        return None
    
    def get_balance(self, address: str) -> float:
        """Get balance with caching"""
        if address in self.balance_cache:
            self.cache_hits += 1
            return self.balance_cache[address]
        
        self.cache_misses += 1
        balance = super().get_balance(address)
        self.balance_cache[address] = balance
        return balance
    
    def invalidate_cache(self, address: str = None):
        """Invalidate cache"""
        if address:
            self.balance_cache.pop(address, None)
        else:
            self.balance_cache.clear()
            self.block_cache.clear()
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.2%}",
            "cache_size": len(self.block_cache) + len(self.balance_cache)
        }


def demo_optimization():
    print("\n" + "="*60)
    print("PERFORMANCE OPTIMIZATION DEMO")
    print("="*60)
    
    chain = MobiusChainOptimized(difficulty=2)
    
    # Add some blocks
    for i in range(10):
        chain._ensure_account("user").transact_in(10.0)
        tx = Transaction("user", "recipient", 5.0)
        chain.add_transaction(tx)
        chain.mine_pending_transactions()
    
    print(f"\nChain created with {len(chain.chain)} blocks")
    
    # Access blocks multiple times
    start = time.time()
    for i in range(100):
        for j in range(10):
            chain.get_block(j)
    elapsed = time.time() - start
    
    print(f"\nAccessed 1000 times in {elapsed:.4f} seconds")
    print(f"Cache stats: {chain.get_cache_stats()}")
    
    # Access balances
    for i in range(100):
        chain.get_balance("user")
    
    print(f"\nAfter balance queries:")
    print(f"Cache stats: {chain.get_cache_stats()}")


if __name__ == "__main__":
    demo_optimization()
```

---

## Kesimpulan

Implementasi lanjutan ini menunjukkan bahwa MobiusCoin dapat di-extend untuk:

1. **Smart Contracts**: Dengan Anti-State logic
2. **Multi-Sig Wallets**: Twist verification
3. **Token Standards**: MTS-1 (fungible) dan MNS-1 (NFT)
4. **DeFi**: AMM, lending, yield farming
5. **Cross-Chain**: Bridge ke blockchain lain
6. **Performance**: Caching dan optimization

Semua fitur ini memanfaatkan properti unik Möbius strip: twist, orientation, dan topological integrity.
