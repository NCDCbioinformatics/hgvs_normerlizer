
import argparse, sys, os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import normalize_field

def _normalize_series_with_audit(series: pd.Series, kind: str, threads: int):
    """Return lists: new_vals, changed_flags, reasons"""
    vals = series.tolist()
    new_vals = [None]*len(vals)
    changed = [False]*len(vals)
    reasons = [""]*len(vals)

    def worker(i):
        v = vals[i]
        new, rs = normalize_field(v, kind)
        chg = (str(v) if v is not None else "") != (str(new) if new is not None else "")
        return (i, new, chg or bool(rs), ";".join(rs) if rs else "")

    if threads <= 1 or len(vals) < 1000:
        # small data → serial is faster
        for i in range(len(vals)):
            i2, nv, ch, rs = worker(i)
            new_vals[i2] = nv; changed[i2] = ch; reasons[i2] = rs
    else:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futs = [ex.submit(worker, i) for i in range(len(vals))]
            for f in as_completed(futs):
                i2, nv, ch, rs = f.result()
                new_vals[i2] = nv; changed[i2] = ch; reasons[i2] = rs

    return new_vals, changed, reasons

def _apply_with_audit(df: pd.DataFrame, col: str, kind: str, threads: int) -> pd.DataFrame:
    before_col = f"{col}_before"
    changed_col = f"{col}_changed"
    reason_col = f"{col}_change_reason"
    if before_col not in df.columns:
        df[before_col] = df[col] if col in df.columns else None
    else:
        df[before_col] = df[col] if col in df.columns else df[before_col]

    series = df[col] if col in df.columns else pd.Series([None]*len(df))
    new_vals, changed_flags, reasons_all = _normalize_series_with_audit(series, kind, threads)
    df[col] = new_vals
    df[changed_col] = changed_flags
    df[reason_col] = reasons_all
    return df

def normalize_columns(df: pd.DataFrame,
                      p_cols = ("HGVSp","HGVSp_short"),
                      c_cols = ("HGVSc",),
                      threads: int = 8) -> pd.DataFrame:
    for col in p_cols:
        if col in df.columns:
            df = _apply_with_audit(df, col, kind="p", threads=threads)
    for col in c_cols:
        if col in df.columns:
            df = _apply_with_audit(df, col, kind="c", threads=threads)
    return df

def main():
    p = argparse.ArgumentParser(description="Normalize HGVS strings (c./p.) with per-column change tracking (parallel)")
    io = p.add_argument_group("I/O")
    io.add_argument("--excel-in", help="Input Excel (.xlsx)")
    io.add_argument("--sheet", default="0", help="Excel sheet index or name (default: 0)")
    io.add_argument("--excel-out", help="Output Excel (.xlsx)")
    io.add_argument("--in", dest="in_file", help="Input TSV/CSV")
    io.add_argument("--out", dest="out_file", help="Output TSV/CSV")
    io.add_argument("--sep", default="\\t", help="Field separator for TSV/CSV (default: tab)")

    opts = p.add_argument_group("Options")
    opts.add_argument("--p-cols", default="HGVSp,HGVSp_short", help="Comma-separated protein-like columns")
    opts.add_argument("--c-cols", default="HGVSc", help="Comma-separated coding-like columns")
    opts.add_argument("--threads", type=int, default=8, help="Parallel threads (default: 8)")

    args = p.parse_args()
    p_cols = [x for x in (args.p_cols.split(",") if args.p_cols else []) if x]
    c_cols = [x for x in (args.c_cols.split(",") if args.c_cols else []) if x]

    if args.excel_in:
        sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
        df = pd.read_excel(args.excel_in, sheet_name=sheet, engine="openpyxl")
        res = normalize_columns(df, p_cols=p_cols, c_cols=c_cols, threads=args.threads)
        if args.excel_out:
            res.to_excel(args.excel_out, index=False)
            print(f"Wrote: {args.excel_out}")
        else:
            outp = os.path.splitext(args.excel_in)[0] + ".normalized.tsv"
            res.to_csv(outp, sep="\\t", index=False)
            print(f"Wrote: {outp}")
        return

    if args.in_file and args.out_file:
        df = pd.read_csv(args.in_file, sep=args.sep)
        res = normalize_columns(df, p_cols=p_cols, c_cols=c_cols, threads=args.threads)
        res.to_csv(args.out_file, sep=args.spep, index=False)
        print(f"Wrote: {args.excel_out}")
        return

    p.print_help()
    sys.exit(2)
