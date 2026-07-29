#!/usr/bin/env python3
"""
MobiusCoin Blockchain Explorer - Backend API
============================================
Full-featured blockchain explorer with REST API
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import time

# Add parent directory to import blockchain
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mobius_blockchain import MobiusChain, Wallet, Transaction, Block

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize blockchain
blockchain = MobiusChain(difficulty=2)

# Database setup
DB_PATH = 'explorer.db'

def init_db():
    """Initialize SQLite database for indexing"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Blocks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY,
            hash TEXT UNIQUE NOT NULL,
            prev_hash TEXT NOT NULL,
            timestamp REAL NOT NULL,
            nonce INTEGER NOT NULL,
            orientation INTEGER NOT NULL,
            twist_bit INTEGER NOT NULL,
            merkle_root TEXT NOT NULL,
            num_transactions INTEGER NOT NULL
        )
    ''')
    
    # Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            tx_hash TEXT UNIQUE NOT NULL,
            block_id INTEGER,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp REAL NOT NULL,
            signature TEXT,
            nonce INTEGER,
            FOREIGN KEY (block_id) REFERENCES blocks (id)
        )
    ''')
    
    # Accounts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            address TEXT PRIMARY KEY,
            side_a REAL NOT NULL,
            side_b REAL NOT NULL,
            orientation INTEGER NOT NULL,
            twist_count INTEGER NOT NULL,
            first_seen REAL NOT NULL,
            last_seen REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def index_blockchain():
    """Index entire blockchain into database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for block in blockchain.chain:
        # Index block
        c.execute('''
            INSERT OR REPLACE INTO blocks 
            (id, hash, prev_hash, timestamp, nonce, orientation, twist_bit, merkle_root, num_transactions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            block.index,
            block.hash,
            block.prev_hash,
            block.timestamp,
            block.nonce,
            block.orientation,
            block.twist_bit,
            block.merkle_root,
            len(block.transactions)
        ))
        
        # Index transactions
        for tx in block.transactions:
            tx_hash = tx.compute_tx_hash()
            c.execute('''
                INSERT OR REPLACE INTO transactions
                (tx_hash, block_id, sender, recipient, amount, timestamp, signature, nonce)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx_hash,
                block.index,
                tx.sender,
                tx.recipient,
                tx.amount,
                tx.timestamp,
                tx.signature,
                tx.nonce
            ))
            
            # Update accounts
            for addr in [tx.sender, tx.recipient]:
                if addr in blockchain.accounts:
                    account = blockchain.accounts[addr]
                    now = time.time()
                    c.execute('''
                        INSERT OR REPLACE INTO accounts
                        (address, side_a, side_b, orientation, twist_count, first_seen, last_seen)
                        VALUES (?, ?, ?, ?, ?, 
                            COALESCE((SELECT first_seen FROM accounts WHERE address = ?), ?),
                            ?)
                    ''', (
                        addr,
                        account.side_a,
                        account.side_b,
                        account.orientation,
                        account.twist_count,
                        addr,
                        now,
                        now
                    ))
    
    conn.commit()
    conn.close()

# ============================================================================
# STATIC FILES
# ============================================================================

@app.route('/')
def index():
    """Serve main page"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files"""
    return send_from_directory('static', path)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/status')
def get_status():
    """Get blockchain status"""
    return jsonify({
        'chain_length': len(blockchain.chain),
        'total_accounts': len(blockchain.accounts),
        'pending_transactions': len(blockchain.pending_transactions),
        'difficulty': blockchain.difficulty,
        'block_reward': blockchain.block_reward,
        'latest_block': {
            'index': blockchain.chain[-1].index,
            'hash': blockchain.chain[-1].hash,
            'timestamp': blockchain.chain[-1].timestamp
        } if blockchain.chain else None
    })

