from __future__ import annotations

import csv
import re
import time
from datetime import datetime
from pathlib import Path

import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "datos" / "originales"
BAUD = 115200
DURATION_S = 10
SAMPLE_RATE_HZ = 100


def choose_port() -> str:
    ports = list(list_ports.comports())
    print("\nPuertos seriales disponibles:")
    for p in ports:
        print(f"  {p.device}: {p.description}")
    port = input("Escriba el puerto del ESP32-S3 (ej. COM5): ").strip()
    if not port:
        raise ValueError("No se indicó un puerto serial.")
    return port


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    port = choose_port()

    participant = input("Código anónimo del participante (ej. P01): ").strip().upper()
    if not re.fullmatch(r"P\d{2,3}", participant):
        raise ValueError("Use un código anónimo como P01, P02, etc.; no escriba nombres.")

    print("\nCondición experimental:")
    print("  1 = estable (dedo quieto y correctamente apoyado)")
    print("  0 = perturbada (movimiento controlado durante la captura)")
    choice = input("Seleccione 1 o 0: ").strip()
    if choice not in {"0", "1"}:
        raise ValueError("La etiqueta debe ser 1 o 0.")

    label = int(choice)
    condition = "estable" if label == 1 else "movimiento"
    duration = input(f"Duración en segundos [predeterminado {DURATION_S}]: ").strip()
    duration_s = float(duration) if duration else DURATION_S
    if duration_s < 5 or duration_s > 30:
        raise ValueError("Use una duración entre 5 y 30 segundos.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"{participant}_{condition}_{stamp}"
    output = OUT_DIR / f"{session_id}.csv"

    print("\nCierre el Monitor Serial de Arduino antes de continuar.")
    print("Se abrirá la conexión y el ESP32-S3 podría reiniciarse.")

    rows: list[tuple[int, float, int]] = []
    with serial.Serial(port, BAUD, timeout=0.25) as ser:
        time.sleep(2.0)
        ser.reset_input_buffer()
        input("Prepare el dedo y presione ENTER para iniciar la captura...")
        ser.reset_input_buffer()
        start = time.monotonic()
        first_idx: int | None = None
        while time.monotonic() - start < duration_s:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
            if not raw or raw.startswith("#") or raw.startswith("sample_idx"):
                continue
            parts = raw.split(",")
            if len(parts) != 2:
                continue
            try:
                sample_idx = int(parts[0])
                red_value = int(parts[1])
            except ValueError:
                continue
            if first_idx is None:
                first_idx = sample_idx
            relative_idx = sample_idx - first_idx
            t_s = relative_idx / SAMPLE_RATE_HZ
            rows.append((relative_idx, t_s, red_value))

    if not rows:
        raise RuntimeError(
            "No se recibieron muestras. Revise el firmware, el puerto COM y que el Monitor Serial esté cerrado."
        )

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "participant_id", "session_id", "condition", "label",
            "sample_idx", "t_s", "red_raw"
        ])
        for idx, t_s, red in rows:
            writer.writerow([participant, session_id, condition, label, idx, f"{t_s:.3f}", red])

    expected = int(duration_s * SAMPLE_RATE_HZ)
    print(f"\nCaptura guardada: {output}")
    print(f"Muestras recibidas: {len(rows)} (esperadas aproximadamente: {expected})")
    print(f"Etiqueta: {label} ({'APTA/estable' if label == 1 else 'NO APTA/perturbada'})")
    if len(rows) < expected * 0.7:
        print("ADVERTENCIA: llegaron pocas muestras. Revise la tasa de adquisición y la conexión USB.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
