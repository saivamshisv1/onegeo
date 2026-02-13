from dataclasses import dataclass


@dataclass
class LasData:
    curves: list[str]
    depth: list[float]
    rows: list[dict[str, float | None]]


NULL_SENTINELS = {-999.25, -999.0, -9999.0}


def parse_las_text(content: str) -> LasData:
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

    curve_names: list[str] = []
    data_start = None
    in_curve_section = False

    for idx, line in enumerate(lines):
        upper_line = line.upper()
        if upper_line.startswith("~CURVE"):
            in_curve_section = True
            continue
        if upper_line.startswith("~A"):
            data_start = idx + 1
            break
        if in_curve_section and line.startswith("~"):
            in_curve_section = False

        if in_curve_section and "." in line:
            candidate = line.split(".", 1)[0].strip()
            if candidate:
                curve_names.append(candidate)

    if not curve_names:
        raise ValueError("Could not detect curve names in LAS file.")
    if data_start is None:
        raise ValueError("Could not detect ASCII data section (~A) in LAS file.")

    depth_values: list[float] = []
    rows: list[dict[str, float | None]] = []

    for line in lines[data_start:]:
        parts = line.split()
        if len(parts) < len(curve_names):
            continue

        numeric: list[float] = []
        valid = True
        for raw in parts[: len(curve_names)]:
            try:
                numeric.append(float(raw))
            except ValueError:
                valid = False
                break
        if not valid:
            continue

        row: dict[str, float | None] = {}
        for curve, value in zip(curve_names, numeric):
            row[curve] = None if value in NULL_SENTINELS else value

        depth = row[curve_names[0]]
        if depth is None:
            continue

        depth_values.append(depth)
        rows.append(row)

    if not depth_values:
        raise ValueError("No valid LAS data rows found in ~A section.")

    return LasData(curves=curve_names, depth=depth_values, rows=rows)
