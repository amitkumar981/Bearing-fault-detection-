# Bearing Fault Detection

## Project objective

Build an offline machine-learning pipeline that classifies bearing vibration recordings as healthy or faulty. The current implementation produces predictions for individual analysis windows.

## Intended use

An educational condition-monitoring prototype demonstrating signal processing, mechanically interpretable features and evaluation on separate recordings and physical bearings.

This is a development project. Industrial reliability has not been demonstrated.

## Inputs

- Bearing vibration samples.
- Sampling-rate metadata and measurement-unit status, with unresolved items explicitly flagged.
- Sensor channel, recording identity and bearing identity.
- Operating speed, torque and radial-force settings, when available.

The current models use vibration-derived features only. Operating settings support analysis and error reporting; they are not model inputs.

Physical vibration units and calibration remain unverified. Amplitudes are therefore reported in recorded units.

## Outputs

- Healthy or faulty prediction for each analysis window.
- Feature values supporting investigation.
- Development evaluation results grouped by held-out bearings and operating condition.
- False alarms, missed faults, fault recall and balanced accuracy.

## Approach and current progress

1. **Completed:** inspect raw recordings and identify channels, axes and metadata.
2. **Completed:** construct the recording registry and separate development and final-test bearings.
3. **Completed for eligible development recordings:** create consistent windows and remove each window's mean.
4. **Completed:** extract 13 time-domain and frequency-domain features.
5. **Completed:** compare feature families using logistic regression.
6. **Completed:** compare logistic regression, Random Forest and XGBoost using two waveform-shape features.
7. **Completed initial analysis:** investigate failed predictions, feature contributions and operating-condition-dependent errors.
8. **Ongoing:** document assumptions, limitations and reproducible project steps.
9. **Planned:** develop mechanically motivated envelope features.
10. **Pending:** freeze the selected pipeline and evaluate the reserved final-test bearings.

## Dataset and partitions

The project uses a selected seven-bearing subset of the Paderborn bearing dataset, with 80 registered recordings per bearing: 560 recordings in total.

| Partition | Healthy bearings | Faulty bearings | Registered recordings |
|---|---|---|---:|
| Development | K001, K002 | KA04, KI04 | 320 |
| Final test | K003 | KA15, KI14 | 240 |

After provisional development eligibility checks, 272 recordings were retained and produced 1,085 complete analysis windows.

Repeated recordings and windows do not increase the number of independent physical bearings.

### Nominal operating settings

| Code combination | Speed | Torque | Radial force |
|---|---:|---:|---:|
| N09_M07_F10 | 900 rpm | 0.7 Nm | 1,000 N |
| N15_M01_F10 | 1,500 rpm | 0.1 Nm | 1,000 N |
| N15_M07_F04 | 1,500 rpm | 0.7 Nm | 400 N |
| N15_M07_F10 | 1,500 rpm | 0.7 Nm | 1,000 N |

These are operating settings, not a claim that every instantaneous measurement equals its setting.

## Preprocessing and windowing

- Selected channel: `vibration_1`.
- Nominal analysis sampling rate: 64,000 Hz.
- Window duration: one second, containing 64,000 samples.
- Windows do not overlap.
- Incomplete trailing segments are excluded.
- Each window's mean is removed before feature extraction.
- No filtering or resampling is currently applied.
- Raw MATLAB files remain unchanged.

Some stored time axes have unresolved discrepancies relative to the nominal sampling grid. Flagged development recordings are provisionally excluded; their timing has not been repaired.

Eligibility does not establish that acquisition was error-free.

Prepared windows are saved separately for each recording. A window registry preserves recording ID, bearing ID, condition, operating settings, nominal time boundaries and the saved array path.

## Features

| Feature family | Features | Count |
|---|---|---:|
| Time domain | RMS, crest factor, Pearson kurtosis | 3 |
| Frequency bands | Absolute power and relative power share in four bands | 8 |
| Spectral summaries | Spectral centroid and dominant frequency | 2 |
| **Total** | | **13** |

Frequency bands:

- 0–2 kHz.
- 2–5 kHz.
- 5–12 kHz.
- 12–32 kHz.

These are broad exploratory regions, not confirmed bearing-defect frequency boundaries.

Frequency features use Welch PSD estimates with 8,192-sample Hann segments and 50% overlap. At 64 kHz, frequency-bin spacing is 7.8125 Hz.

The dominant-frequency feature excludes the zero-frequency bin.

### Feature units

- RMS: recorded amplitude units.
- Absolute band power: recorded units squared.
- Crest factor and Pearson kurtosis: dimensionless.
- Relative band power: percentage.
- Spectral centroid and dominant frequency: Hz.

