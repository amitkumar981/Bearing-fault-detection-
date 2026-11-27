from pathlib import Path
import logging
import sys
import numpy as np
import pandas as pd
from scipy.io import loadmat

logger = logging.getLogger("bearing_fault_detection.data")


def load_signal(path):
    path = Path(path)
    logger.info("Loading recording: %s", path.name)

    try:
        recording = loadmat(path)[path.stem][0, 0]
        channels = recording["Y"].ravel()
        names = [channel["Name"].item() for channel in channels]
        logger.info("Available channels: %s", names)

        if names.count("vibration_1") != 1:
            raise ValueError(f"Expected one vibration channel: {path.name}")

        x = channels[names.index("vibration_1")]["Data"].ravel().astype(float)

        if x.size < 2 or not np.isfinite(x).all():
            raise ValueError(f"Invalid vibration samples: {path.name}")

        logger.info("Loaded %s | samples=%d", path.name, x.size)
        return x

    except Exception:
        logger.exception("Failed to load recording: %s", path.name)
        raise


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project))
    from logging_config import setup_logging

    setup_logging(project)
    registry = pd.read_csv(project / "metadata/recording_registry.csv")
    development = registry[
        registry["partition"].eq("development")
        & registry["eligible_for_analysis"].eq(True)
    ]
    logger.info("Eligible development recordings: %d", len(development))

    if development.empty:
        logger.error("No eligible development recordings found.")
        raise ValueError("No eligible development recordings found.")

    record = development.iloc[0]
    path = project / "data/raw/paderborn" / record["relative_path"]
    x = load_signal(path)

    output = project / "data/interim/development_recordings.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    development.to_csv(output, index=False)
    logger.info("Saved development registry: %s", output)
