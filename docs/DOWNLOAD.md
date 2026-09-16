# Install and verify

## Download

- Full data package (Hugging Face): https://huggingface.co/datasets/Zafrens/zscreen-pilot
- Code and documentation (GitHub): https://github.com/Zafrens/zscreen-pilot
- Archived release (Zenodo, resolves to the latest version): https://doi.org/10.5281/zenodo.22003566

Use the full package folder or matching full archive. Open a terminal in the extracted package root. Python 3.11 or later is supported:

```bash
python -m pip install -e .
python verify.py --full
```

The verifier checks every distributed file against the root [file_manifest.csv](../file_manifest.csv) and [MANIFEST.json](../MANIFEST.json), then checks data shapes, axes, IDs and current package objects. These two inventory files are excluded from their own checksum list: total files equal manifested files plus two. Recognized local virtual environments, caches and OS metadata are excluded; unlisted payloads and altered distributed files fail.

## Reference model

For the strict fixed-prediction check, use the verified CPU build:

```bash
python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[model]"
python models/predict.py --check-golden
```

The diagnostic applies its reference software thread count and restores the caller's setting. It does not require 12 hardware cores. [Model guide](../models/README.md).

To reproduce the complete dependency snapshot, use Python 3.11.14, install the CPU PyTorch build above, then run:

```bash
python -m pip install -r environment.lock
python -m pip install -e . --no-deps
```

For notebooks with supported dependency ranges, install `python -m pip install -e ".[notebooks]"`.

## Archive checksums

If supplied with the archive, `SHA256SUMS.txt` uses LF line endings. Run `sha256sum -c SHA256SUMS.txt` on Linux or `shasum -a 256 -c SHA256SUMS.txt` on macOS from the archive directory. On Windows compare `Get-FileHash -Algorithm SHA256` with the list.

A code/documentation review subset omits large inputs; use the full download for execution. [Start Here](../START_HERE.md) · [Data dictionary](DATA_DICTIONARY.md) · [Data access](ANALYSIS_ACCESS.md).
