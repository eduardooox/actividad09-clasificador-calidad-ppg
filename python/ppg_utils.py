from __future__ import annotations

import numpy as np
import pandas as pd

SAMPLE_RATE_HZ = 100
EXPECTED_SECONDS = 10
MIN_SAMPLES = 500


def extract_features(red_values: np.ndarray | pd.Series) -> dict[str, float]:
    """Extrae cuatro características simples de una ventana PPG roja."""
    x = np.asarray(red_values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < MIN_SAMPLES:
        raise ValueError(
            f"Registro demasiado corto: {x.size} muestras; se necesitan al menos {MIN_SAMPLES}."
        )

    dc_mean = float(np.mean(x))
    centered = x - np.median(x)
    ac_amplitude = float(np.percentile(centered, 95) - np.percentile(centered, 5))
    ac_std = float(np.std(centered, ddof=1))
    diff_std = float(np.std(np.diff(x), ddof=1)) if x.size > 2 else 0.0

    return {
        "dc_mean": dc_mean,
        "ac_amplitude": ac_amplitude,
        "ac_std": ac_std,
        "diff_std": diff_std,
    }


def read_raw_csv(path: str) -> pd.DataFrame:
    """Lee una captura CSV y valida la columna red_raw."""
    df = pd.read_csv(path)
    if "red_raw" not in df.columns:
        raise ValueError(f"El archivo {path} no contiene la columna red_raw.")
    df["red_raw"] = pd.to_numeric(df["red_raw"], errors="coerce")
    df = df.dropna(subset=["red_raw"])
    return df
