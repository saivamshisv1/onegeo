from statistics import mean


def _curve_stats(values: list[float | None]) -> dict[str, float | int | None]:
    filtered = [v for v in values if v is not None]
    if not filtered:
        return {"count": 0, "mean": None, "min": None, "max": None}
    return {
        "count": len(filtered),
        "mean": round(mean(filtered), 3),
        "min": round(min(filtered), 3),
        "max": round(max(filtered), 3),
    }


def interpret_data(depth: list[float], curves: dict[str, list[float | None]]) -> dict:
    stats = {name: _curve_stats(values) for name, values in curves.items()}

    insights = []
    gr_mean = stats.get("GR", {}).get("mean")
    rhob_mean = stats.get("RHOB", {}).get("mean")

    if gr_mean is not None:
        if gr_mean < 60:
            insights.append("Gamma ray trend suggests cleaner sands or carbonates in this interval.")
        elif gr_mean > 90:
            insights.append("Elevated gamma ray values indicate likely shale-rich lithology.")
        else:
            insights.append("Gamma ray values indicate mixed lithology with moderate shale content.")

    if rhob_mean is not None:
        if rhob_mean < 2.35:
            insights.append("Low bulk density may suggest porosity and potential hydrocarbon-bearing zones.")
        elif rhob_mean > 2.65:
            insights.append("High bulk density suggests tight rock matrix or mineral-rich interval.")

    if not insights:
        insights.append("Insufficient common petrophysical curves for lithology heuristics; use statistical summary.")

    return {
        "depth_interval": {
            "from": depth[0] if depth else None,
            "to": depth[-1] if depth else None,
            "samples": len(depth),
        },
        "curve_statistics": stats,
        "insights": insights,
        "recommended_next_steps": [
            "Correlate interpreted interval with adjacent wells.",
            "Overlay resistivity/neutron logs for fluid and porosity confidence.",
            "Validate interpretations with core or cuttings data when available.",
        ],
    }
