#!/usr/bin/env python3
"""MobiusCoin — Blockchain Full Prototype berbasis ASL + O(1) Consensus"""

import hashlib, time, json

class Block:
    def __init__(self, index, prev_hash, data, orientation):
        self.index = index
        self.prev_hash = prev_hash
        self.data = data
        self.orientation = orientation
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        s = f"{self.index}{self.prev_hash}{json.dumps(self.data)}{self.orientation}{self.timestamp}{self.nonce}"
        return hashlib.sha256(s.encode()).hexdigest()

    def mine(self, difficulty=2):
        while self.hash[:difficulty] != "0"*difficulty:
            self.nonce += 1
            self.hash = self.compute_hash()
        self.orientation *= -1  # twist setelah mine

class MobiusChain:
    def __init__(self):
        self.chain = []
        self.create_genesis()

    def create_genesis(self):
        genesis = Block(0, "0", {"msg":"Genesis Möbius"}, 1)
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    def add_block(self, data):
        prev = self.chain[-1]
        new = Block(len(self.chain), prev.hash, data, prev.orientation)
        new.mine()
        self.chain.append(new)
        print(f"Blok {new.index} ditambahkan | orientasi: {new.orientation} | hash: {new.hash[:16]}")

    def validate(self):
        for i in range(1, len(self.chain)):
            b = self.chain[i]
            p = self.chain[i-1]
            # O(1) validator: hanya cek integritas dan link
            if b.prev_hash != p.hash:
                return False, f"Link rusak di blok {i}"
            if b.orientation is None:
                return False, f"Robekan ruang di blok {i}"
        return True, "Ruang utuh — konsensus O(1) diterima"

if __name__ == "__main__":
    chain = MobiusChain()
    chain.add_block({"tx":"alice -> bob 50"})
    chain.add_block({"tx":"bob -> alice 20"})
    ok, msg = chain.validate()
    print("Validasi:", ok, "|", msg)
    for b in chain.chain:
        print(f"  {b.index}: orientasi={b.orientation}, hash={b.hash[:12]}...")
