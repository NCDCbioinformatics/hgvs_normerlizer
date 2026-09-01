# hgvs_normerlizer

Tabular HGVS nomenclature normalization component of the CURE-NGS panel
harmonization framework.

> **Supported deployment:** use the unified
> [CURE-NGS Docker/OCI distribution](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework).
> This repository preserves historical package provenance and the reviewer bug
> fix. The supported container is published from the umbrella repository, not
> from this component repository; **No packages published** here is therefore
> expected.

## Role in the unified project

| Item | Value |
| --- | --- |
| Historical responsibility | Normalize HGVSc, HGVSp, and HGVSp-short fields in CSV/TSV/XLSX tables |
| Supported command | `cure-ngs normalize-hgvs-table` |
| Latest audited component release | `hgvsnorm-cli-0.2.2.tar` |
| Reviewer regression | CSV output uses `args.sep`; the erroneous `args.spep` path is tested |

## Install the supported Docker distribution

Install [Docker Desktop](https://docs.docker.com/desktop/) or
[Docker Engine](https://docs.docker.com/engine/install/), then pull the public
core image without a GitHub login:

```bash
docker pull ghcr.io/ncdcbioinformatics/cure-ngs-harmonizer:0.2.3-core
```

To build the identical `v0.2.3` release source instead:

```bash
git clone --branch v0.2.3 --depth 1 https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework.git
cd cure-ngs-panel-harmonization-framework
docker build --file docker/Dockerfile.core --tag cure-ngs-harmonizer:0.2.3-core .
```

The supported container is the umbrella repository's audited
[`v0.2.3` distribution](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/releases/tag/v0.2.3).

## Verify and run this capability

The full reviewer walkthrough includes the CSV separator regression:

```bash
git clone --branch v0.2.3 --depth 1 https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework.git
cd cure-ngs-panel-harmonization-framework
bash scripts/run_reviewer_demo.sh
```

Direct component command:

```bash
mkdir -p output
chmod 0777 output  # Linux: writable by the image's non-root UID 10001
docker run --rm \
  --volume "$PWD/examples:/examples:ro" \
  --volume "$PWD/output:/data/output" \
  ghcr.io/ncdcbioinformatics/cure-ngs-harmonizer:0.2.3-core \
  normalize-hgvs-table \
  /examples/synthetic/hgvs_input.csv \
  /data/output/hgvs.normalized.csv --delimiter comma
```

The output retains the original cells, records normalized values, and writes a
provenance manifest.

## Historical standalone package

The `hgvsnorm-cli-0.2.2.tar.gz` asset remains available for users who need the
historical command:

```bash
python3 -m pip install hgvsnorm-cli-0.2.2.tar.gz
hgvsnorm --excel-in input.xlsx --sheet 0 \
  --excel-out output.normalized.xlsx --threads 16
```

For manuscript reproduction, use the consolidated container and automated
regression suite instead of creating an unpinned Python environment.

## Documentation and test data

- [Project structure](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/blob/main/docs/PROJECT_STRUCTURE.md)
- [HGVS normalization commands](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/blob/main/docs/COMMAND_REFERENCE.md#structured-hgvs-or-report-derived-route)
- [CSV regression fixture](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/blob/main/examples/synthetic/hgvs_input.csv)
- [Reviewer reproduction checklist](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/blob/main/docs/REVIEWER_REPRODUCTION.md)
- [Clean public-image validation](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/actions/runs/33350796468)

License: MIT. No CURE-NGS patient-level data are distributed here.
