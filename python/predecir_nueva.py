from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from ppg_utils import extract_features, read_raw_csv

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "modelos" / "modelo_calidad_ppg.joblib"


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Primero ejecute entrenar_modelo.py para crear el modelo.")

    raw_path = input("Ruta del CSV de la nueva captura: ").strip().strip('"')
    df = read_raw_csv(raw_path)
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]

    vector = extract_features(df["red_raw"])
    X = pd.DataFrame([vector], columns=features)
    prediction = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]

    print("\nCARACTERÍSTICAS DE LA CAPTURA")
    for key, value in vector.items():
        print(f"{key}: {value:.4f}")

    print("\nRESULTADO DEL MODELO")
    if prediction == 1:
        print("APTA / estable: el modelo la clasifica como similar a las capturas estables.")
    else:
        print("NO APTA / perturbada: el modelo la clasifica como similar a las capturas perturbadas.")
    print(f"Probabilidad estimada de clase 0 (perturbada): {probabilities[0]:.3f}")
    print(f"Probabilidad estimada de clase 1 (estable): {probabilities[1]:.3f}")
    print("Nota: resultado experimental; no es una evaluación clínica ni una garantía universal de calidad PPG.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
