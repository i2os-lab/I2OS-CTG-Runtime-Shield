# I2OS-CTG Runtime Shield v1.1

Dry-run transition governance prototype
for AI agent runtime security.

Author:
Masayuki Ando (ANDOM)
Independent Researcher, Japan

CTG does **not** execute commands. It analyzes command-like actions as state transitions and classifies them into:

```text
GO / HOLD / REPAIR / BLOCK
```

Core principle:

```text
Permit(T)=1[C(S_t,T,S_{t+1})=1]
```

A transition is permitted only when the movement from the current state to the next state satisfies admissibility constraints.

## v1.1 Test Expansion Edition

This release expands runtime test coverage from the v1.0 baseline to 39 tests across:

- PowerShell
- Windows dangerous operations
- Git credential operations
- Python / Node inline execution
- SSH private key access
- API key / token / `.env` access
- System overwrite
- Log deletion
- External transmission
- Network exfiltration
- Self-modification
- Unknown command fallback

## Run

```bash
python runtime_judge.py
python dashboard.py
```

Open:

```text
results/ctg_dashboard_v1_1.html
```

## Current target metrics

```text
Runtime Pass Rate: 100.0%
Type Pass Rate: 100.0%
False GO: 0
False BLOCK: 0
```

## Positioning

This is not malware detection.
This is not simple command filtering.

It is transition governance.

Admissibility before execution.
Continuity before expansion.
Recovery before autonomy.

## Limitations

This is a dry-run research prototype, not production security software. Commands are analyzed as strings and never executed. Production use would require independent security review, sandboxing, OS-specific hardening, bypass testing, logging, and compliance review.
