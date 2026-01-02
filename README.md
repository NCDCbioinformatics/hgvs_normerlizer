# hgvs_normerlizer
<img width="2406" height="1335" alt="image" src="https://github.com/user-attachments/assets/1f8476f1-1f36-4edd-b130-31c39317f933" />

python3 -m pip install hgvsnorm-cli-0.2.2.tar.gz \

hgvsnorm --excel-in "/path/to/minimal_maf_test.xlsx" \
         --sheet 0 \
         --excel-out "/path/to/minimal_maf_test.normalized.xlsx" \
         --threads 16


# Feature Summary
- Unifying mutation nomenclature, which is written in various ways, into HGVS
- Basically it works on HGVSc, HGVSp, HGVSp_short and if possible it recognizes and fills each other complementarily.
- In cases where the nomenclature is not unified (323G>A, P.G125D, etc.), change to the standardized HGVS nomenclature.

