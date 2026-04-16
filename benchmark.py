"""
Throughput benchmark for mini-ethereum.
Measures: tx submission rate, PoW mining time, and confirmed TPS.
"""
import time, sys, os, random
sys.path.insert(0, os.path.dirname(__file__))

from blockchain import Blockchain
from network import Network


# Helper: fund a node by mining coinbase blocks
def fund_node(node, rounds=3):
    for _ in range(rounds):
        # coinbase tx (sender="0") bypasses balance check
        node.blockchain.add_transaction({
            "sender": "0",
            "recipient": node.wallet.address,
            "amount": 1000.0,
            "gas_fee": 0,
        })
        node.blockchain.mine_pending_transactions(node.wallet.address)


def run_benchmark():
    print("=== mini-ethereum throughput benchmark ===\n")

    # ── Setup ──────────────────────────────────
    net = Network()
    net.network_difficulty = 4
    for i in range(5):
        net.create_node(f"node{i}")
    net.create_full_mesh()
    print(f"Network: {len(net.nodes)} nodes, full mesh, difficulty={net.network_difficulty}")

    # Fund every node so transactions pass balance check
    print("Funding nodes (coinbase blocks)...")
    for node in net.nodes.values():
        fund_node(node, rounds=2)
    print("  Done.")

    # ── Phase 1: TX submission throughput ──────
    TX_COUNT = 200
    node_ids = list(net.nodes.keys())

    t0 = time.perf_counter()
    sent = 0
    for i in range(TX_COUNT):
        sender_id = node_ids[i % len(node_ids)]
        recipient_id = node_ids[(i + 1) % len(node_ids)]
        if net.simulate_transaction(sender_id, recipient_id, 0.5):
            sent += 1
    t1 = time.perf_counter()

    tx_submit_rate = sent / (t1 - t0)
    print(f"\n[TX submission]")
    print(f"  Sent {sent}/{TX_COUNT} txs in {t1-t0:.4f}s  →  {tx_submit_rate:,.0f} tx/s")

    # ── Phase 2: Mining throughput ─────────────
    # How many unique txs sit in mempools?
    pending_before = sum(len(n.mempool) for n in net.nodes.values())
    print(f"\n[Mining — difficulty {net.network_difficulty}]")
    print(f"  Pending mempool entries (w/ fan-out): {pending_before}")

    blocks_mined = 0
    total_tx_confirmed = 0
    t_mine_start = time.perf_counter()

    rounds = 0
    while any(len(n.mempool) > 0 for n in net.nodes.values()) and rounds < 50:
        result = net.simulate_mining_round()
        for node_id, r in result.items():
            if r.get("success"):
                blocks_mined += 1
                # block.transactions includes the coinbase reward tx
                total_tx_confirmed += max(0, r.get("transactions", 0) - 1)
        rounds += 1

    t_mine_end = time.perf_counter()
    mine_elapsed = t_mine_end - t_mine_start

    tps_confirmed  = total_tx_confirmed / mine_elapsed if mine_elapsed > 0 else 0
    avg_block_time = mine_elapsed / blocks_mined       if blocks_mined > 0  else 0
    avg_tx_per_blk = total_tx_confirmed / blocks_mined if blocks_mined > 0  else 0

    print(f"  Mining rounds: {rounds}")
    print(f"  Blocks mined: {blocks_mined}")
    print(f"  User txs confirmed: {total_tx_confirmed}")
    print(f"  Total mining time: {mine_elapsed:.3f}s")
    print(f"  Avg block time: {avg_block_time:.3f}s")
    print(f"  Avg txs/block (excl. coinbase): {avg_tx_per_blk:.1f}")

    # ── Phase 3: Raw PoW timing (isolated) ─────
    print(f"\n[Raw single-block PoW timing]")
    for d in [2, 3, 4, 5]:
        bc = Blockchain(difficulty=d)
        bc.add_transaction({"sender": "0", "recipient": "bench", "amount": 1.0, "gas_fee": 0})
        t_a = time.perf_counter()
        bc.mine_pending_transactions("bench")
        t_b = time.perf_counter()
        elapsed = t_b - t_a
        blk = bc.get_latest_block()
        print(f"  d={d}: {elapsed:.3f}s  nonce={blk.nonce:,}  est. {10/elapsed:.1f} tx/s @ 10 tx/block")

    # ── Summary ────────────────────────────────
    print(f"\n{'='*50}")
    print(f"  TX submission throughput   : {tx_submit_rate:>10,.0f} tx/s")
    print(f"  Confirmed TPS (d={net.network_difficulty}, 5 nodes)  : {tps_confirmed:>10.2f} tx/s")
    print(f"  Avg block time             : {avg_block_time:>10.3f} s")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_benchmark()
