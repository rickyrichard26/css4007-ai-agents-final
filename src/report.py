"""Turn a validated result into readable text."""


def format_report(result: dict) -> str:
    lines = [
        f"Verdict: {result['verdict'].upper()}",
        f"Risk score: {result['risk_score']}/100",
        "",
        "Red flags:",
    ]
    if result["red_flags"]:
        lines += [f"  - [{f['type']}] {f['evidence']}" for f in result["red_flags"]]
    else:
        lines.append("  (none found)")
    lines += [
        "",
        "Explanation:",
        f"  {result['explanation']}",
        "",
        "Recommended action:",
        f"  {result['recommended_action']}",
    ]
    return "\n".join(lines)
