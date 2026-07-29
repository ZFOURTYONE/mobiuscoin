#!/usr/bin/env python3
"""Anti-State Ledger (ASL) — prototipe Möbius strip blockchain core"""

class AntiStateAccount:
    def __init__(self, address):
        self.address = address
        self.side_a = 0.0   # debit
        self.side_b = 0.0   # credit
        self.orientation = 1  # +1 atau -1 (twist)

    def twist(self):
        # Flip orientasi seperti Möbius strip
        self.side_a, self.side_b = self.side_b, self.side_a
        self.orientation *= -1

    def transact(self, amount):
        # Transaksi memindahkan dari A ke B melalui twist
        if self.side_a >= amount:
            self.side_a -= amount
            self.side_b += amount
            self.twist()
            return True
        return False

    def loop_back(self):
        # Setelah satu loop penuh, kembali ke genesis dengan orientasi terbalik
        return self.orientation == -1

# Simulasi loop ledger kecil
ledger = [AntiStateAccount("alice"), AntiStateAccount("bob")]
print("Genesis:", ledger[0].side_a, ledger[0].side_b, "orientasi:", ledger[0].orientation)
ledger[0].transact(100)
print("Setelah transaksi:", ledger[0].side_a, ledger[0].side_b, "orientasi:", ledger[0].orientation)
print("Loop kembali?", ledger[0].loop_back())
