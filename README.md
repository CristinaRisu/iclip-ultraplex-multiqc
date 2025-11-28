# iclip-ultraplex-multiqc
iCLIP Demultiplexing with Ultraplex and MultiQC

This repository provides a small but practical workflow to:

1. **Demultiplex iCLIP / iiCLIP libraries** using [Ultraplex](https://github.com/goodwright/ultraplex) and internal barcodes.
2. **Parse Ultraplex log files** to extract summary statistics (reads processed, % trimmed, % assigned, etc.).
3. **Generate a MultiQC report** that includes:
   - A custom table summarizing all Ultraplex metrics.
   - A barplot showing the percentage of correctly assigned reads per demultiplexed pool.

This is particularly useful for iCLIP libraries using RT primers with internal barcodes in the format  
`NNNN,XXXXX_0,W WW` (UMI + barcode + random bases).

---

## Requirements

- Python ≥ 3.8  
- MultiQC ≥ 1.10  
- matplotlib  
- Ultraplex installed (via conda or pip)


