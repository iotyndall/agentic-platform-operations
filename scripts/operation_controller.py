#!/usr/bin/env python3
"""Deterministic operation-record state machine for agentic platform operations.

The controller is deliberately dependency-free and has no repository, network, merge,
deploy, or rollback authority. It validates evidence and emits the next record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
OP_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
REPO_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

ACTIVE_STATES = (
    "observed",
    "oriented",
    "decided",
    "reproducing",
    "evidence_frozen",
    "repairing",
    "verifying",
    "reviewed",
    "release_authorized",
    "deployed",
    "production_probation",
    "healthy",
    "rollback_authorized",
    "rolled_back",
    "recovery_verified",
    "learning",
)
TERMINAL_STATES = ("closed", "escalated")
ALL_STATES = ACTIVE_STATES + TERMINAL_STATES

ALLOWED_TRANSITIONS = {
    "observed": {"oriented", "escalated"},
    "oriented": {"decided", "escalated"},
    "decided": {"reproducing", "escalated"},
    "reproducing": {"evidence_frozen", "escalated"},
    "evidence_frozen": {"repairing", "escalated"},
    "repairing": {"verifying", "escalated"},
    "verifying": {"reviewed", "escalated"},
    "reviewed": {"release_authorized", "escalated"},
    "release_authorized": {"deployed", "escalated"},
    "deployed": {"production_probation", "escalated"},
    "production_probation": {"healthy", "rollback_authorized", "escalated"},
    "healthy": {"learning", "escalated"},
    "rollback_authorized": {"rolled_back", "escalated"},
    "rolled_back": {"recovery_verified", "escalated"},
    "recovery_verified": {"learning", "escalated"},
    "learning": {"closed", "escalated"},
    "closed": set(),
    "escalated": set(),
}


class OperationError(ValueError):
    """Fail-closed operation transition error."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _event_digest(event_without_digest: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(event_without_digest).encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OperationError(message)


