import json
from pathlib import Path
from runtime_hook import analyze_command
from ctg_engine import judge_transition
from policy_loader import load_policy

TEST_FILE = Path("runtime_tests/runtime_tests_v1_1.json")
RESULT_FILE = Path("results/runtime_report_v1_1.json")
MD_FILE = Path("results/runtime_report_v1_1.md")

def main():
    policy=load_policy("policies/policy.json")
    tests=json.loads(TEST_FILE.read_text(encoding="utf-8"))
    rows=[]
    false_go=false_block=type_pass=decision_pass=0
    for item in tests:
        tr=analyze_command(item["command"], "policies/policy.json")
        judged=judge_transition(tr, policy)
        dp= judged["decision"] == item["expected_decision"]
        tp= judged["command_type"] == item["expected_type"]
        decision_pass += int(dp); type_pass += int(tp)
        false_go += int(judged["decision"]=="GO" and item["expected_decision"]!="GO")
        false_block += int(judged["decision"]=="BLOCK" and item["expected_decision"]!="BLOCK")
        rows.append({**item, **judged, "decision_pass":dp, "type_pass":tp})
    n=len(tests)
    summary={"version":"1.1","total_tests":n,"runtime_pass_rate":round(100*decision_pass/n,1),"type_pass_rate":round(100*type_pass/n,1),"false_go":false_go,"false_block":false_block}
    RESULT_FILE.parent.mkdir(exist_ok=True)
    RESULT_FILE.write_text(json.dumps({"summary":summary,"results":rows},indent=2),encoding="utf-8")
    md=["# I2OS-CTG Runtime Shield v1.1 Runtime Report","",f"Total Tests: {n}",f"Runtime Pass Rate: {summary['runtime_pass_rate']}%",f"Type Pass Rate: {summary['type_pass_rate']}%",f"False GO: {false_go}",f"False BLOCK: {false_block}","","| Command | Expected | Actual | Type | Pass |","|---|---:|---:|---|---:|"]
    for r in rows:
        md.append(f"| `{r['command']}` | {r['expected_decision']} | {r['decision']} | {r['command_type']} | {r['decision_pass'] and r['type_pass']} |")
    MD_FILE.write_text("\n".join(md),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
