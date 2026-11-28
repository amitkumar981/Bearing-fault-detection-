"""Create original-grid development windows and save their metadata."""

from pathlib import Path
import logging
import sys
import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger("bearing_fault_detection.preprocessing")


def make_windows(x, fs, window_seconds=1.0, remove_mean=True):
    """Return complete non-overlapping windows; leave the input unchanged."""
    x = np.asarray(x, dtype=float)
    samples = fs * window_seconds
    if not np.isfinite([fs, window_seconds]).all() or fs <= 0 or window_seconds <= 0:
        raise ValueError("Sampling rate and window duration must be positive and finite.")
    if not np.isfinite(samples) or samples < 1 or samples != int(samples):
        raise ValueError("Window duration must give a whole number of samples.")
    if x.ndim != 1 or not np.isfinite(x).all() or x.size < samples:
        raise ValueError("Signal must be finite, one-dimensional and at least one window long.")

    size = int(samples)
    windows = x[:x.size // size * size].reshape(-1, size).copy()
    if remove_mean:
        windows -= windows.mean(axis=1, keepdims=True)
    return windows


def preprocess(project, params):
    """Read the development manifest and save one window array per recording."""
    from bearing_fault_detection.data import load_signal

    project = Path(project)
    paths, settings = params["paths"], params["preprocessing"]
    records = pd.read_csv(project / paths["development_registry"])
    if records.empty or records["recording_id"].duplicated().any():
        raise ValueError("Development manifest must be nonempty with unique recording IDs.")
    if not (records["partition"].eq("development") & records["eligible_for_analysis"].eq(True)).all():
        raise ValueError("Only eligible development recordings may be processed.")
    fs = settings["fs_hz"]
    if not records["nominal_fs_hz"].eq(fs).all():
        raise ValueError("Configured sampling rate differs from recording metadata; no resampling is applied.")

    folder = project / paths["windows"]
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, record in records.iterrows():
        x = load_signal(project / paths["raw_data"] / record["relative_path"], params["data"]["channel"])
        windows = make_windows(x, fs, settings["window_seconds"], settings["remove_mean"])
        output = folder / f"{record['recording_id']}.npy"
        np.save(output, windows, allow_pickle=False)
        size = windows.shape[1]
        for number in range(len(windows)):
            start, end = number * size, (number + 1) * size
            rows.append({**record.to_dict(), "window_no": number,
                         "start_sample": start, "end_sample": end,
                         "start_time_s": start / fs, "end_time_s": end / fs,
                         "window_samples": size, "window_file": output.relative_to(project).as_posix()})
        logger.info("Prepared %s | windows=%d | dropped samples=%d", record["recording_id"], len(windows), x.size % size)

    registry = pd.DataFrame(rows)
    output = project / paths["window_registry"]
    output.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(output, index=False)
    logger.info("Saved %d windows from %d recordings | registry=%s", len(registry), len(records), output)
    return registry


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[2]
    sys.path[:0] = [str(project), str(project / "src")]
    from logging_config import setup_logging

    setup_logging(project)
    try:
        with (project / "params.yaml").open(encoding="utf-8") as file:
            preprocess(project, yaml.safe_load(file))
    except Exception:
        logger.exception("Preprocessing failed.")
        raise