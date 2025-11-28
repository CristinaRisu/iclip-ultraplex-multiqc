#!/usr/bin/env python3
"""
Parse Ultraplex log files, generate a summary TSV and a barplot.

- Looks for logs under: demux_pcr*/**/*.log
- Extracts the last 5 summary lines from each log
- Writes: ultraplex_summary.tsv
- Writes: ultraplex_assigned_barplot_mqc.png (picked up by MultiQC)
"""

import sys
import re
import pathlib
import csv
import matplotlib.pyplot as plt


def parse_log(log_path):
    """Return (metrics_dict, last5_lines_list) for one Ultraplex log."""
    with open(log_path) as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip()]

    if len(lines) < 5:
        return None, []

    last5 = lines[-5:]

    metrics = {
        "log_path": str(log_path),
        "reads_processed": None,
        "seconds": None,
        "n_quality_trimmed": None,
        "pct_quality_trimmed": None,
        "n_adapter_trimmed": None,
        "pct_adapter_trimmed": None,
        "n_5p_bc_no_3p": None,
        "pct_5p_bc_no_3p": None,
        "n_assigned": None,
        "pct_assigned": None,
    }

    # 1) Demultiplexing complete! N reads processed in X seconds
    m = re.search(
        r"(\d+)\s+reads processed in\s+([\d\.]+)\s+seconds",
        last5[0],
    )
    if m:
        metrics["reads_processed"] = int(m.group(1))
        metrics["seconds"] = float(m.group(2))

    # 2) N (p%) reads quality trimmed
    m = re.search(
        r"(\d+)\s+\(([\d\.]+)%\)\s+reads quality trimmed",
        last5[1],
    )
    if m:
        metrics["n_quality_trimmed"] = int(m.group(1))
        metrics["pct_quality_trimmed"] = float(m.group(2))

    # 3) N (p%) reads adaptor trimmed
    m = re.search(
        r"(\d+)\s+\(([\d\.]+)%\)\s+reads adaptor trimmed",
        last5[2],
    )
    if m:
        metrics["n_adapter_trimmed"] = int(m.group(1))
        metrics["pct_adapter_trimmed"] = float(m.group(2))

    # 4) N (p%) reads with correct 5' bc but 3' bc not found
    m = re.search(
        r"(\d+)\s+\(([\d\.]+)%\)\s+reads with correct 5' bc but 3' bc not found",
        last5[3],
    )
    if m:
        metrics["n_5p_bc_no_3p"] = int(m.group(1))
        metrics["pct_5p_bc_no_3p"] = float(m.group(2))

    # 5) N (p%) reads correctly assigned to sample files
    m = re.search(
        r"(\d+)\s+\(([\d\.]+)%\)\s+reads correctly assigned to sample files",
        last5[4],
    )
    if m:
        metrics["n_assigned"] = int(m.group(1))
        metrics["pct_assigned"] = float(m.group(2))

    return metrics, last5


def main():
    if len(sys.argv) > 1:
        root = pathlib.Path(sys.argv[1])
    else:
        root = pathlib.Path.cwd()

    print(f"Searching for Ultraplex logs under: {root}")

    log_paths = sorted(root.glob("demux_pcr*/**/*.log"))
    if not log_paths:
        print("⚠ No .log files found under demux_pcr*/")
        sys.exit(1)

    rows = []
    for log_path in log_paths:
        # Use parent directory name (e.g. demux_pcr1) as sample id
        sample = log_path.parent.name

        metrics, last5 = parse_log(log_path)
        if metrics is None:
            print(f"⚠ Log too short, skipping: {log_path}")
            continue

        metrics["sample"] = sample
        metrics["log_last5"] = " | ".join(last5)
        rows.append(metrics)

    if not rows:
        print("⚠ No valid logs parsed.")
        sys.exit(1)

    # Sort rows by sample name
    rows.sort(key=lambda x: x["sample"])

    # Write TSV summary
    out_tsv = root / "ultraplex_summary.tsv"
    fieldnames = [
        "sample",
        "log_path",
        "reads_processed",
        "seconds",
        "n_quality_trimmed",
        "pct_quality_trimmed",
        "n_adapter_trimmed",
        "pct_adapter_trimmed",
        "n_5p_bc_no_3p",
        "pct_5p_bc_no_3p",
        "n_assigned",
        "pct_assigned",
        "log_last5",
    ]
    with open(out_tsv, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"✔ Summary written to: {out_tsv}")

    # Barplot with % assigned
    samples = [r["sample"] for r in rows]
    pct_assigned = [r["pct_assigned"] for r in rows]

    plt.figure(figsize=(10, 5))
    plt.bar(samples, pct_assigned)
    plt.ylabel("% reads assigned")
    plt.xlabel("Demux / pool (directory)")
    plt.title("Ultraplex - % reads correctly assigned")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_png = root / "ultraplex_assigned_barplot_mqc.png"
    plt.savefig(out_png, dpi=150)
    print(f"✔ Barplot saved to: {out_png}")


if __name__ == "__main__":
    main()
