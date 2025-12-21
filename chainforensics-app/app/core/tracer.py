"""
ChainForensics - UTXO Tracer
Forward and backward UTXO tracing with graph building.
Now with Electrs integration for enhanced forward tracing!
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter

from app.config import settings
from app.core.bitcoin_rpc import BitcoinRPC, get_rpc

logger = logging.getLogger("chainforensics.tracer")


class UTXOStatus(Enum):
    """UTXO status enumeration."""
    UNSPENT = "unspent"
    SPENT = "spent"
    COINBASE = "coinbase"
    UNKNOWN = "unknown"


@dataclass
class UTXONode:
    """Represents a UTXO in the trace graph."""
    txid: str
    vout: int
    value_sats: int
    address: Optional[str]
    script_type: str
    status: UTXOStatus
    block_height: Optional[int]
    block_time: Optional[datetime]
    spent_by_txid: Optional[str] = None
    spent_by_vin: Optional[int] = None
    depth: int = 0
    coinjoin_score: float = 0.0
    
    @property
    def value_btc(self) -> float:
        return self.value_sats / 100_000_000
    
    def to_dict(self) -> Dict:
        return {
            "txid": self.txid,
            "vout": self.vout,
            "value_sats": self.value_sats,
            "value_btc": self.value_btc,
            "address": self.address,
            "script_type": self.script_type,
            "status": self.status.value,
            "block_height": self.block_height,
            "block_time": self.block_time.isoformat() if self.block_time else None,
            "spent_by_txid": self.spent_by_txid,
            "spent_by_vin": self.spent_by_vin,
            "depth": self.depth,
            "coinjoin_score": self.coinjoin_score
        }


@dataclass
class TraceEdge:
    """Represents an edge (spend) in the trace graph."""
    from_txid: str
    from_vout: int
    to_txid: str
    to_vin: int
    value_sats: int


@dataclass
class TraceResult:
    """Complete trace result."""
    start_txid: str
    start_vout: int
    direction: str  # 'forward' or 'backward'
    max_depth: int
    nodes: List[UTXONode] = field(default_factory=list)
    edges: List[TraceEdge] = field(default_factory=list)
    unspent_endpoints: List[UTXONode] = field(default_factory=list)
    coinbase_origins: List[UTXONode] = field(default_factory=list)
    coinjoin_txids: List[str] = field(default_factory=list)
    total_transactions: int = 0
    total_value_traced_sats: int = 0
    execution_time_ms: int = 0
    warnings: List[str] = field(default_factory=list)
    hit_limit: bool = False
    electrs_enabled: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "start_txid": self.start_txid,
            "start_vout": self.start_vout,
            "direction": self.direction,
            "max_depth": self.max_depth,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [
                {
                    "from_txid": e.from_txid,
                    "from_vout": e.from_vout,
                    "to_txid": e.to_txid,
                    "to_vin": e.to_vin,
                    "value_sats": e.value_sats
                }
                for e in self.edges
            ],
            "unspent_endpoints": [n.to_dict() for n in self.unspent_endpoints],
            "coinbase_origins": [n.to_dict() for n in self.coinbase_origins],
            "coinjoin_txids": self.coinjoin_txids,
            "total_transactions": self.total_transactions,
            "total_value_traced_sats": self.total_value_traced_sats,
            "execution_time_ms": self.execution_time_ms,
            "warnings": self.warnings,
            "hit_limit": self.hit_limit,
            "electrs_enabled": self.electrs_enabled,
            "summary": {
                "unspent_count": len(self.unspent_endpoints),
                "coinbase_count": len(self.coinbase_origins),
                "coinjoin_count": len(self.coinjoin_txids),
                "total_nodes": len(self.nodes)
            }
        }


class UTXOTracer:
    """UTXO forward and backward tracer with Electrs support."""
    
    # Safety limits
    MAX_TRANSACTIONS_PER_TRACE = 200
    MAX_QUEUE_SIZE = 1000
    MAX_CONSECUTIVE_ELECTRS_FAILURES = 3  # Stop using Electrs after 3 failures (was 5)
    MAX_TRACE_TIME_SECONDS = 60  # 60 second overall timeout (was 240s)
    
    def __init__(self, rpc: BitcoinRPC = None):
        self.rpc = rpc or get_rpc()
        self._tx_cache: Dict[str, Dict] = {}
        self._electrs = None
        self._electrs_checked = False
    
    async def _get_electrs(self):
        """Lazy load Electrs client."""
        if not self._electrs_checked:
            try:
                from app.core.electrs import get_electrs
                self._electrs = get_electrs()
                if self._electrs.is_configured:
                    await self._electrs.connect()
                else:
                    self._electrs = None
            except Exception as e:
                logger.debug(f"Electrs not available: {e}")
                self._electrs = None
            self._electrs_checked = True
        return self._electrs
    
    def clear_cache(self):
        """Clear the transaction cache."""
        self._tx_cache.clear()
    
    async def _get_transaction(self, txid: str) -> Optional[Dict]:
        """Get transaction with caching."""
        if txid in self._tx_cache:
            cached = self._tx_cache[txid]
            # Validate cached data is a dict, not a string
            if isinstance(cached, dict):
                return cached
            else:
                del self._tx_cache[txid]
        
        try:
            tx = await self.rpc.get_raw_transaction(txid, True)
            # Validate response is a dict (not a hex string)
            if tx and isinstance(tx, dict):
                self._tx_cache[txid] = tx
                return tx
            elif tx and isinstance(tx, str):
                logger.warning(f"Got hex string instead of dict for tx {txid}")
                return None
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch transaction {txid}: {e}")
            return None
    
    def _calculate_coinjoin_score_fast(self, tx: Dict) -> float:
        """Fast CoinJoin score calculation - NO external calls."""
        vouts = tx.get("vout", [])
        vins = tx.get("vin", [])
        
        if len(vouts) < 2:
            return 0.0
        
        values = [round(out.get("value", 0), 8) for out in vouts]
        value_counts = Counter(values)
        
        if not value_counts:
            return 0.0
        
        max_equal = max(value_counts.values())
        num_outputs = len(vouts)
        num_inputs = len(vins)
        
        # Whirlpool: exactly 5 equal outputs
        if num_outputs == 5 and max_equal == 5:
            equal_value = max(value_counts.keys(), key=lambda k: value_counts[k])
            whirlpool_denoms = [0.001, 0.01, 0.05, 0.5]
            if any(abs(equal_value - d) < 0.0001 for d in whirlpool_denoms):
                return 0.95
            return 0.85
        
        # Wasabi: many equal outputs
        if max_equal >= 10:
            return 0.85
        
        # JoinMarket / Generic
        if max_equal >= 5 and num_inputs >= 3:
            return 0.70
        
        if max_equal >= 3 and num_inputs >= 2:
            return 0.40
        
        unique_ratio = len(value_counts) / num_outputs
        if unique_ratio < 0.3 and num_outputs >= 5:
            return 0.50
        
        return 0.0
    
    async def _find_spending_tx_electrs(self, txid: str, vout: int, address: str) -> Optional[str]:
        """Use Electrs to find the transaction that spent this output."""
        electrs = await self._get_electrs()
        if not electrs:
            logger.debug("_find_spending_tx_electrs: No electrs client")
            return None
        
        try:
            logger.debug(f"_find_spending_tx_electrs: Starting lookup for {txid[:16]}...:{vout}")
            # Reduced timeout to 30s - if Electrs doesn't respond quickly, it's probably stuck
            spending_txid = await asyncio.wait_for(
                electrs.find_spending_tx(txid, vout),
                timeout=30.0  # 30 second timeout per lookup (was 120s)
            )
            if spending_txid:
                logger.debug(f"_find_spending_tx_electrs: Found spending tx {spending_txid[:16]}...")
            else:
                logger.debug(f"_find_spending_tx_electrs: No spending tx found (UTXO may be unspent or lookup failed)")
            return spending_txid
        except asyncio.TimeoutError:
            logger.warning(f"_find_spending_tx_electrs: TIMEOUT after 30s for {txid[:16]}...:{vout}")
            # Force reconnection after timeout - the connection is likely corrupted
            logger.warning("_find_spending_tx_electrs: Forcing Electrs reconnection due to timeout")
            try:
                await electrs.disconnect()
            except:
                pass
            return None
        except Exception as e:
            logger.warning(f"_find_spending_tx_electrs: EXCEPTION for {txid[:16]}...:{vout}: {type(e).__name__}: {e}")
            # Force reconnection after any exception too
            try:
                await electrs.disconnect()
            except:
                pass
            return None
    
    async def trace_forward(
        self,
        txid: str,
        vout: int,
        max_depth: int = None,
        progress_callback=None
    ) -> TraceResult:
        """
        Trace a UTXO forward through all subsequent spends.
        
        With Electrs: Can find spending transactions and follow the full chain.
        Without Electrs: Can only identify if UTXO is spent, not where it went.
        """
        logger.info(f"=== TRACE FORWARD START === txid={txid[:16]}..., vout={vout}")
        
        if max_depth is None:
            max_depth = settings.DEFAULT_TRACE_DEPTH
        max_depth = min(max_depth, settings.MAX_TRACE_DEPTH)
        
        logger.info(f"Max depth: {max_depth}, Max transactions: {self.MAX_TRANSACTIONS_PER_TRACE}, Timeout: {self.MAX_TRACE_TIME_SECONDS}s")
        
        start_time = datetime.utcnow()
        result = TraceResult(
            start_txid=txid,
            start_vout=vout,
            direction="forward",
            max_depth=max_depth
        )
        
        # Check if Electrs is available
        logger.info("Checking Electrs availability...")
        electrs = await self._get_electrs()
        result.electrs_enabled = electrs is not None
        logger.info(f"Electrs enabled: {result.electrs_enabled}")
        
        if not result.electrs_enabled:
            result.warnings.append(
                "Electrs not available - forward tracing limited. "
                "Can identify spent UTXOs but cannot follow to spending transaction."
            )
        
        # Queue: (txid, vout, depth)
        queue: List[Tuple[str, int, int]] = [(txid, vout, 0)]
        visited: Set[Tuple[str, int]] = set()
        tx_count = 0
        consecutive_electrs_failures = 0
        electrs_disabled = False
        electrs_lookup_count = 0
        electrs_success_count = 0
        
        logger.info("Starting trace loop...")
        
        while queue and tx_count < self.MAX_TRANSACTIONS_PER_TRACE:
            # Check overall timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > self.MAX_TRACE_TIME_SECONDS:
                logger.warning(f"TIMEOUT after {elapsed:.1f}s - tx_count={tx_count}, queue_size={len(queue)}, visited={len(visited)}")
                result.warnings.append(f"Trace timeout ({self.MAX_TRACE_TIME_SECONDS}s) reached - returning partial results")
                result.hit_limit = True
                break
            
            # Log progress every 10 transactions
            if tx_count > 0 and tx_count % 10 == 0:
                logger.info(f"Progress: tx_count={tx_count}, queue_size={len(queue)}, visited={len(visited)}, elapsed={elapsed:.1f}s, electrs_lookups={electrs_lookup_count}, electrs_success={electrs_success_count}")
            
            if len(queue) > self.MAX_QUEUE_SIZE:
                logger.warning(f"Queue size {len(queue)} exceeded limit {self.MAX_QUEUE_SIZE}")
                result.warnings.append(f"Queue size exceeded {self.MAX_QUEUE_SIZE}, truncating")
                result.hit_limit = True
                queue = queue[:self.MAX_QUEUE_SIZE]
            
            current_txid, current_vout, depth = queue.pop(0)
            
            if (current_txid, current_vout) in visited:
                continue
            visited.add((current_txid, current_vout))
            
            if depth > max_depth:
                logger.debug(f"Depth limit {max_depth} reached at {current_txid[:16]}...:{current_vout}")
                result.warnings.append(f"Depth limit reached at {current_txid}:{current_vout}")
                continue
            
            tx = await self._get_transaction(current_txid)
            if not tx or not isinstance(tx, dict):
                logger.warning(f"Transaction not found or invalid: {current_txid[:16]}...")
                result.warnings.append(f"Transaction not found: {current_txid}")
                continue
            
            tx_count += 1
            
            if current_vout >= len(tx.get("vout", [])):
                result.warnings.append(f"Invalid vout {current_vout} for tx {current_txid}")
                continue
            
            output = tx["vout"][current_vout]
            value_sats = int(output["value"] * 100_000_000)
            script_pub_key = output.get("scriptPubKey", {})
            address = script_pub_key.get("address")
            script_type = script_pub_key.get("type", "unknown")
            
            block_height = tx.get("blockheight") or tx.get("height")
            block_time = None
            if tx.get("blocktime"):
                block_time = datetime.utcfromtimestamp(tx["blocktime"])
            
            # Check if spent using Bitcoin Core
            utxo_check = await self.rpc.get_tx_out(current_txid, current_vout)
            
            cj_score = self._calculate_coinjoin_score_fast(tx)
            if cj_score > 0.7 and current_txid not in result.coinjoin_txids:
                result.coinjoin_txids.append(current_txid)
            
            if utxo_check is not None:
                # UTXO is unspent
                node = UTXONode(
                    txid=current_txid,
                    vout=current_vout,
                    value_sats=value_sats,
                    address=address,
                    script_type=script_type,
                    status=UTXOStatus.UNSPENT,
                    block_height=block_height,
                    block_time=block_time,
                    depth=depth,
                    coinjoin_score=cj_score
                )
                result.nodes.append(node)
                result.unspent_endpoints.append(node)
                result.total_value_traced_sats += value_sats
            else:
                # UTXO is spent - try to find spending transaction
                spending_txid = None
                spending_vin = None
                
                if electrs and address and depth < max_depth and not electrs_disabled:
                    electrs_lookup_count += 1
                    lookup_start = datetime.utcnow()
                    logger.debug(f"Electrs lookup #{electrs_lookup_count} for {current_txid[:16]}...:{current_vout} (address={address[:20]}...)")
                    
                    spending_txid = await self._find_spending_tx_electrs(current_txid, current_vout, address)
                    
                    lookup_time = (datetime.utcnow() - lookup_start).total_seconds()
                    
                    if spending_txid:
                        electrs_success_count += 1
                        consecutive_electrs_failures = 0  # Reset on success
                        logger.debug(f"Electrs lookup SUCCESS in {lookup_time:.2f}s - found {spending_txid[:16]}...")
                        
                        # Found the spending transaction! Add it to queue
                        spending_tx = await self._get_transaction(spending_txid)
                        if spending_tx and isinstance(spending_tx, dict):
                            # Find which vin spent our output
                            for i, vin in enumerate(spending_tx.get("vin", [])):
                                if vin.get("txid") == current_txid and vin.get("vout") == current_vout:
                                    spending_vin = i
                                    break
                            
                            # Add edge
                            result.edges.append(TraceEdge(
                                from_txid=current_txid,
                                from_vout=current_vout,
                                to_txid=spending_txid,
                                to_vin=spending_vin or 0,
                                value_sats=value_sats
                            ))
                            
                            # Add all outputs of spending tx to queue
                            for out_idx, out in enumerate(spending_tx.get("vout", [])):
                                if (spending_txid, out_idx) not in visited:
                                    queue.append((spending_txid, out_idx, depth + 1))
                    else:
                        # Electrs lookup failed
                        consecutive_electrs_failures += 1
                        logger.warning(f"Electrs lookup FAILED in {lookup_time:.2f}s - consecutive failures: {consecutive_electrs_failures}")
                        
                        if consecutive_electrs_failures >= self.MAX_CONSECUTIVE_ELECTRS_FAILURES:
                            electrs_disabled = True
                            logger.error(f"Electrs DISABLED after {consecutive_electrs_failures} consecutive failures")
                            result.warnings.append(
                                f"Electrs disabled after {consecutive_electrs_failures} consecutive failures - "
                                "continuing without forward tracing"
                            )
                
                node = UTXONode(
                    txid=current_txid,
                    vout=current_vout,
                    value_sats=value_sats,
                    address=address,
                    script_type=script_type,
                    status=UTXOStatus.SPENT,
                    block_height=block_height,
                    block_time=block_time,
                    spent_by_txid=spending_txid,
                    spent_by_vin=spending_vin,
                    depth=depth,
                    coinjoin_score=cj_score
                )
                result.nodes.append(node)
                result.total_value_traced_sats += value_sats
            
            if progress_callback:
                await progress_callback(tx_count, len(visited), depth)
        
        if tx_count >= self.MAX_TRANSACTIONS_PER_TRACE:
            result.warnings.append(f"Transaction limit ({self.MAX_TRANSACTIONS_PER_TRACE}) reached")
            result.hit_limit = True
        
        result.total_transactions = tx_count
        result.execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info(f"=== TRACE FORWARD COMPLETE ===")
        logger.info(f"  Total time: {result.execution_time_ms}ms")
        logger.info(f"  Transactions processed: {tx_count}")
        logger.info(f"  Nodes found: {len(result.nodes)}")
        logger.info(f"  Edges found: {len(result.edges)}")
        logger.info(f"  Unspent endpoints: {len(result.unspent_endpoints)}")
        logger.info(f"  Electrs lookups: {electrs_lookup_count}, successes: {electrs_success_count}")
        logger.info(f"  Electrs disabled: {electrs_disabled}")
        logger.info(f"  Warnings: {len(result.warnings)}")
        if result.warnings:
            for w in result.warnings[:5]:
                logger.info(f"    - {w[:100]}...")
        
        return result
    
    async def trace_backward(
        self,
        txid: str,
        max_depth: int = None,
        progress_callback=None
    ) -> TraceResult:
        """
        Trace a transaction backward through all inputs to find origins.
        Stops at coinbase transactions or limits.
        """
        if max_depth is None:
            max_depth = settings.DEFAULT_TRACE_DEPTH
        max_depth = min(max_depth, settings.MAX_TRACE_DEPTH)
        
        start_time = datetime.utcnow()
        result = TraceResult(
            start_txid=txid,
            start_vout=0,
            direction="backward",
            max_depth=max_depth
        )
        
        # Check Electrs status
        electrs = await self._get_electrs()
        result.electrs_enabled = electrs is not None
        
        # Queue: (txid, depth)
        queue: List[Tuple[str, int]] = [(txid, 0)]
        visited: Set[str] = set()
        tx_count = 0
        
        while queue and tx_count < self.MAX_TRANSACTIONS_PER_TRACE:
            if len(queue) > self.MAX_QUEUE_SIZE:
                result.warnings.append(f"Queue size exceeded {self.MAX_QUEUE_SIZE}, truncating")
                result.hit_limit = True
                queue = queue[:self.MAX_QUEUE_SIZE]
            
            current_txid, depth = queue.pop(0)
            
            if current_txid in visited:
                continue
            visited.add(current_txid)
            
            if depth > max_depth:
                result.warnings.append(f"Depth limit reached at {current_txid}")
                continue
            
            tx = await self._get_transaction(current_txid)
            if not tx or not isinstance(tx, dict):
                result.warnings.append(f"Transaction not found: {current_txid}")
                continue
            
            tx_count += 1
            
            block_height = tx.get("blockheight") or tx.get("height")
            block_time = None
            if tx.get("blocktime"):
                block_time = datetime.utcfromtimestamp(tx["blocktime"])
            
            # Check for coinbase
            is_coinbase = any("coinbase" in vin for vin in tx.get("vin", []))
            
            if is_coinbase:
                total_value = sum(int(out["value"] * 100_000_000) for out in tx.get("vout", []))
                node = UTXONode(
                    txid=current_txid,
                    vout=0,
                    value_sats=total_value,
                    address=None,
                    script_type="coinbase",
                    status=UTXOStatus.COINBASE,
                    block_height=block_height,
                    block_time=block_time,
                    depth=depth
                )
                result.nodes.append(node)
                result.coinbase_origins.append(node)
                continue
            
            cj_score = self._calculate_coinjoin_score_fast(tx)
            if cj_score > 0.7 and current_txid not in result.coinjoin_txids:
                result.coinjoin_txids.append(current_txid)
            
            # Only add parent transactions if below max depth
            if depth < max_depth:
                for vin in tx.get("vin", []):
                    if "txid" in vin:
                        prev_txid = vin["txid"]
                        prev_vout = vin["vout"]
                        
                        result.edges.append(TraceEdge(
                            from_txid=prev_txid,
                            from_vout=prev_vout,
                            to_txid=current_txid,
                            to_vin=vin.get("sequence", 0),
                            value_sats=0
                        ))
                        
                        if prev_txid not in visited:
                            queue.append((prev_txid, depth + 1))
            
            total_output = sum(int(out["value"] * 100_000_000) for out in tx.get("vout", []))
            node = UTXONode(
                txid=current_txid,
                vout=0,
                value_sats=total_output,
                address=None,
                script_type="transaction",
                status=UTXOStatus.SPENT,
                block_height=block_height,
                block_time=block_time,
                depth=depth,
                coinjoin_score=cj_score
            )
            result.nodes.append(node)
            result.total_value_traced_sats += total_output
            
            if progress_callback:
                await progress_callback(tx_count, len(visited), depth)
        
        if tx_count >= self.MAX_TRANSACTIONS_PER_TRACE:
            result.warnings.append(f"Transaction limit ({self.MAX_TRANSACTIONS_PER_TRACE}) reached")
            result.hit_limit = True
        
        result.total_transactions = tx_count
        result.execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return result
    
    async def get_utxo_tree(
        self,
        txid: str,
        forward_depth: int = 5,
        backward_depth: int = 5
    ) -> Dict:
        """Get complete UTXO tree (both directions)."""
        forward_result = await self.trace_forward(txid, 0, forward_depth)
        backward_result = await self.trace_backward(txid, backward_depth)
        
        return {
            "txid": txid,
            "forward": forward_result.to_dict(),
            "backward": backward_result.to_dict(),
            "electrs_enabled": forward_result.electrs_enabled,
            "summary": {
                "forward_unspent": len(forward_result.unspent_endpoints),
                "backward_coinbase": len(backward_result.coinbase_origins),
                "total_coinjoins": len(set(forward_result.coinjoin_txids + backward_result.coinjoin_txids)),
                "total_transactions_analyzed": forward_result.total_transactions + backward_result.total_transactions
            }
        }


# Singleton
_tracer_instance: Optional[UTXOTracer] = None


def get_tracer() -> UTXOTracer:
    """Get or create tracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = UTXOTracer()
    return _tracer_instance