Pearson kurtosis uses the convention in which a Gaussian distribution has kurtosis 3.

## Development evaluation

Each validation fold holds out one healthy and one faulty bearing. All recordings and windows belonging to those bearings are excluded from that fold's training data.

| Fold | Training bearings | Validation bearings |
|---|---|---|
| 1 | K002, KI04 | K001, KA04 |
| 2 | K002, KA04 | K001, KI04 |
| 3 | K001, KI04 | K002, KA04 |
| 4 | K001, KA04 | K002, KI04 |

A fresh estimator is fitted in every fold.

Balanced accuracy is the average of healthy recall and fault recall. False alarms are healthy windows predicted faulty; missed faults are faulty windows predicted healthy.

### Feature-family comparison: logistic regression

Logistic regression uses StandardScaler and balanced class weights. Scaling is fitted using training windows only.

| Feature set | Features | Mean balanced accuracy | Worst-fold balanced accuracy |
|---|---:|---:|---:|
| RMS only | 1 | 34.56% | 13.24% |
| Crest factor + Pearson kurtosis | 2 | **82.14%** | **64.04%** |
| Relative band power | 4 | 62.98% | 50.00% |
| All features | 13 | 47.01% | 0.00% |

Among the logistic-regression feature sets, crest factor and Pearson kurtosis transferred most consistently across the development bearings.

Adding all 13 features did not consistently improve performance.

### Model comparison: waveform-shape features

Logistic regression, Random Forest and XGBoost were compared using the same two inputs:

- Crest factor.
- Pearson kurtosis.

All three models use the same four bearing-separated folds.

| Model | Mean balanced accuracy | Worst-fold balanced accuracy |
|---|---:|---:|
| Logistic regression | 82.14% | 64.04% |
| Random Forest | **86.82%** | **71.97%** |
| XGBoost | 75.32% | 50.25% |

Random Forest improved mean balanced accuracy by 4.68 percentage points over logistic regression.

These results apply to the tested configurations and development bearings. They do not establish a general ranking of the algorithms.

### Model configurations

**Logistic regression**

- StandardScaler fitted within each training fold.
- Balanced class weights.
- Maximum iterations: 1,000.

**Random Forest**

- Number of trees: 200.
- Maximum depth: 3.
- Minimum leaf size: 20 training windows.
- Balanced class weights.
- Random state: 42.

**XGBoost**

- Number of boosting rounds: 100.
- Maximum depth: 2.
- Learning rate: 0.05.
- L2 regularization: `reg_lambda=5`.
- Objective: `binary:logistic`.
- Evaluation metric: `logloss`.
- Tree method: `hist`.
- Random state: 42.
- Positive-class weighting: healthy training-window count divided by faulty training-window count, calculated separately within each fold.

These were fixed starting configurations, not the outcome of an extensive hyperparameter search.

### Interpretation of reported scores

Means are unweighted averages across the four folds, calculated from the reported confusion counts. Averaging already-rounded fold percentages can differ by 0.01 percentage point.

These are exploratory development results used for model comparison, not final-test results.

Validation bearings recur across folds. Repeated predictions must not be counted as independent tests or independent bearings.

## Error analysis

### Weakest waveform-shape validation fold

All three models have their lowest balanced accuracy when validating on K002 and KA04.

This fold contains 298 healthy windows and 287 faulty windows.

| Model | False alarms | Missed faults |
|---|---:|---:|
| Logistic regression | 97 | 113 |
| Random Forest | 165 | 2 |
| XGBoost | 148 | 143 |

Random Forest detected substantially more faults, but produced more false alarms than logistic regression.

### Errors by operating setting

The following rates apply to the K002/KA04 validation fold.

| Setting | Logistic false alarm (%) | Logistic fault recall (%) | Forest false alarm (%) | Forest fault recall (%) | XGBoost false alarm (%) | XGBoost fault recall (%) |
|---|---:|---:|---:|---:|---:|---:|
| N09_M07_F10 | 0.00 | 53.95 | 100.00 | 97.37 | 91.55 | 0.00 |
| N15_M01_F10 | 61.11 | 44.78 | 47.22 | 100.00 | 29.17 | 0.00 |
| N15_M07_F04 | 26.58 | 51.39 | 50.63 | 100.00 | 62.03 | 100.00 |
| N15_M07_F10 | 42.11 | 91.67 | 26.32 | 100.00 | 17.11 | 100.00 |

Important observations:

- Random Forest misclassified all 71 healthy K002 windows at 900 rpm.
- XGBoost missed all 76 KA04 fault windows at 900 rpm.
- XGBoost also missed all 67 KA04 fault windows at 1,500 rpm with 0.1 Nm torque.
- All 143 XGBoost missed faults came from those two settings.
- No tested model demonstrated consistently low false alarms and missed faults across all settings in this fold.

