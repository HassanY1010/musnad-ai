"""
MUSNAD AI - Cryptographic Tamper-Evident Audit Logger
Implements forward-chained SHA-256 hash trees for immutable audit logs:
entry_hash = SHA256(previous_hash + payload)

Provides verification functions to detect:
1. Entry modifications
2. Entry deletions
3. Entry reordering
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


GENESIS_HASH = "0" * 64


def compute_payload_hash(payload: Dict[str, Any]) -> str:
    """Deterministic SHA-256 hash of a serialized payload."""
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_entry_hash(previous_hash: str, payload: Dict[str, Any]) -> str:
    """Computes entry_hash = SHA256(previous_hash + payload_hash)."""
    p_hash = compute_payload_hash(payload)
    chained_data = f"{previous_hash}:{p_hash}"
    return hashlib.sha256(chained_data.encode("utf-8")).hexdigest()


class AuditLogChain:
    """In-memory and persistent cryptographic audit log chain."""

    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def append(self, action: str, entity_type: str, entity_id: str, metadata: Optional[Dict[str, Any]] = None, actor_id: Optional[str] = None) -> Dict[str, Any]:
        prev_hash = self.entries[-1]["entry_hash"] if self.entries else GENESIS_HASH
        
        payload = {
            "index": len(self.entries) + 1,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "actor_id": actor_id or "system",
        }
        
        entry_hash = compute_entry_hash(prev_hash, payload)
        
        entry = {
            **payload,
            "previous_hash": prev_hash,
            "entry_hash": entry_hash,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self.entries.append(entry)
        return entry

    @staticmethod
    def verify_chain(entries: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Validates entire audit trail integrity.
        Returns (True, None) if valid, or (False, error_reason) if tampered.
        """
        if not entries:
            return True, None

        expected_prev_hash = GENESIS_HASH
        for idx, entry in enumerate(entries):
            # Check 1: Chain continuity
            if entry.get("previous_hash") != expected_prev_hash:
                return False, f"Broken chain at entry {idx + 1}: expected prev_hash {expected_prev_hash}, got {entry.get('previous_hash')}"

            # Check 2: Payload tampering
            payload = {
                "index": entry.get("index"),
                "action": entry.get("action"),
                "entity_type": entry.get("entity_type"),
                "entity_id": entry.get("entity_id"),
                "metadata": entry.get("metadata", {}),
                "actor_id": entry.get("actor_id"),
            }
            computed_hash = compute_entry_hash(expected_prev_hash, payload)
            if computed_hash != entry.get("entry_hash"):
                return False, f"Tampered payload at entry {idx + 1}: computed {computed_hash} != stored {entry.get('entry_hash')}"

            expected_prev_hash = entry["entry_hash"]

        return True, None


audit_log_chain = AuditLogChain()