@app.route('/api/blocks')
def get_blocks():
    """Get all blocks"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    start = (page - 1) * per_page
    end = start + per_page
    
    blocks = blockchain.chain[start:end][::-1]  # Latest first
    
    return jsonify({
        'blocks': [
            {
                'index': b.index,
                'hash': b.hash,
                'prev_hash': b.prev_hash,
                'timestamp': b.timestamp,
                'nonce': b.nonce,
                'orientation': b.orientation,
                'twist_bit': b.twist_bit,
                'num_transactions': len(b.transactions)
            }
            for b in blocks
        ],
        'total': len(blockchain.chain),
        'page': page,
        'per_page': per_page
    })

@app.route('/api/block/<int:block_id>')
def get_block(block_id):
    """Get specific block"""
    if block_id < 0 or block_id >= len(blockchain.chain):
        return jsonify({'error': 'Block not found'}), 404
    
    block = blockchain.chain[block_id]
    
    return jsonify({
        'index': block.index,
        'hash': block.hash,
        'prev_hash': block.prev_hash,
        'timestamp': block.timestamp,
        'nonce': block.nonce,
        'orientation': block.orientation,
        'twist_bit': block.twist_bit,
        'merkle_root': block.merkle_root,
        'transactions': [
            {
                'hash': tx.compute_tx_hash(),
                'sender': tx.sender,
                'recipient': tx.recipient,
                'amount': tx.amount,
                'timestamp': tx.timestamp,
                'signature': tx.signature
            }
            for tx in block.transactions
        ]
    })

@app.route('/api/transactions')
def get_transactions():
    """Get all transactions"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    all_txs = []
    for block in blockchain.chain:
        for tx in block.transactions:
            all_txs.append({
                'hash': tx.compute_tx_hash(),
                'block_id': block.index,
                'sender': tx.sender,
                'recipient': tx.recipient,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            })
    
    # Sort by timestamp (latest first)
    all_txs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'transactions': all_txs[start:end],
        'total': len(all_txs),
        'page': page,
        'per_page': per_page
    })

@app.route('/api/transaction/<tx_hash>')
def get_transaction(tx_hash):
    """Get specific transaction"""
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx.compute_tx_hash() == tx_hash:
                return jsonify({
                    'hash': tx_hash,
                    'block_id': block.index,
                    'sender': tx.sender,
                    'recipient': tx.recipient,
                    'amount': tx.amount,
                    'timestamp': tx.timestamp,
                    'signature': tx.signature,
                    'nonce': tx.nonce
                })
    
    return jsonify({'error': 'Transaction not found'}), 404

@app.route('/api/accounts')
def get_accounts():
    """Get all accounts"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    accounts = [
        {
            'address': addr,
            'side_a': acc.side_a,
            'side_b': acc.side_b,
            'orientation': acc.orientation,
            'twist_count': acc.twist_count
        }
        for addr, acc in blockchain.accounts.items()
    ]
    
    # Sort by balance (side_a)
    accounts.sort(key=lambda x: x['side_a'], reverse=True)
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'accounts': accounts[start:end],
        'total': len(accounts),
        'page': page,
        'per_page': per_page
    })

@app.route('/api/account/<address>')
def get_account(address):
    """Get specific account"""
    if address not in blockchain.accounts:
        return jsonify({'error': 'Account not found'}), 404
    
    acc = blockchain.accounts[address]
    
    # Get transaction history
    txs = []
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx.sender == address or tx.recipient == address:
                txs.append({
                    'hash': tx.compute_tx_hash(),
                    'block_id': block.index,
                    'sender': tx.sender,
                    'recipient': tx.recipient,
                    'amount': tx.amount,
                    'timestamp': tx.timestamp,
                    'type': 'sent' if tx.sender == address else 'received'
                })
    
    return jsonify({
        'address': address,
        'side_a': acc.side_a,
        'side_b': acc.side_b,
        'orientation': acc.orientation,
        'twist_count': acc.twist_count,
        'total_balance': acc.side_a,
        'transactions': txs
    })

@app.route('/api/search')
def search():
    """Search for blocks, transactions, or accounts"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    results = {
        'blocks': [],
        'transactions': [],
        'accounts': []
    }
    
    # Search blocks by hash or index
    try:
        block_id = int(query)
        if 0 <= block_id < len(blockchain.chain):
            block = blockchain.chain[block_id]
            results['blocks'].append({
                'index': block.index,
                'hash': block.hash,
                'type': 'block'
            })
    except ValueError:
        # Search by hash
        for block in blockchain.chain:
            if block.hash.startswith(query) or query in block.hash:
                results['blocks'].append({
                    'index': block.index,
                    'hash': block.hash,
                    'type': 'block'
                })
    
    # Search transactions by hash
    for block in blockchain.chain:
        for tx in block.transactions:
            tx_hash = tx.compute_tx_hash()
            if tx_hash.startswith(query) or query in tx_hash:
                results['transactions'].append({
                    'hash': tx_hash,
                    'sender': tx.sender,
                    'recipient': tx.recipient,
                    'type': 'transaction'
                })
    
    # Search accounts by address
    for addr in blockchain.accounts:
        if query.lower() in addr.lower():
            results['accounts'].append({
                'address': addr,
                'type': 'account'
            })
    
    return jsonify(results)

