import re
from dataclasses import dataclass, asdict
from typing import Dict, Any
from policy_loader import load_policy

@dataclass
class RuntimeTransition:
    raw_command: str
    command_type: str
    intent: str
    risk: float
    recoverability: float
    boundary_pressure: float
    future_collapse_risk: float
    reason: str


def _norm(cmd: str) -> str:
    return re.sub(r"\s+", " ", cmd.strip())


def _contains_any(text: str, hints) -> bool:
    low = text.lower()
    return any(h.lower() in low for h in hints)


def _writes_to_self(cmd: str, policy: Dict[str, Any]) -> bool:
    low = cmd.lower()
    write_ops = [">", ">>", "out-file", "set-content", "add-content", "copy ", "cp ", "move ", "mv "]
    return any(op in low for op in write_ops) and _contains_any(low, policy.get("self_files", []))


def classify_command(command: str, policy: Dict[str, Any] | None = None) -> RuntimeTransition:
    policy = policy or load_policy()
    cmd = _norm(command)
    low = cmd.lower()
    weights = policy.get("risk_weights", {})
    cred_hints = policy.get("credential_hints", [])
    exfil_hints = policy.get("exfiltration_hints", [])
    log_hints = policy.get("log_hints", [])
    protected = policy.get("protected_paths", [])

    def make(t, intent, reason, recover=0.5, bp=None, fcr=None):
        risk = float(weights.get(t, weights.get("unknown_command", 0.4)))
        return RuntimeTransition(cmd, t, intent, risk, recover, bp if bp is not None else risk, fcr if fcr is not None else risk, reason)

    # Priority 1: self-modification / system overwrite / log deletion
    if _writes_to_self(cmd, policy):
        return make("self_modification_command", "modify_guarded_runtime_file", "attempts to write into CTG/runtime policy files", 0.05, 0.95, 0.92)
    if re.search(r"\b(format|mkfs|reg delete)\b", low) or "system32" in low and any(x in low for x in ["del", "remove-item", "rm "]):
        return make("system_overwrite_command", "overwrite_or_destroy_system_area", "targets system-level destructive area", 0.04, 0.96, 0.95)
    if any(x in low for x in ["rm -rf", "del /f", "del /q", "remove-item"] ) and _contains_any(low, log_hints):
        return make("log_deletion_command", "delete_logs_or_audit_trail", "attempts to delete logs/audit trail", 0.08, 0.90, 0.88)
    if any(x in low for x in ["rm -rf /", "rm -rf *", "remove-item c:\\", "del c:\\"]):
        return make("destructive_shell_command", "destructive_shell_operation", "broad destructive command pattern", 0.06, 0.93, 0.91)

    # Priority 2: credential / secret exposure, even through read-only forms
    if _contains_any(low, cred_hints):
        if any(x in low for x in ["git config --global credential.helper store", "git credential", ".git-credentials"]):
            return make("git_credential_command", "credential_persistence_or_access", "git credential storage/access pattern", 0.32, 0.76, 0.68)
        return make("credential_access_command", "access_sensitive_secret_material", "credential-like target detected", 0.35, 0.72, 0.64)
    if "print(os.environ)" in low or "get-childitem env:" in low or "set |" in low or re.search(r"\benv\b", low) and any(x in low for x in ["print", "cat", "type", "get-content"]):
        return make("credential_access_command", "expose_environment_variables", "environment variable exposure may include secrets", 0.36, 0.70, 0.62)

    # Priority 3: exfiltration / external transmission / pipe execution
    if _contains_any(low, exfil_hints):
        return make("external_transmission_command", "transmit_local_data_external", "external transmission/upload pattern", 0.28, 0.78, 0.80)
    if "| bash" in low or "| sh" in low or "iex" in low or "invoke-expression" in low:
        return make("pipe_execution_command", "download_or_pipe_into_execution", "pipe-to-execution pattern", 0.25, 0.77, 0.78)
    if any(x in low for x in ["curl ", "wget ", "invoke-webrequest", "start-bitstransfer"]):
        return make("network_download_command", "network_download", "network retrieval requires verification", 0.50, 0.55, 0.45)

    # Priority 4: script execution / package install
    if re.search(r"\bpython\b.*\-c", low) or re.search(r"\bpowershell\b", low) or re.search(r"\bnode\b.*\-e", low):
        return make("script_execution_command", "inline_script_execution", "inline script execution requires verification", 0.45, 0.55, 0.48)
    if any(x in low for x in ["pip install", "npm install", "apt install", "brew install", "choco install"]):
        return make("package_install_command", "package_installation", "package installation changes runtime environment", 0.50, 0.50, 0.45)

    # Priority 5: safe commands
    if low in [x.lower() for x in policy.get("safe_read_commands", [])] or re.fullmatch(r"(dir|ls|pwd|whoami|git status|git log --oneline)", low):
        return make("read_only_shell_command" if not low.startswith("git") else "safe_git_command", "read_only_observation", "safe read-only observation", 0.95, 0.08, 0.05)
    if re.fullmatch(r"(cd|cd \.|cd \.\.|pushd .+|popd)", low):
        return make("safe_navigation_command", "local_navigation", "local navigation without execution", 0.90, 0.08, 0.05)

    return make("unknown_command", "unknown_transition", "no high-confidence pattern matched", 0.55, 0.45, 0.40)


def analyze_command(command: str, policy_path="policies/policy.json") -> Dict[str, Any]:
    return asdict(classify_command(command, load_policy(policy_path)))
