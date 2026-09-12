#!/usr/bin/env python3
"""Behavioral self-tests for the deterministic operation controller."""
from __future__ import annotations

from copy import deepcopy

from operation_controller import OperationError, init_record, transition_record, validate_record

A = "a" * 40
B = "b" * 40
C = "c" * 40
H = "d" * 64


def must_fail(fn, contains: str) -> None:
    try:
        fn()
    except OperationError as exc:
        assert contains in str(exc), (contains, str(exc))
    else:
        raise AssertionError(f"expected failure containing: {contains}")


def base_record():
    return init_record(
        operation_id="op-test-001",
        repository="example/service",
        incident_issue=42,
        source_type="synthetic",
        signal="critical journey failed",
        production_before_sha=A,
    )


def through_probation():
    r = base_record()
    r = transition_record(r, to_state="oriented", evidence={
        "classification": {"kind": "incident", "severity": "P1", "confidence": 0.98}
    })
    r = transition_record(r, to_state="decided", evidence={
        "decision": {"autonomy_level": 3, "risk": "moderate", "authorized": True}
    })
    r = transition_record(r, to_state="reproducing", evidence={
        "reproduction": {"branch": "auto-repro/issue-42"}
    })
    r = transition_record(r, to_state="evidence_frozen", evidence={
        "reproduction": {"sha": B, "result": "red", "tests_only": True}
    })
    r = transition_record(r, to_state="repairing", evidence={
        "repair": {"branch": "auto-repair/issue-42", "reproduction_sha": B}
    })
    r = transition_record(r, to_state="verifying", evidence={
        "repair": {"candidate_sha": C, "reproduction_unchanged": True}
    })
    r = transition_record(r, to_state="reviewed", evidence={
        "review": {"reviewed_sha": C, "disposition": "PASS", "engineering_ready": True}
    })
    r = transition_record(r, to_state="release_authorized", evidence={
        "release": {"candidate_sha": C, "ci_verified_sha": C, "reviewed_sha": C, "authorized": True}
    })
    r = transition_record(r, to_state="deployed", evidence={
        "deployment": {"sha": C, "environment": "production", "deployment_id": "deploy-123"}
    })
    return transition_record(r, to_state="production_probation", evidence={
        "probation": {"started_at": "2026-09-12T06:00:00Z", "required_checks": ["booking-journey", "error-rate"]}
    })


def test_happy_path() -> None:
    r = through_probation()
    r = transition_record(r, to_state="healthy", evidence={
        "verification": {"sha": C, "result": "PASS", "evidence_sha256": H}
    })
    r = transition_record(r, to_state="learning", evidence={
        "learning": {"lesson_id": "lesson-42", "durable_improvement": "monitor:booking-journey-v2"}
    })
    r = transition_record(r, to_state="closed", evidence={
        "closure": {"resolution": "healthy", "summary": "Candidate remained healthy through probation."}
    })
    validate_record(r)
    assert r["state"] == "closed"
    assert r["candidate_sha"] == r["reviewed_sha"] == r["deployed_sha"] == C


def test_rollback_path() -> None:
    r = through_probation()
    r = transition_record(r, to_state="rollback_authorized", evidence={
        "rollback": {
            "current_sha": C,
            "prior_known_good_sha": A,
            "authorized": True,
            "schema_compatible": True,
        }
    })
    r = transition_record(r, to_state="rolled_back", evidence={
        "rollback": {"target_sha": A, "result": "success"}
    })
    r = transition_record(r, to_state="recovery_verified", evidence={
        "verification": {"sha": A, "result": "PASS", "evidence_sha256": H}
    })
    r = transition_record(r, to_state="learning", evidence={
        "learning": {"summary": "Rollback restored the critical journey.", "durable_improvement": "test:regression-42"}
    })
    r = transition_record(r, to_state="closed", evidence={
        "closure": {"resolution": "rolled_back", "summary": "Production restored to prior known-good release."}
    })
    validate_record(r)
    assert r["state"] == "closed"
    assert r["prior_known_good_sha"] == A


def test_skipped_state_fails() -> None:
    r = base_record()
    must_fail(
        lambda: transition_record(r, to_state="release_authorized", evidence={}),
        "illegal transition",
    )


def test_stale_review_sha_fails() -> None:
    r = through_probation()
    events = r["events"]
    verifying_index = next(i for i, e in enumerate(events) if e["to"] == "verifying")
    partial = deepcopy(r)
    partial["events"] = deepcopy(events[: verifying_index + 1])
    partial["sequence"] = verifying_index
    partial["state"] = "verifying"
    partial["reviewed_sha"] = None
    partial["deployed_sha"] = None
    validate_record(partial)
    must_fail(
        lambda: transition_record(partial, to_state="reviewed", evidence={
            "review": {"reviewed_sha": A, "disposition": "PASS", "engineering_ready": True}
        }),
        "exact candidate SHA",
    )


def test_release_sha_mismatch_fails() -> None:
    r = through_probation()
    events = r["events"]
    reviewed_index = next(i for i, e in enumerate(events) if e["to"] == "reviewed")
    partial = deepcopy(r)
    partial["events"] = deepcopy(events[: reviewed_index + 1])
    partial["sequence"] = reviewed_index
    partial["state"] = "reviewed"
    partial["deployed_sha"] = None
    validate_record(partial)
    must_fail(
        lambda: transition_record(partial, to_state="release_authorized", evidence={
            "release": {"candidate_sha": C, "ci_verified_sha": A, "reviewed_sha": C, "authorized": True}
        }),
        "CI evidence must bind candidate SHA",
    )


def test_tampered_chain_fails() -> None:
    r = through_probation()
    tampered = deepcopy(r)
    tampered["events"][2]["evidence"]["decision"]["risk"] = "low"
    must_fail(lambda: validate_record(tampered), "digest mismatch")


def test_rollback_target_mismatch_fails() -> None:
    r = through_probation()
    r = transition_record(r, to_state="rollback_authorized", evidence={
        "rollback": {
            "current_sha": C,
            "prior_known_good_sha": A,
            "authorized": True,
            "schema_compatible": True,
        }
    })
    must_fail(
        lambda: transition_record(r, to_state="rolled_back", evidence={
            "rollback": {"target_sha": B, "result": "success"}
        }),
        "authorized prior-known-good SHA",
    )


def test_escalation_is_terminal() -> None:
    r = base_record()
    r = transition_record(r, to_state="escalated", evidence={
        "escalation": {"reason": "Policy ambiguity requires human decision."}
    })
    validate_record(r)
    must_fail(
        lambda: transition_record(r, to_state="oriented", evidence={
            "classification": {"kind": "incident", "severity": "P1", "confidence": 1.0}
        }),
        "illegal transition",
    )


def main() -> None:
    tests = [
        test_happy_path,
        test_rollback_path,
        test_skipped_state_fails,
        test_stale_review_sha_fails,
        test_release_sha_mismatch_fails,
        test_tampered_chain_fails,
        test_rollback_target_mismatch_fails,
        test_escalation_is_terminal,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
