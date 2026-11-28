from pathlib import Path
import logging
import sys
import numpy as np
import pandas as pd
import yaml
from scipy.io import loadmat

logger = logging.getLogger("bearing_fault_detection.data")


def load_signal(path, channel="vibration_1"):
    path = Path(path)
    logger.info("Loading recording: %s", path.name)

    try:
        recording = loadmat(path)[path.stem][0, 0]
        channels = recording["Y"].ravel()
        names = [channel["Name"].item() for channel in channels]
        logger.info("Available channels: %s", names)

        if names.count(channel) != 1:
            raise ValueError(f"Expected one {channel} channel: {path.name}")

        x = channels[names.index(channel)]["Data"].ravel().astype(float)

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
    with (project / "params.yaml").open(encoding="utf-8") as file:
        params = yaml.safe_load(file)
    paths, data = params["paths"], params["data"]
    if data["partition"] != "development":
        raise ValueError("This pipeline is for development bearings only.")
    registry = pd.read_csv(project / paths["recording_registry"])
    development = registry[
        registry["partition"].eq(data["partition"])
        & registry["eligible_for_analysis"].eq(True)
    ]
    logger.info("Eligible development recordings: %d", len(development))

    if development.empty:
        logger.error("No eligible development recordings found.")
        raise ValueError("No eligible development recordings found.")

    record = development.iloc[0]
    path = project / paths["raw_data"] / record["relative_path"]
    x = load_signal(path, data["channel"])

    output = project / paths["development_registry"]
    output.parent.mkdir(parents=True, exist_ok=True)
    development.to_csv(output, index=False)
    logger.info("Saved development registry: %s", output)