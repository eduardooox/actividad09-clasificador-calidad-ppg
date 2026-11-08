from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.tree import DecisionTreeClassifier, plot_tree

from ppg_utils import extract_features, read_raw_csv

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "datos" / "originales"
PROCESSED_DIR = ROOT / "datos" / "procesados"
MODEL_DIR = ROOT / "modelos"
FEATURES = ["dc_mean", "ac_amplitude", "ac_std", "diff_std"]


def build_feature_table() -> pd.DataFrame:
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No hay capturas CSV en {RAW_DIR}")

    records: list[dict] = []
    for path in files:
        df = read_raw_csv(str(path))
        if len(df) < 500:
            print(f"Se omite {path.name}: solo tiene {len(df)} muestras.")
            continue

        feats = extract_features(df["red_raw"])
        first = df.iloc[0]
        records.append({
            "file": path.name,
            "participant_id": str(first.get("participant_id", "P00")),
            "condition": str(first.get("condition", "desconocida")),
            "label": int(first.get("label", -1)),
            **feats,
        })

    if not records:
        raise RuntimeError("No hay registros suficientemente largos para procesar.")

    table = pd.DataFrame(records)
    if not set(table["label"].unique()).issubset({0, 1}):
        raise ValueError("Las etiquetas deben ser 0 (perturbada) o 1 (estable).")
    if table["label"].nunique() != 2:
        raise ValueError("Se necesitan capturas de ambas clases: estable y perturbada.")
    return table


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    table = build_feature_table()
    feature_path = PROCESSED_DIR / "dataset_caracteristicas.csv"
    table.to_csv(feature_path, index=False)

    if table["participant_id"].nunique() < 3:
        raise ValueError(
            "Para evaluar sin mezclar capturas de una misma persona se requieren al menos 3 participantes."
        )

    X = table[FEATURES]
    y = table["label"].astype(int)
    groups = table["participant_id"]

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    if y_train.nunique() < 2 or y_test.nunique() < 2:
        raise ValueError(
            "La partición dejó una sola clase en entrenamiento o prueba. Asegúrense de que cada participante tenga registros estables y perturbados; luego vuelvan a ejecutar."
        )

    model = DecisionTreeClassifier(
        max_depth=3,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    report = classification_report(
        y_test,
        pred,
        labels=[0, 1],
        target_names=["No apta / perturbada", "Apta / estable"],
        zero_division=0,
    )
    accuracy = accuracy_score(y_test, pred)
    cm = confusion_matrix(y_test, pred, labels=[0, 1])

    model_path = MODEL_DIR / "modelo_calidad_ppg.joblib"
    joblib.dump({"model": model, "features": FEATURES}, model_path)

    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["No apta", "Apta"],
    )
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Matriz de confusión - Calidad PPG")
    fig.tight_layout()
    fig.savefig(MODEL_DIR / "matriz_confusion.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 7))
    plot_tree(
        model,
        feature_names=FEATURES,
        class_names=["No apta", "Apta"],
        filled=True,
        rounded=True,
        ax=ax,
    )
    ax.set_title("Árbol de decisión para clasificación de calidad PPG")
    fig.tight_layout()
    fig.savefig(MODEL_DIR / "arbol_decision.png", dpi=160)
    plt.close(fig)

    metrics_path = MODEL_DIR / "metricas_evaluacion.txt"
    with metrics_path.open("w", encoding="utf-8") as f:
        f.write(f"Registros usados: {len(table)}\n")
        f.write(f"Participantes: {table['participant_id'].nunique()}\n")
        f.write(f"Entrenamiento: {len(train_idx)} registros\n")
        f.write(f"Prueba: {len(test_idx)} registros\n")
        f.write(f"Accuracy: {accuracy:.4f}\n\n")
        f.write(report)
        f.write("\n\nImportancia de variables:\n")
        for name, importance in zip(FEATURES, model.feature_importances_):
            f.write(f"{name}: {importance:.4f}\n")

    print("\nDATASET DE CARACTERÍSTICAS")
    print(table.head())
    print(f"\nRegistros procesados: {len(table)}")
    print(f"Accuracy: {accuracy:.3f}")
    print("\nReporte de clasificación:")
    print(report)
    print(f"Modelo guardado: {model_path}")
    print(f"Matriz de confusión: {MODEL_DIR / 'matriz_confusion.png'}")
    print(f"Árbol de decisión: {MODEL_DIR / 'arbol_decision.png'}")
    print(f"Métricas: {metrics_path}")


if __name__ == "__main__":
    main()
