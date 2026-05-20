from typing import Dict, Any
from policy_loader import load_policy


def judge_transition(t: Dict[str, Any], policy: Dict[str, Any] | None = None) -> Dict[str, Any]:
    policy = policy or load_policy()
    thresholds = policy.get("thresholds", {})
    ctype = t.get("command_type", "unknown_command")
    risk = float(t.get("risk", 0.4))
    rec = float(t.get("recoverability", 0.5))
    bp = float(t.get("boundary_pressure", risk))
    fcr = float(t.get("future_collapse_risk", risk))

    score = max(0.0, min(1.0, rec * (1.0-risk) * (1.0-0.35*bp) * (1.0-0.35*fcr)))

    block_types = {"self_modification_command","log_deletion_command","system_overwrite_command","destructive_shell_command"}
    hold_types = {"credential_access_command","external_transmission_command","pipe_execution_command","script_execution_command","network_download_command","package_install_command","git_credential_command","unknown_command"}

    if ctype in block_types or rec <= thresholds.get("block_max_recoverability",0.22) or bp >= thresholds.get("high_boundary_pressure",0.82):
        decision = "BLOCK"
    elif ctype in hold_types or fcr >= thresholds.get("high_future_collapse_risk",0.78) or score < thresholds.get("go_min",0.78):
        decision = "HOLD"
    else:
        decision = "GO"

    return {**t, "admissibility_score": round(score,4), "decision": decision,
            "kernel": "Permit(T)=1[C(S_t,T,S_{t+1})=1]",
            "version": policy.get("version","1.1")}
