#!/usr/bin/env bash
set -euo pipefail

# Base project directory (edit this)
BASE=/path/to/your/project

cd "$BASE"

# Create output directories for each pool
for i in {1..n}; do
    mkdir -p "demux_pcr${i}"
done

# Example Ultraplex commands (edit input and barcode files as needed)

ultraplex \
    -i file1.fastq.gz \
    -b barcodes_pcr1.csv \
    -o demux_pcr1/ultraplex_demux_pcr1 \
    -t 8 \
    --fiveprimemismatches 0

ultraplex \
    -i file2.fastq.gz \
    -b barcodes_pcr2.csv \
    -o demux_pcr2/ultraplex_demux_pcr2 \
    -t 8 \
    --fiveprimemismatches 0

# Repeat for other pools (file3 → demux_pcr3, etc.)
