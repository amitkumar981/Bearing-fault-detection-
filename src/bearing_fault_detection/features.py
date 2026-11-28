"""Calculate the notebook's time-domain and frequency-domain features."""

from pathlib import Path
import logging
import sys
import numpy as np
import pandas as pd
import yaml
from scipy.signal import welch
from scipy.stats import kurtosis

logger = logging.getLogger("bearing_fault_detection.features")


def extract_features(windows, fs, settings):
    """Return one feature row per window, preserving the input row order."""
    windows = np.asarray(windows, dtype=float)
    if windows.ndim != 2 or not windows.size or not np.isfinite(windows).all():
        raise ValueError("Windows must be a nonempty, finite two-dimensional array.")
    if not np.isfinite(fs) or fs <= 0 or windows.shape[1] < settings["welch"]["nperseg"]:
        raise ValueError("Check sampling rate and Welch segment length.")
    if settings["welch"]["scaling"] != "density" or not settings["welch"]["return_onesided"]:
        raise ValueError("Power features require a one-sided density PSD.")

    rms = np.sqrt(np.mean(windows**2, axis=1))
    if not (rms > 0).all():
        raise ValueError("Crest factor is undefined for zero-RMS windows.")
    result = pd.DataFrame({
        "RMS": rms,
        "Crest factor": np.max(np.abs(windows), axis=1) / rms,
        "Pearson kurtosis": kurtosis(windows, axis=1, fisher=False, bias=settings["kurtosis_bias"])
    })

    frequency, psd = welch(windows, fs=fs, axis=1, **settings["welch"])
    total_power = np.trapezoid(psd, x=frequency, axis=1)
    if not (total_power > 0).all():
        raise ValueError("Spectral features require positive total PSD power.")
    for low, high in settings["bands_hz"]:
        band = (frequency >= low) & (frequency <= high)
        if not (0 <= low < high <= fs / 2) or band.sum() < 2:
            raise ValueError(f"Invalid or unresolved frequency band: {low}-{high} Hz")
        power = np.trapezoid(psd[:, band], x=frequency[band], axis=1)
        name = f"{low:g}-{high:g} Hz"
        result[f"{name} power"] = power
        result[f"{name} share (%)"] = 100 * power / total_power

    result["Spectral centroid (Hz)"] = np.trapezoid(psd * frequency, x=frequency, axis=1) / total_power
    result["Dominant frequency (Hz)"] = frequency[np.argmax(psd[:, 1:], axis=1) + 1]
    if not np.isfinite(result.to_numpy()).all():
        raise ValueError("Calculated features contain non-finite values.")
    return result


def build_features(project, params):
    """Read saved development windows and save their metadata plus features."""
    project = Path(project)
    paths = params["paths"]
    registry = pd.read_csv(project / paths["window_registry"])
    if registry.empty or registry.duplicated(["recording_id", "window_no"]).any():
        raise ValueError("Window registry must be nonempty with unique recording/window IDs.")
    if not (registry["partition"].eq("development") & registry["eligible_for_analysis"].eq(True)).all():
        raise ValueError("Only eligible development windows may be processed.")
    if not registry["nominal_fs_hz"].eq(params["preprocessing"]["fs_hz"]).all():
        raise ValueError("Window sampling rates differ from the configured nominal rate.")

    tables = []
    for recording_id, info in registry.groupby("recording_id"):
        logger.info("Extracting features: %s", recording_id)
        info = info.sort_values("window_no").reset_index(drop=True)
        if info["window_file"].nunique() != 1:
            raise ValueError(f"Multiple window files for recording: {recording_id}")
        windows = np.load(project / info["window_file"].iloc[0], allow_pickle=False)
        if not np.array_equal(info["window_no"], np.arange(len(windows))):
            raise ValueError(f"Window IDs do not match saved array rows: {recording_id}")
        values = extract_features(windows, float(info["nominal_fs_hz"].iloc[0]), params["features"])
        if not info["window_samples"].eq(windows.shape[1]).all():
            raise ValueError(f"Window sample counts differ from metadata: {recording_id}")
        tables.append(pd.concat([info, values], axis=1))

    features = pd.concat(tables, ignore_index=True)
    output = project / paths["features"]
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output, index=False)
    count = len(features.columns) - len(registry.columns)
    logger.info("Saved %d features for %d windows from %d recordings | file=%s",
                count, len(features), features["recording_id"].nunique(), output)
    return features


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project))
    from logging_config import setup_logging

    setup_logging(project)
    try:
        with (project / "params.yaml").open(encoding="utf-8") as file:
            build_features(project, yaml.safe_load(file))
    except Exception:
        logger.exception("Feature extraction failed.")
        raise