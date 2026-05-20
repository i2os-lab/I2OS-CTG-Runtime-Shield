from ctg_engine import judge_transition
from runtime_hook import analyze_command

def judge_chain(commands):
    results=[]
    broken=False
    for c in commands:
        r=judge_transition(analyze_command(c))
        results.append(r)
        if r["decision"] in {"HOLD","BLOCK"}:
            broken=True
            break
    return {"chain_broken": broken, "results": results}
