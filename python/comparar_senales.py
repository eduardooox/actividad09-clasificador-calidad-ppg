from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from ppg_utils import read_raw_csv

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "datos" / "originales"
OUT_DIR = ROOT / "modelos"


def select_file(prompt: str) -> Path:
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No hay archivos CSV en {RAW_DIR}")
    print("\nCapturas disponibles:")
    for i, p in enumerate(files, start=1):
        print(f"{i}. {p.name}")
    while True:
        value = input(prompt).strip()
        try:
            idx = int(value) - 1
            if 0 <= idx < len(files):
                return files[idx]
        except ValueError:
            pass
        print("Seleccione uno de los números de la lista.")


def main() -> None:
    stable_path = select_file("Número de captura ESTABLE: ")
    motion_path = select_file("Número de captura PERTURBADA: ")

    stable = read_raw_csv(str(stable_path))
    motion = read_raw_csv(str(motion_path))

    for df in (stable, motion):
        if "t_s" not in df.columns:
            df["t_s"] = range(len(df))
            df["t_s"] = df["t_s"] / 100.0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=False)
    axes[0].plot(stable["t_s"], stable["red_raw"], linewidth=0.8)
    axes[0].set_title(f"Captura estable: {stable_path.name}")
    axes[0].set_ylabel("Lectura roja (cuentas ADC)")
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(motion["t_s"], motion["red_raw"], linewidth=0.8)
    axes[1].set_title(f"Captura perturbada: {motion_path.name}")
    axes[1].set_xlabel("Tiempo (s)")
    axes[1].set_ylabel("Lectura roja (cuentas ADC)")
    axes[1].grid(True, alpha=0.25)

    fig.suptitle("Comparación de señales PPG del MAX30102")
    fig.tight_layout()
    out = OUT_DIR / "comparacion_senales_ppg.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Gráfico guardado en: {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