def _require_str(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    _require(isinstance(value, str) and bool(value.strip()), f"missing/invalid evidence field: {key}")
    return value


def _require_bool(mapping: dict[str, Any], key: str, expected: bool = True) -> bool:
    value = mapping.get(key)
    _require(isinstance(value, bool) and value is expected, f"evidence field {key} must be {expected}")
    return value


def _require_sha(mapping: dict[str, Any], key: str) -> str:
    value = _require_str(mapping, key)
    _require(bool(SHA_RE.fullmatch(value)), f"evidence field {key} must be a full 40-character lowercase SHA")
    return value


def _require_sha256(mapping: dict[str, Any], key: str) -> str:
    value = _require_str(mapping, key)
    _require(bool(SHA256_RE.fullmatch(value)), f"evidence field {key} must be a 64-character lowercase SHA-256")
    return value


def _build_event(
    *,
    sequence: int,
    from_state: str | None,
    to_state: str,
    actor: str,
    evidence: dict[str, Any],
    previous_event_sha256: str | None,
) -> dict[str, Any]:
    base = {
        "sequence": sequence,
        "from": from_state,
        "to": to_state,
        "actor": actor,
        "evidence": deepcopy(evidence),
        "previous_event_sha256": previous_event_sha256,
    }
    return {**base, "event_sha256": _event_digest(base)}


def init_record(
    *,
    operation_id: str,
    repository: str,
    incident_issue: int,
    source_type: str,
    signal: str,
    production_before_sha: str | None = None,
) -> dict[str, Any]:
    _require(bool(OP_ID_RE.fullmatch(operation_id)), "invalid operation_id")
    _require(bool(REPO_RE.fullmatch(repository)), "repository must be owner/name")
    _require(isinstance(incident_issue, int) and incident_issue > 0, "incident_issue must be positive")
    _require(isinstance(source_type, str) and bool(source_type.strip()), "source_type is required")
    _require(isinstance(signal, str) and bool(signal.strip()), "signal is required")
    if production_before_sha is not None:
        _require(bool(SHA_RE.fullmatch(production_before_sha)), "production_before_sha must be a full SHA")

    evidence: dict[str, Any] = {
        "operation_id": operation_id,
        "repository": repository,
        "incident_issue": incident_issue,
        "source_type": source_type,
        "signal": signal,
    }
    if production_before_sha is not None:
        evidence["production_before_sha"] = production_before_sha

    event = _build_event(
        sequence=0,
        from_state=None,
        to_state="observed",
        actor="deterministic-controller",
        evidence=evidence,
        previous_event_sha256=None,
    )
    record = {
        "version": 1,
        "operation_id": operation_id,
        "repository": repository,
        "incident_issue": incident_issue,
        "state": "observed",
        "sequence": 0,
        "production_before_sha": production_before_sha,
        "reproduction_sha": None,
        "candidate_sha": None,
        "reviewed_sha": None,
        "deployed_sha": None,
        "prior_known_good_sha": None,
        "resolution_path": None,
        "events": [event],
    }
    validate_record(record)
    return record


def _validate_transition_evidence(record: dict[str, Any], to_state: str, evidence: dict[str, Any]) -> None:
    if to_state == "oriented":
        classification = evidence.get("classification")
        _require(isinstance(classification, dict), "oriented requires classification evidence")
        _require_str(classification, "kind")
        _require_str(classification, "severity")
        confidence = classification.get("confidence")
        _require(isinstance(confidence, (int, float)) and not isinstance(confidence, bool) and 0 <= confidence <= 1, "classification.confidence must be 0..1")

    elif to_state == "decided":
        decision = evidence.get("decision")
        _require(isinstance(decision, dict), "decided requires decision evidence")
        level = decision.get("autonomy_level")
        _require(isinstance(level, int) and not isinstance(level, bool) and 0 <= level <= 3, "decision.autonomy_level must be 0..3")
        _require_str(decision, "risk")
        _require_bool(decision, "authorized", True)

    elif to_state == "reproducing":
        reproduction = evidence.get("reproduction")
        _require(isinstance(reproduction, dict), "reproducing requires reproduction evidence")
        _require_str(reproduction, "branch")

    elif to_state == "evidence_frozen":
        reproduction = evidence.get("reproduction")
        _require(isinstance(reproduction, dict), "evidence_frozen requires reproduction evidence")
        _require_sha(reproduction, "sha")
        _require(reproduction.get("result") == "red", "frozen reproduction must be red")
        _require_bool(reproduction, "tests_only", True)

    elif to_state == "repairing":
        repair = evidence.get("repair")
        _require(isinstance(repair, dict), "repairing requires repair evidence")
        _require_str(repair, "branch")
        frozen = _require_sha(repair, "reproduction_sha")
        _require(frozen == record["reproduction_sha"], "repair must consume the exact frozen reproduction SHA")

    elif to_state == "verifying":
        repair = evidence.get("repair")
        _require(isinstance(repair, dict), "verifying requires repair evidence")
        candidate = _require_sha(repair, "candidate_sha")
        _require(candidate != record["reproduction_sha"], "repair candidate must differ from frozen reproduction SHA")
        _require_bool(repair, "reproduction_unchanged", True)

    elif to_state == "reviewed":
        review = evidence.get("review")
        _require(isinstance(review, dict), "reviewed requires review evidence")
        reviewed = _require_sha(review, "reviewed_sha")
        _require(reviewed == record["candidate_sha"], "review must bind the exact candidate SHA")
        _require(review.get("disposition") == "PASS", "independent review disposition must be PASS")
        _require_bool(review, "engineering_ready", True)

    elif to_state == "release_authorized":
        release = evidence.get("release")
        _require(isinstance(release, dict), "release_authorized requires release evidence")
        candidate = _require_sha(release, "candidate_sha")
        ci_sha = _require_sha(release, "ci_verified_sha")
        reviewed = _require_sha(release, "reviewed_sha")
        _require(candidate == record["candidate_sha"], "release candidate SHA is stale")
        _require(ci_sha == candidate, "CI evidence must bind candidate SHA")
        _require(reviewed == record["reviewed_sha"] == candidate, "review evidence must bind candidate SHA")
        _require_bool(release, "authorized", True)

    elif to_state == "deployed":
        deployment = evidence.get("deployment")
        _require(isinstance(deployment, dict), "deployed requires deployment evidence")
        deployed = _require_sha(deployment, "sha")
        _require(deployed == record["candidate_sha"], "deployment SHA must equal authorized candidate SHA")
        _require(deployment.get("environment") == "production", "deployment environment must be production")
        _require_str(deployment, "deployment_id")

    elif to_state == "production_probation":
        probation = evidence.get("probation")
        _require(isinstance(probation, dict), "production_probation requires probation evidence")
        _require_str(probation, "started_at")
        checks = probation.get("required_checks")
        _require(
            isinstance(checks, list) and len(checks) > 0 and all(isinstance(x, str) and bool(x.strip()) for x in checks),
            "probation.required_checks must be a nonempty string array",
        )

    elif to_state == "healthy":
        verification = evidence.get("verification")
        _require(isinstance(verification, dict), "healthy requires verification evidence")
        verified = _require_sha(verification, "sha")
        _require(verified == record["deployed_sha"], "production verification must bind deployed SHA")
        _require(verification.get("result") == "PASS", "production verification must PASS")
        _require_sha256(verification, "evidence_sha256")

    elif to_state == "rollback_authorized":
        rollback = evidence.get("rollback")
        _require(isinstance(rollback, dict), "rollback_authorized requires rollback evidence")
        current = _require_sha(rollback, "current_sha")
        prior = _require_sha(rollback, "prior_known_good_sha")
        _require(current == record["deployed_sha"], "rollback current_sha must equal deployed SHA")
        _require(prior != current, "prior known-good SHA must differ from failed deployed SHA")
        _require_bool(rollback, "authorized", True)
        _require_bool(rollback, "schema_compatible", True)

    elif to_state == "rolled_back":
        rollback = evidence.get("rollback")
        _require(isinstance(rollback, dict), "rolled_back requires rollback evidence")
        target = _require_sha(rollback, "target_sha")
        _require(target == record["prior_known_good_sha"], "rollback target must equal authorized prior-known-good SHA")
        _require(rollback.get("result") == "success", "rollback result must be success")

    elif to_state == "recovery_verified":
        verification = evidence.get("verification")
        _require(isinstance(verification, dict), "recovery_verified requires verification evidence")
        verified = _require_sha(verification, "sha")
        _require(verified == record["prior_known_good_sha"], "recovery verification must bind rollback target SHA")
        _require(verification.get("result") == "PASS", "recovery verification must PASS")
        _require_sha256(verification, "evidence_sha256")

    elif to_state == "learning":
        learning = evidence.get("learning")
        _require(isinstance(learning, dict), "learning requires learning evidence")
        lesson_id = learning.get("lesson_id")
        summary = learning.get("summary")
        has_lesson = isinstance(lesson_id, str) and bool(lesson_id.strip())
        has_summary = isinstance(summary, str) and bool(summary.strip())
        _require(has_lesson or has_summary, "learning requires a nonempty lesson_id or summary")
        _require_str(learning, "durable_improvement")

    elif to_state == "closed":
        closure = evidence.get("closure")
        _require(isinstance(closure, dict), "closed requires closure evidence")
        expected = record.get("resolution_path")
        _require(expected in {"healthy", "rolled_back"}, "closure requires a deterministically bound resolution path")
        _require(closure.get("resolution") == expected, f"closure resolution must match completed path: {expected}")
        _require_str(closure, "summary")

    elif to_state == "escalated":
        escalation = evidence.get("escalation")
        _require(isinstance(escalation, dict), "escalated requires escalation evidence")
        _require_str(escalation, "reason")


def _apply_bound_fields(
    record: dict[str, Any],
    to_state: str,
    evidence: dict[str, Any],
    *,
    from_state: str | None = None,
) -> None:
    if to_state == "evidence_frozen":
        record["reproduction_sha"] = evidence["reproduction"]["sha"]
    elif to_state == "verifying":
        record["candidate_sha"] = evidence["repair"]["candidate_sha"]
    elif to_state == "reviewed":
        record["reviewed_sha"] = evidence["review"]["reviewed_sha"]
    elif to_state == "deployed":
        record["deployed_sha"] = evidence["deployment"]["sha"]
    elif to_state == "rollback_authorized":
        record["prior_known_good_sha"] = evidence["rollback"]["prior_known_good_sha"]
    elif to_state == "learning":
        if from_state == "healthy":
            record["resolution_path"] = "healthy"
        elif from_state == "recovery_verified":
            record["resolution_path"] = "rolled_back"
        else:
            raise OperationError("learning must follow healthy or recovery_verified")


def transition_record(
    record: dict[str, Any],
    *,
    to_state: str,
    evidence: dict[str, Any],
    actor: str = "deterministic-controller",
) -> dict[str, Any]:
    validate_record(record)
    _require(to_state in ALL_STATES, f"unknown target state: {to_state}")
    current = record["state"]
    _require(to_state in ALLOWED_TRANSITIONS[current], f"illegal transition: {current} -> {to_state}")
    _require(isinstance(evidence, dict), "evidence must be an object")
    _require(isinstance(actor, str) and bool(actor.strip()), "actor is required")

    _validate_transition_evidence(record, to_state, evidence)
    updated = deepcopy(record)
    sequence = updated["sequence"] + 1
    previous = updated["events"][-1]["event_sha256"]
    event = _build_event(
        sequence=sequence,
        from_state=current,
        to_state=to_state,
        actor=actor,
        evidence=evidence,
        previous_event_sha256=previous,
    )
    updated["events"].append(event)
    updated["state"] = to_state
    updated["sequence"] = sequence
    _apply_bound_fields(updated, to_state, evidence, from_state=current)
    validate_record(updated)
    return updated


def validate_record(record: dict[str, Any]) -> None:
    _require(isinstance(record, dict), "record must be an object")
    _require(record.get("version") == 1, "record version must be 1")
    _require(bool(OP_ID_RE.fullmatch(str(record.get("operation_id", "")))), "invalid operation_id")
    _require(bool(REPO_RE.fullmatch(str(record.get("repository", "")))), "invalid repository")
    _require(isinstance(record.get("incident_issue"), int) and record["incident_issue"] > 0, "invalid incident_issue")
    _require(record.get("state") in ALL_STATES, "invalid state")
    _require(record.get("resolution_path") in {None, "healthy", "rolled_back"}, "invalid resolution_path")
    events = record.get("events")
    _require(isinstance(events, list) and len(events) >= 1, "events must be a nonempty array")
    _require(record.get("sequence") == len(events) - 1, "record sequence does not match event count")

    prior_digest = None
    prior_state = None
    replay: dict[str, Any] = {
        "operation_id": None,
        "repository": None,
        "incident_issue": None,
        "production_before_sha": None,
        "reproduction_sha": None,
        "candidate_sha": None,
        "reviewed_sha": None,
        "deployed_sha": None,
        "prior_known_good_sha": None,
        "resolution_path": None,
    }
    for idx, event in enumerate(events):
        _require(isinstance(event, dict), f"event {idx} must be an object")
        _require(event.get("sequence") == idx, f"event {idx} sequence mismatch")
        expected_from = None if idx == 0 else prior_state
        _require(event.get("from") == expected_from, f"event {idx} from-state mismatch")
        to_state = event.get("to")
        _require(to_state in ALL_STATES, f"event {idx} has invalid target state")
        if idx == 0:
            _require(to_state == "observed", "first event must initialize observed state")
        else:
            _require(to_state in ALLOWED_TRANSITIONS[prior_state], f"event {idx} encodes illegal transition")
        _require(event.get("previous_event_sha256") == prior_digest, f"event {idx} previous digest mismatch")
        base = {
            "sequence": event.get("sequence"),
            "from": event.get("from"),
            "to": event.get("to"),
            "actor": event.get("actor"),
            "evidence": event.get("evidence"),
            "previous_event_sha256": event.get("previous_event_sha256"),
        }
        digest = _event_digest(base)
        _require(event.get("event_sha256") == digest, f"event {idx} digest mismatch")
        if idx == 0:
            event_evidence = event.get("evidence")
            _require(isinstance(event_evidence, dict), "genesis evidence must be an object")
            operation_id = _require_str(event_evidence, "operation_id")
            repository = _require_str(event_evidence, "repository")
            incident_issue = event_evidence.get("incident_issue")
            _require(bool(OP_ID_RE.fullmatch(operation_id)), "invalid genesis operation_id")
            _require(bool(REPO_RE.fullmatch(repository)), "invalid genesis repository")
            _require(isinstance(incident_issue, int) and incident_issue > 0, "invalid genesis incident_issue")
            _require_str(event_evidence, "source_type")
            _require_str(event_evidence, "signal")
            replay["operation_id"] = operation_id
            replay["repository"] = repository
            replay["incident_issue"] = incident_issue
            if event_evidence.get("production_before_sha") is not None:
                _require(bool(SHA_RE.fullmatch(event_evidence["production_before_sha"])), "invalid initial production SHA")
                replay["production_before_sha"] = event_evidence["production_before_sha"]
        else:
            shadow = {**record, **replay, "state": prior_state}
            _validate_transition_evidence(shadow, to_state, event.get("evidence") or {})
            _apply_bound_fields(replay, to_state, event.get("evidence") or {}, from_state=prior_state)
        prior_digest = digest
        prior_state = to_state

    _require(record["state"] == prior_state, "record state does not match last event")
    for key, value in replay.items():
        _require(record.get(key) == value, f"top-level bound field {key} does not match event history")


def _load_json(value: str) -> Any:
    if value == "-":
        return json.load(sys.stdin)
    path = Path(value)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def _write_json(value: dict[str, Any], output: str | None) -> None:
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create an observed operation record")
    init.add_argument("--operation-id", required=True)
    init.add_argument("--repository", required=True)
    init.add_argument("--incident-issue", type=int, required=True)
    init.add_argument("--source-type", required=True)
    init.add_argument("--signal", required=True)
    init.add_argument("--production-before-sha")
    init.add_argument("--output")

    trans = sub.add_parser("transition", help="apply one fail-closed state transition")
    trans.add_argument("--record", required=True, help="record JSON file, '-' for stdin, or inline JSON")
    trans.add_argument("--to", required=True, choices=ALL_STATES)
    trans.add_argument("--evidence", required=True, help="evidence JSON file or inline JSON")
    trans.add_argument("--actor", default="deterministic-controller")
    trans.add_argument("--output")

    val = sub.add_parser("validate", help="validate structure, hash chain, state path, identity, and SHA bindings")
    val.add_argument("--record", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = init_record(
                operation_id=args.operation_id,
                repository=args.repository,
                incident_issue=args.incident_issue,
                source_type=args.source_type,
                signal=args.signal,
                production_before_sha=args.production_before_sha,
            )
            _write_json(result, args.output)
        elif args.command == "transition":
            result = transition_record(
                _load_json(args.record),
                to_state=args.to,
                evidence=_load_json(args.evidence),
                actor=args.actor,
            )
            _write_json(result, args.output)
        else:
            validate_record(_load_json(args.record))
            print("PASS operation record")
        return 0
    except (OperationError, json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
