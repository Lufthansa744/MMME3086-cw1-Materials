"""Process verified Fluent force exports without changing raw inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import statistics
import sys


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value, label):
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def unit_vector(value, label):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{label} must contain three numbers")
    vector = [finite(x, label) for x in value]
    if not math.isclose(dot(vector, vector), 1.0, abs_tol=1e-8):
        raise ValueError(f"{label} must be a unit vector")
    return vector


def load_metadata(path):
    meta = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(meta.get("case_id"), str) or not meta["case_id"].strip():
        raise ValueError("case_id must be nonempty")
    scalar_keys = ["density_kg_m3", "reference_speed_m_s", "reference_area_m2"]
    for key in scalar_keys:
        meta[key] = finite(meta[key], key)
        if meta[key] <= 0:
            raise ValueError(f"{key} must be positive")
    if not math.isclose(meta["reference_speed_m_s"], 50.9, abs_tol=1e-9):
        raise ValueError("reference speed must match the authorised 50.9 m/s")
    for key in ["drag_direction", "lift_direction"]:
        meta[key] = unit_vector(meta[key], key)
    if abs(dot(meta["drag_direction"], meta["lift_direction"])) > 1e-8:
        raise ValueError("lift and drag directions must be perpendicular")
    if not isinstance(meta.get("force_definition"), str) or not meta["force_definition"].strip():
        raise ValueError("force_definition is required")
    evidence = meta.get("evidence", {})
    required = scalar_keys + ["drag_direction", "lift_direction", "force_definition", "native_force_source"]
    if any(key not in evidence for key in required):
        raise ValueError("every physical input, force definition and native_force_source needs evidence")
    resolved = {}
    for key, item in evidence.items():
        if not isinstance(item.get("locator"), str) or not item["locator"].strip():
            raise ValueError(f"evidence locator missing: {key}")
        source = Path(item["path"])
        if not source.is_absolute():
            source = path.parent / source
        source = source.resolve(strict=True)
        if not source.is_file():
            raise ValueError(f"evidence must be a file: {source}")
        resolved[key] = {"path": str(source), "locator": item["locator"], "sha256": sha256(source)}
    return meta, resolved


def verify_conversion(meta, evidence, forces_path):
    """Require a preserved native source and an explicit transformation record."""
    if "native_force_source" not in evidence:
        raise ValueError("native_force_source evidence is required")
    conversion = meta.get("conversion")
    if not isinstance(conversion, dict) or conversion.get("mode") not in ["identity", "script"]:
        raise ValueError("conversion.mode must be identity or script")
    mapping = conversion.get("column_mapping")
    columns = {"iteration": "iteration", "Fx_N": "N", "Fy_N": "N", "Fz_N": "N"}
    if not isinstance(mapping, dict) or any(key not in mapping for key in columns):
        raise ValueError("conversion.column_mapping must cover iteration and all three force columns")
    for key, target_units in columns.items():
        item = mapping[key]
        fields = ["source", "expression", "source_units", "target_units"]
        if not isinstance(item, dict) or any(not isinstance(item.get(f), str) or not item[f].strip() for f in fields):
            raise ValueError(f"conversion mapping for {key} needs source, expression (including sign), source_units and target_units")
        if item["target_units"] != target_units:
            raise ValueError(f"target units for {key} must be {target_units}")
        if conversion["mode"] == "identity" and (
            item["source"] != key or item["expression"] != key or item["source_units"] != target_units
        ):
            raise ValueError(f"identity conversion must leave {key} and its units unchanged")
    if conversion["mode"] == "identity":
        if sha256(forces_path) != evidence["native_force_source"]["sha256"]:
            raise ValueError("identity conversion requires byte-identical native and input CSV files")
    else:
        if "conversion_script" not in evidence:
            raise ValueError("script conversion requires preserved conversion_script evidence")
        if forces_path.resolve() == Path(evidence["native_force_source"]["path"]).resolve():
            raise ValueError("script conversion must preserve the native file separately from its derived CSV")


def diagnostic(values, iterations):
    n = len(values)
    xbar = statistics.mean(iterations)
    ybar = statistics.mean(values)
    denominator = sum((x - xbar) ** 2 for x in iterations)
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(iterations, values)) / denominator if denominator else None
    return {"samples": n, "mean": ybar, "minimum": min(values), "maximum": max(values),
            "range": max(values) - min(values), "slope_per_iteration": slope}


def plot_svg(rows, case_id, path):
    width, height = 1000, 600
    left, right, top, bottom = 95, 30, 60, 85
    xmin, xmax = rows[0]["iteration"], rows[-1]["iteration"]
    values = [r[k] for r in rows for k in ("CL", "CD")]
    ymin, ymax = min(values), max(values)
    pad = (ymax - ymin) * 0.08 or max(abs(ymax) * 0.08, 0.01)
    ymin, ymax = ymin - pad, ymax + pad
    def px(x):
        return left + (x - xmin) / (xmax - xmin or 1) * (width - left - right)
    def py(y):
        return height - bottom - (y - ymin) / (ymax - ymin) * (height - top - bottom)
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                '<rect width="100%" height="100%" fill="white"/>',
                '<g font-family="Arial,sans-serif" font-size="17" fill="#202020">',
                f'<text x="{left}" y="30" font-size="22">{html.escape(case_id)}: force coefficient history</text>']
    for i in range(6):
        y = ymin + (ymax - ymin) * i / 5
        x = xmin + (xmax - xmin) * i / 5
        elements.extend([f'<line x1="{left}" y1="{py(y):.3f}" x2="{width-right}" y2="{py(y):.3f}" stroke="#dddddd"/>',
                         f'<text x="{left-10}" y="{py(y)+6:.3f}" text-anchor="end">{y:.5g}</text>',
                         f'<text x="{px(x):.3f}" y="{height-bottom+28}" text-anchor="middle">{x:.6g}</text>'])
    elements.extend([f'<path d="M{left},{top} V{height-bottom} H{width-right}" fill="none" stroke="black"/>',
                     f'<text x="{width/2}" y="{height-20}" text-anchor="middle">Iteration</text>',
                     f'<text x="22" y="{height/2}" text-anchor="middle" transform="rotate(-90,22,{height/2})">Force coefficient</text>'])
    for key, color, offset in [("CL", "#0072b2", 0), ("CD", "#d55e00", 90)]:
        points = " ".join(f'{px(row["iteration"]):.3f},{py(row[key]):.3f}' for row in rows)
        elements.extend([f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>',
                         f'<text x="{width-right-180+offset}" y="{top-12}" fill="{color}">{key}</text>'])
    elements.append('</g></svg>')
    path.write_text("\n".join(elements), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forces", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--window", default=100, type=int)
    args = parser.parse_args()
    if args.window < 2:
        raise ValueError("diagnostic window must contain at least two samples")
    forces_path = args.forces.resolve(strict=True)
    metadata_path = args.metadata.resolve(strict=True)
    meta, evidence = load_metadata(metadata_path)
    verify_conversion(meta, evidence, forces_path)
    denominator = 0.5 * meta["density_kg_m3"] * meta["reference_speed_m_s"] ** 2 * meta["reference_area_m2"]
    rows = []
    with forces_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = ["iteration", "Fx_N", "Fy_N", "Fz_N"]
        if not reader.fieldnames or not set(required).issubset(reader.fieldnames):
            raise ValueError(f"CSV requires columns {required}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("CSV column names must be unique")
        for line, raw in enumerate(reader, 2):
            row = {key: finite(raw[key], f"row {line}: {key}") for key in required}
            if rows and row["iteration"] <= rows[-1]["iteration"]:
                raise ValueError(f"iterations must strictly increase (row {line}); split restarted histories explicitly")
            force = [row[key] for key in ["Fx_N", "Fy_N", "Fz_N"]]
            row.update(source_csv_line=line, CD=dot(force, meta["drag_direction"]) / denominator,
                       CL=dot(force, meta["lift_direction"]) / denominator)
            rows.append(row)
    if len(rows) < 2:
        raise ValueError("at least two actual monitor samples are required")
    output = args.output.resolve()
    names = ["coefficients.csv", "audit.json", "force_coefficients.svg"]
    if any((output / name).exists() for name in names):
        raise ValueError("output already exists; choose a new directory to preserve previous processing")
    if forces_path in [output / n for n in names] or metadata_path in [output / n for n in names]:
        raise ValueError("outputs cannot replace inputs")
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "coefficients.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    svg_path = output / "force_coefficients.svg"
    plot_svg(rows, meta["case_id"], svg_path)
    window = rows[-args.window:]
    audit = {"case_id": meta["case_id"], "metadata": meta, "evidence": evidence,
             "inputs": [{"path": str(p), "sha256": sha256(p)} for p in [forces_path, metadata_path, Path(__file__).resolve()]],
             "normalising_force_N": denominator, "sample_count": len(rows),
             "diagnostic_window_start_iteration": window[0]["iteration"],
             "diagnostic_window_end_iteration": window[-1]["iteration"],
             "diagnostics": {key: diagnostic([r[key] for r in window], [r["iteration"] for r in window]) for key in ["CL", "CD"]},
             "convergence_assessment": "Not determined by this processor; requires independent solver and physics review",
             "outputs": [{"path": str(p), "sha256": sha256(p)} for p in [csv_path, svg_path]]}
    (output / "audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Processed {len(rows)} actual samples for {meta['case_id']}: {output}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError, json.JSONDecodeError) as error:
        print(f"Processing refused: {error}", file=sys.stderr)
        raise SystemExit(2)
