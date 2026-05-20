from pathlib import Path

def main():
    src=Path("results/runtime_report_v1_1.md")
    out=Path("results/CTG_v1_1_COMBINED_REPORT.md")
    out.write_text(src.read_text(encoding="utf-8"),encoding="utf-8")
    print(out)
if __name__=="__main__": main()