### Decision-boundary investigation

At N15_M01_F10, the healthy and faulty waveform-feature clusters were visually separated, but the logistic-regression boundary cut through the held-out clusters.

The model had learned one boundary from training recordings across all four operating settings. Separation visible at one setting did not guarantee correct predictions from that global model.

Nonlinear models changed the error pattern but did not resolve transfer across bearings and operating conditions.

### All-feature logistic-regression failure

The all-feature model misclassified every validation window in the K001/KA04 fold.

Score-contribution analysis showed that:

- High-frequency absolute power pushed healthy K001 toward faulty.
- Low-frequency power and share pushed faulty KA04 toward healthy.

These contributions explain the model's calculation, not the mechanical causes of the vibration.

### Feature-value spot checks

Recalculating features from one saved recording per development bearing matched the stored values in all four spot checks.

This is not verification of every recording.

## Evaluation rules

- Group related recordings from the same physical bearing together when evaluating unseen bearings.
- Never split windows from one recording across training and validation within a fold.
- Fit scaling and other learned transformations using training data only within each fold.
- Use development validation for model comparison.
- Keep final-test data out of exploratory signal analysis, feature choices and model tuning.
- Report bearing and recording counts as well as window counts.
- Retain false alarms and missed faults alongside aggregate metrics.
- Freeze preprocessing, features, model settings and decision rules before final-test evaluation.

## Initial Paderborn data inspection

The initial inspection used the healthy K001 recording `N15_M07_F10_K001_1.mat`.

Its MATLAB structure contains:

- `Info`: recording information.
- `X`: measurement axes.
- `Y`: measurement channels.
- `Description`: descriptive metadata.

Available channels include force, two motor phase currents, speed, bearing-module temperature, torque and vibration.

The selected vibration channel has raster `HostService` and `XIndex = 2`, referencing the second axis entry at Python position `1`. Its stored unit field is empty.

| Timing item | Initial-recording observation |
|---|---|
| Vibration samples | 256,001 |
| Nominal sampling interval | 15.625 microseconds |
| Stored time-axis span | Approximately 4 seconds |
| Rate from complete axis span | 64,000.0205 Hz |
| Maximum deviation from nominal grid | 1.374 microseconds |

For this recording:

- Signal and time-array lengths matched.
- Signal and time values were finite.
- Stored time increased throughout.
- Individual stored increments varied; their cause was not established.

The reciprocal of the median stored increment was not substituted for the nominal sampling rate.

The complete-axis rate is calculated as:

`(N - 1) / (last_time - first_time)`

Original timestamps remain in the raw files. Constructing nominal coordinates with `np.arange(N) / fs` does not resample vibration samples.

Initial waveform plots showed recurring oscillation bursts, with no obvious clipping or long flat dropout in the inspected views.

The healthy label came from dataset metadata, not waveform appearance. These observations did not establish the cause of the bursts or rule out sensor errors.

No preprocessing or feature extraction was performed in the initial inspection stage.

## Current project files

- `metadata/recording_registry.csv`: recording identities, partitions and eligibility metadata.
- `metadata/window_registry.csv`: development-window identities and saved-array locations.
- `data/interim/windows/`: one NumPy window array per processed recording.
- `data/processed/development_features.csv`: calculated features with window metadata.
- `reports/tables/development_model_comparison.csv`: logistic-regression feature-family results.
- `reports/tables/waveform_model_comparison.csv`: logistic regression, Random Forest and XGBoost comparison.
- `reports/tables/waveform_shape_errors_by_setting.csv`: logistic-regression error analysis for the K002/KA04 fold.
- `reports/tables/random_forest_errors_by_setting.csv`: Random Forest error analysis for the same fold.
- `reports/tables/xgboost_errors_by_setting.csv`: XGBoost error analysis for the same fold.

Raw recordings and generated arrays should remain outside source control. Keep the code, documentation and appropriate metadata needed to reproduce the analysis.

## Limitations and next steps

- Development contains only four physical bearings.
- Every fold trains on just one healthy and one faulty bearing.
- Holding out KA04 or KI04 also tests transfer to a different fault type.
- Feature distributions vary with bearing identity and operating settings.
- More features and more flexible models did not consistently improve every fold or error type.
- Physical units, calibration and some timestamp discrepancies remain unresolved.
- Random Forest is the provisional development candidate, but substantial false alarms and missed faults remain.
- Final-test bearings have not been used for exploratory feature analysis or model fitting.
- Final-test classification results are not yet available.