@app.route('/api/stats')
def get_stats():
    """Get blockchain statistics"""
    total_txs = sum(len(b.transactions) for b in blockchain.chain)
    total_accounts = len(blockchain.accounts)
    
    # Calculate average block time
    if len(blockchain.chain) > 1:
        block_times = [
            blockchain.chain[i].timestamp - blockchain.chain[i-1].timestamp
            for i in range(1, len(blockchain.chain))
        ]
        avg_block_time = sum(block_times) / len(block_times)
    else:
        avg_block_time = 0
    
    # Orientation distribution
    orientations = [b.orientation for b in blockchain.chain]
    positive = orientations.count(1)
    negative = orientations.count(-1)
    
    return jsonify({
        'total_blocks': len(blockchain.chain),
        'total_transactions': total_txs,
        'total_accounts': total_accounts,
        'average_block_time': avg_block_time,
        'orientation_distribution': {
            'positive': positive,
            'negative': negative
        },
        'chain_valid': blockchain.validate_chain()[0]
    })

# ============================================================================
# ACTION ENDPOINTS (for demo purposes)
# ============================================================================

@app.route('/api/mine', methods=['POST'])
def mine_block():
    """Mine a new block"""
    data = request.get_json()
    recipient = data.get('recipient', 'demo_user')
    amount = data.get('amount', 10.0)
    
    # Create a transaction
    if blockchain.accounts:
        sender = list(blockchain.accounts.keys())[0]
        if blockchain.accounts[sender].side_a >= amount:
            tx = Transaction(sender, recipient, amount)
            blockchain.add_transaction(tx)
    
    # Mine block
    block = blockchain.mine_pending_transactions()
    
    if block:
        # Re-index database
        index_blockchain()
        
        return jsonify({
            'success': True,
            'block': {
                'index': block.index,
                'hash': block.hash,
                'orientation': block.orientation,
                'num_transactions': len(block.transactions)
            }
        })
    
    return jsonify({'success': False, 'error': 'No transactions to mine'}), 400

@app.route('/api/transfer', methods=['POST'])
def transfer():
    """Create a transfer transaction"""
    data = request.get_json()
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = data.get('amount')
    
    if not all([sender, recipient, amount]):
        return jsonify({'error': 'Missing fields'}), 400
    
    if sender not in blockchain.accounts:
        return jsonify({'error': 'Sender account not found'}), 404
    
    if blockchain.accounts[sender].side_a < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    tx = Transaction(sender, recipient, amount)
    success = blockchain.add_transaction(tx)
    
    if success:
        return jsonify({
            'success': True,
            'transaction': {
                'hash': tx.compute_tx_hash(),
                'sender': tx.sender,
                'recipient': tx.recipient,
                'amount': tx.amount
            }
        })
    
    return jsonify({'success': False, 'error': 'Transaction failed'}), 400

@app.route('/api/create_account', methods=['POST'])
def create_account():
    """Create a new account"""
    data = request.get_json()
    address = data.get('address')
    initial_balance = data.get('initial_balance', 100.0)
    
    if not address:
        return jsonify({'error': 'Address required'}), 400
    
    if address in blockchain.accounts:
        return jsonify({'error': 'Account already exists'}), 400
    
    # Create account with initial balance
    blockchain._ensure_account(address).transact_in(initial_balance)
    
    # Re-index
    index_blockchain()
    
    return jsonify({
        'success': True,
        'account': {
            'address': address,
            'balance': initial_balance
        }
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*60)
    print("MOBIUSCOIN BLOCKCHAIN EXPLORER")
    print("="*60)
    
    # Initialize database
    init_db()
    
    # Create some demo data
    print("\nCreating demo accounts...")
    blockchain._ensure_account("alice").transact_in(1000.0)
    blockchain._ensure_account("bob").transact_in(500.0)
    blockchain._ensure_account("charlie").transact_in(250.0)
    
    print("Creating demo transactions...")
    for i in range(3):
        tx = Transaction("alice", "bob", 50.0)
        blockchain.add_transaction(tx)
        tx = Transaction("bob", "charlie", 25.0)
        blockchain.add_transaction(tx)
        blockchain.mine_pending_transactions()
    
    # Index blockchain
    print("Indexing blockchain...")
    index_blockchain()
    
    print(f"\n✅ Blockchain ready: {len(blockchain.chain)} blocks")
    print(f"✅ Accounts: {len(blockchain.accounts)}")
    print(f"✅ Database indexed")
    
    print("\n🌐 Starting web server...")
    print("   Open http://localhost:5000 in your browser")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
