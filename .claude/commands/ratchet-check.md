---
description: Run all four ratchet checks locally and report status
allowed-tools: Bash
---

You are running the four ratchet checks on the user's local working
copy. This is the same set CI runs on every PR.

## Procedure

Run each check in sequence. Don't run them in parallel — some emit
a lot of output and interleaving is confusing.

```bash
echo "=== Ratchet 1: Test count (Rule 3) ==="
./scripts/ci/check_test_ratchet.py

echo "=== Ratchet 2: Formal specs (Rule 10) ==="
./scripts/ci/check_spec_ratchet.py

echo "=== Ratchet 3: CI tripwires ==="
./scripts/ci/check_tripwire_ratchet.py

echo "=== Ratchet 4: Frontmatter coverage (Rule 12) ==="
./scripts/ci/check_frontmatter.py
```

## Reporting

After all four complete, summarize for the user in 4 lines:

```
Tests:        <current> / <baseline>  [PASS|FAIL|NO-OP]
Specs:        <current> / <baseline>  [PASS|FAIL|NO-OP]
Tripwires:    <current> / <baseline>  [PASS|FAIL]
Frontmatter:  <current> / <baseline>  [PASS|FAIL]
```

NO-OP means the baseline is empty — common right after bootstrap
before any sprint has run. The check script's exit code is 0 in
that case.

If any check failed, list which one(s) and what the failure said
(usually a "decreased by N" line).

Don't propose fixes unless the user asks. Reporting is the
default behavior here.

## Companion checks

The four ratchets above are the project-level numbers. The user
might also want to run the per-PR tripwires:

```bash
./scripts/ci/check_no_unwraps.py
./scripts/ci/check_no_mocks.py
./scripts/ci/check_audit_immutability.py
```

Offer to run these if the ratchet output suggests a recent code
change. Otherwise, mention them only if asked.
