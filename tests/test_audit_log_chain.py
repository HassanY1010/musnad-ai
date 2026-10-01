"""
Unit Tests for Cryptographic Tamper-Evident Audit Log Chain (Phase 20)
Verifies:
1. Valid chain passes validation
2. Modified entry fails validation (detects tampering)
3. Deleted entry is detectable (breaks forward chain)
4. Reordered entry is detectable (breaks sequential dependencies)
"""
import copy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from app.services.audit_logger import AuditLogChain, GENESIS_HASH


def test_audit_log_cryptographic_integrity():
    chain = AuditLogChain()

    # 1. Append valid entries
    e1 = chain.append("CLAIM_VERIFICATION", "analysis", "ana_001", {"status": "supported"})
    e2 = chain.append("SOURCE_RETRIEVAL", "source", "quran_001", {"score": 1.0})
    e3 = chain.append("STATUS_DECISION", "engine", "rule_001", {"decision": "supported"})

    # Test 1: Valid chain passes
    is_valid, err = AuditLogChain.verify_chain(chain.entries)
    assert is_valid is True, f"Valid chain failed: {err}"
    print("[PASS] 1. Valid audit log chain verified successfully.")

    # Test 2: Modified entry fails validation
    tampered_entries = copy.deepcopy(chain.entries)
    tampered_entries[1]["metadata"]["score"] = 0.50  # modify payload
    is_valid, err = AuditLogChain.verify_chain(tampered_entries)
    assert is_valid is False, "Modified entry should fail validation"
    assert "Tampered payload" in err
    print(f"[PASS] 2. Payload tampering detected: {err}")

    # Test 3: Deleted entry is detectable
    deleted_entries = copy.deepcopy(chain.entries)
    del deleted_entries[1]  # remove middle entry
    is_valid, err = AuditLogChain.verify_chain(deleted_entries)
    assert is_valid is False, "Deleted entry should break chain"
    assert "Broken chain" in err
    print(f"[PASS] 3. Entry deletion detected: {err}")

    # Test 4: Reordered entry is detectable
    reordered_entries = [chain.entries[0], chain.entries[2], chain.entries[1]]
    is_valid, err = AuditLogChain.verify_chain(reordered_entries)
    assert is_valid is False, "Reordered entries should break chain"
    assert "Broken chain" in err
    print(f"[PASS] 4. Entry reordering detected: {err}")

    print("\nALL 4 CRYPTOGRAPHIC AUDIT LOG INTEGRITY TESTS PASSED 100%!")


if __name__ == "__main__":
    test_audit_log_cryptographic_integrity()
