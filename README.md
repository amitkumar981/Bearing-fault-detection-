# Bearing Fault Detection

This repository is a starter project for building a bearing fault detection pipeline using vibration and condition-monitoring data. It is structured as a Python-based machine learning project and includes a basic project scaffold, dependency configuration, and a metadata registry for recordings.

## Project overview

The goal of the project is to detect and classify bearing faults from sensor data, typically by analyzing vibration signals and training a model to distinguish healthy and faulty operating conditions.

This repository currently provides the starting foundation for that workflow:

- Python project configuration with dependency management
- Jupyter-ready environment for exploratory analysis
- Scientific Python stack for signal processing and modeling
- Metadata registry for recording-level tracking
- Simple starter script entry point

## Repository structure

```text
.
├── README.md
├── main.py
├── pyproject.toml
├── requirements.txt
├── metadata/
│   └── recording_registry.csv
└── .venv/
```

## Requirements

- Python 3.11+
- pip or uv for dependency installation

## Setup

### Option 1: using pip

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# or
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### Option 2: using the project metadata

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Run the project

The current starter entry point is defined in `main.py` and simply prints a welcome message:

```bash
python main.py
```

## Dependencies

The project includes common scientific and ML libraries:

- NumPy
- pandas
- SciPy
- Matplotlib
- scikit-learn
- JupyterLab
- IPython kernel
- pytest

## Metadata

The `metadata/recording_registry.csv` file is intended to store recording-level metadata, such as:

- recording ID
- source file name
- dataset source
- URL or reference
- channel/key information
- sampling rate
- operating condition
- fault location
- fault diameter
- load and RPM values
- units and metadata source

This makes it easier to organize experiments and keep track of training data provenance.

## Suggested next steps

A typical bearing fault detection workflow would include:

1. Collecting and labeling vibration data
2. Preprocessing signals and extracting features
3. Training and validating ML models
4. Evaluating performance on fault classes
5. Packaging the trained model for inference

## License

This project does not currently declare a license. If you intend to share or distribute it publicly, add an appropriate license file and update this section.

## Notes

This repository is currently a clean starting scaffold. You can expand it with notebooks, preprocessing scripts, model training code, and evaluation pipelines as the project grows.
