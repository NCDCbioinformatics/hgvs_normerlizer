
import re
from typing import Optional, Tuple, List

def _strip(s: Optional[str]) -> Optional[str]:
    if s is None: return None
    x = str(s).strip()
    if x in ("", "None", "nan"): return None
    return x

# -------- Protein-like (HGVSp / HGVSp_short) --------

def normalize_hgvsp_like(x: Optional[str]) -> Tuple[Optional[str], List[str]]:
    """Returns (normalized_value, reasons)"""
    reasons: List[str] = []
    s0 = x
    s = _strip(x)
    if s is None:
        return None, reasons

    # remove spaces
    if " " in s:
        s = s.replace(" ", "")
        reasons.append("removed_spaces")

    # remove surrounding parentheses
    if re.match(r"^\(.*\)$", s):
        s = s[1:-1]
        reasons.append("removed_parentheses")

    # unify/add 'p.' prefix
    if s.lower().startswith("p."):
        if not s.startswith("p."):
            reasons.append("lowercased_prefix")
        s = "p." + s[2:]
    else:
        # Looks like protein change? (short or long)
        if re.match(r"^[A-Z][0-9]+([A-Z]|\*|=)(fs\*?[0-9]+)?$", s):
            s = "p." + s
            reasons.append("added_prefix_p")
        elif re.match(r"^([A-Z][a-z]{2})[0-9]+([A-Z][a-z]{2}|\*|=)(fs\*?[0-9]+)?$", s):
            s = "p." + s
            reasons.append("added_prefix_p")
        elif s.startswith("P."):
            s = "p." + s[2:]
            reasons.append("lowercased_prefix")
        elif s.startswith("P"):
            t = s[1:]
            if t.startswith("."):
                t = t[1:]
            s = "p." + t
            reasons.append("added_prefix_p")

    if s == s0:
        return s, []
    return s, reasons

# -------- Coding-like (HGVSc) --------

def normalize_hgvsc_like(x: Optional[str]) -> Tuple[Optional[str], List[str]]:
    """Returns (normalized_value, reasons). Normalize like c.818G>A from many forms."""
    reasons: List[str] = []
    s0 = x
    s = _strip(x)
    if s is None:
        return None, reasons

    if " " in s:
        s = s.replace(" ", "")
        reasons.append("removed_spaces")

    # remove surrounding parentheses
    import re as _re
    if _re.match(r"^\(.*\)$", s):
        s = s[1:-1]
        reasons.append("removed_parentheses")

    # Normalize c. prefix handling
    if s.lower().startswith("c."):
        body = s[2:]
        if not s.startswith("c."):
            reasons.append("lowercased_prefix")
    elif s.lower().startswith("c"):
        body = s[1:]
        if body.startswith("."):
            body = body[1:]
        reasons.append( "normalized_prefix_c")
    else:
        body = s

    # Pattern A: '818G>A'
    m = _re.match(r"^(\d+)([ACGTacgtn])>([ACGTacgtn])$", body)
    if m:
        pos, ref, alt = m.groups()
        refU, altU = ref.upper(), alt.upper()
        out = f"c.{int(pos)}{refU}>{altU}"
        if not s.lower().startswith("c."):
            reasons.append("added_prefix_c")
        if (ref != refU) or (alt != altU):
            reasons.append("uppercased_bases")
        return out, reasons

    # Pattern B: 'G818A' (ref + pos + alt)
    m = _re.match(r"^([ACGTacgtn])(\d+)([ACGTacgtn])$", body)
    if m:
        ref, pos, alt = m.groups()
        refU, altU = ref.upper(), alt.upper()
        out = f"c.{int(pos)}{refU}>{altU}"
        reasons.append("reordered_refposalt_to_posrefalt")
        if not s.lower().startswith("c."):
            reasons.append("added_prefix_c")
        if (ref != refU) or (alt != altU):
            reasons.append("uppercased_bases")
        return out, reasons

    # Pattern C: stray leading dot
    m = _re.match(r"^\.?([ACGTacgtn])(\d+)([ACGTacgtn])$", body)
    if m:
        ref, pos, alt = m.groups()
        refU, altU = ref.upper(), alt.upper()
        out = f"c.{int(pos)}{refU}>{altU}"
        reasons.append("reordered_refposalt_to_posrefalt")
        if not s.lower().startswith("c."):
            reasons.append("added_prefix_c")
        if (ref != refU) or (alt != altU):
            reasons.append("uppercased_bases")
        return out, reasons

    # Pattern D: already 'c.818G>A' but case issues
    m = _re.match(r"^[cC]\.(\d+)([ACGTacgtn])>([ACGTacgtn])$", s)
    if m:
        pos, ref, alt = m.groups()
        refU, altU = ref.upper(), alt.upper()
        out = f"c.{int(pos)}{refU}>{altU}"
        if not s.startswith("c."):
            reasons.append("lowercased_prefix")
        if (ref != refU) or (alt != altU):
            reasons.append("uppercased_bases")
        return out, reasons

    # If started with c/C but unknown form, at least standardize prefix
    if s.lower().startswith("c"):
        out = "c." + body
        if not s.startswith("c."):
            reasons.append("normalized_prefix_c")
        if out != s0:
            return out, reasons

    # No recognizable pattern; return original
    return s, []

def normalize_field(value: Optional[str], kind: str) -> Tuple[Optional[str], List[str]]:
    if kind == "p":
        return normalize_hgvsp_like(value)
    elif kind == "c":
        return normalize_hgvsc_like(value)
    else:
        return value, []
