from __future__ import annotations

import sys

from hgvsnorm_cli.cli import main


def test_csv_output_uses_requested_separator(tmp_path, monkeypatch):
    source = tmp_path / "input.csv"
    output = tmp_path / "output.csv"
    source.write_text("sample_id,HGVSc\nsample-000123,818g>a\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hgvsnorm",
            "--in",
            str(source),
            "--out",
            str(output),
            "--sep",
            ",",
        ],
    )
    main()

    rendered = output.read_text(encoding="utf-8")
    assert rendered.startswith("sample_id,HGVSc,")
    assert "sample-000123,c.818G>A," in rendered
