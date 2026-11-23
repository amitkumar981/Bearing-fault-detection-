# Bearing Fault Detection

## Project objective

Build an offline machine-learning pipeline that classifies bearing vibration recordings as healthy or faulty. The current implementation produces predictions for individual analysis windows.

## Intended use

An educational condition-monitoring prototype that demonstrates signal processing, mechanically interpretable features and evaluation on separate recordings and physical bearings.

This is a development project. Industrial reliability has not been demonstrated.

## Inputs

- Bearing vibration samples.
- Sampling-rate metadata and measurement-unit status, with unresolved items explicitly flagged.
- Sensor channel, recording identity and bearing identity.
- Operating speed, torque and radial-force settings, when available.

The current models use vibration-derived features only. Operating settings support analysis and error reporting; they are not current model inputs. Physical vibration units and calibration remain unverified, so amplitudes are reported in recorded units.

## Outputs

- Healthy or faulty prediction for each analysis window.
- Feature values supporting investigation.
- Development evaluation results grouped by held-out bearings and operating condition.
- Tables of false alarms, missed faults, fault recall and balanced accuracy.

## Approach and current progress

1. **Completed:** inspect raw recordings and identify channels, axes and metadata.
2. **Completed:** construct the recording registry and separate development and final-test bearings.
3. **Completed for eligible development recordings:** create consistent windows and remove each window's mean.
4. **Completed:** extract 13 time-domain and frequency-domain features. Envelope features remain planned.
5. **Completed:** compare an RMS-only baseline with waveform-shape, relative-band-power and all-feature models.
6. **In progress:** investigate generalization failures, operating-condition effects and model errors.
7. **Ongoing:** document assumptions, limitations and reproducible project steps.
8. **Pending:** freeze the pipeline and evaluate the reserved final-test bearings.

## Dataset and partitions

The project uses a selected seven-bearing subset of the Paderborn bearing dataset, with 80 recordings registered per bearing: 560 recordings in total.

| Partition | Healthy bearings | Faulty bearings | Registered recordings |
|---|---|---|---:|
| Development | K001, K002 | KA04, KI04 | 320 |
| Final test | K003 | KA15, KI14 | 240 |

After the provisional development eligibility checks, 272 recordings were retained and produced 1,085 complete analysis windows. Repeated recordings and windows do not increase the number of independent physical bearings.

The nominal operating settings are:

| Code combination | Speed | Torque | Radial force |
|---|---:|---:|---:|
| N09_M07_F10 | 900 rpm | 0.7 Nm | 1,000 N |
| N15_M01_F10 | 1,500 rpm | 0.1 Nm | 1,000 N |
| N15_M07_F04 | 1,500 rpm | 0.7 Nm | 400 N |
| N15_M07_F10 | 1,500 rpm | 0.7 Nm | 1,000 N |

These are operating settings, not a claim that every measured instantaneous value equals the setting.

## Preprocessing and windowing

- Selected channel: `vibration_1`.
- Nominal analysis sampling rate: 64,000 Hz.
- Window duration: one second, containing 64,000 samples.
- Windows do not overlap; incomplete trailing segments are excluded.
- Each window's mean is removed before feature extraction.
- No filtering or resampling is currently applied.
- Raw MATLAB files remain unchanged.

Some stored time axes have unresolved discrepancies relative to the nominal sampling grid. Flagged development recordings are provisionally excluded; their timing has not been repaired. Eligibility does not establish that acquisition was error-free.

Prepared windows are saved separately for each recording. A window registry preserves recording ID, bearing ID, condition, operating settings, nominal time boundaries and the saved array path.

## Features

| Feature family | Features | Count |
|---|---|---:|
| Time domain | RMS, crest factor, Pearson kurtosis | 3 |
| Frequency bands | Absolute power and relative power share in each of four bands | 8 |
| Spectral summaries | Spectral centroid and dominant frequency | 2 |
| **Total** | | **13** |

The frequency bands are 0–2, 2–5, 5–12 and 12–32 kHz. They are broad exploratory regions, not confirmed bearing-defect frequency boundaries.

Frequency features use Welch PSD estimates with 8,192-sample Hann segments and 50% overlap. At 64 kHz, frequency-bin spacing is 7.8125 Hz. The dominant-frequency feature excludes the zero-frequency bin.

RMS retains the original recorded amplitude units; absolute band power uses recorded units squared. Crest factor and Pearson kurtosis are dimensionless, band shares are percentages, and spectral centroid and dominant frequency are in Hz. Pearson kurtosis uses the convention in which a Gaussian distribution has kurtosis 3.

## Development evaluation

Each validation fold holds out one healthy and one faulty bearing. All recordings and windows belonging to those bearings are excluded from that fold's training data.

| Fold | Training bearings | Validation bearings |
|---|---|---|
| 1 | K002, KI04 | K001, KA04 |
| 2 | K002, KA04 | K001, KI04 |
| 3 | K001, KI04 | K002, KA04 |
| 4 | K001, KA04 | K002, KI04 |

Each model uses a pipeline containing StandardScaler and logistic regression with balanced class weights. A fresh pipeline is fitted in each fold. Scaling is learned from training windows only.

Balanced accuracy is the average of healthy recall and fault recall. False alarms are healthy windows predicted faulty; missed faults are faulty windows predicted healthy.

### Feature-family comparison

| Feature set | Features | Mean balanced accuracy | Worst-fold balanced accuracy |
|---|---:|---:|---:|
| RMS only | 1 | 34.56% | 13.24% |
| Crest factor + Pearson kurtosis | 2 | **82.14%** | **64.04%** |
| Relative band power | 4 | 62.98% | 50.00% |
| All features | 13 | 47.01% | 0.00% |

Means are unweighted averages across the four folds, calculated from the reported confusion counts. Averaging already-rounded fold percentages can differ by 0.01 percentage point.

These are exploratory development results used for model comparison. They are not final-test performance. Validation bearings recur across folds, so repeated predictions must not be counted as independent tests or independent bearings.

### Error analysis

The two-feature waveform-shape model performed most consistently, but its weakest fold, validating on K002 and KA04, produced 97 false alarms and 113 missed faults.

| Operating setting | False alarm rate | Fault recall |
|---|---:|---:|
| N09_M07_F10 | 0.00% | 53.95% |
| N15_M01_F10 | 61.11% | 44.78% |
| N15_M07_F04 | 26.58% | 51.39% |
| N15_M07_F10 | 42.11% | 91.67% |

No setting in that fold achieved both low false alarms and high fault recall.

The all-feature model misclassified every validation window in the K001/KA04 fold. Score-contribution analysis showed that high-frequency absolute power pushed healthy K001 toward faulty, while low-frequency power and share pushed faulty KA04 toward healthy. These explain the model's calculation, not the mechanical causes of the recorded vibration.

Recalculating features from one saved recording per development bearing matched the stored feature values in all four spot checks. This is not verification of every recording.

## Evaluation rules

- Group related recordings from the same physical bearing together when evaluating unseen bearings.
- Never split windows from one recording across training and validation within a fold.
- Fit scaling and other learned transformations using training data only within each fold.
- Use development validation for model comparison; keep final-test data out of exploratory signal analysis, feature choices and model tuning.
- Report bearing and recording counts as well as window counts.
- Retain false alarms and missed faults alongside aggregate metrics.
- Freeze preprocessing, features, model settings and decision rules before final-test evaluation.

## Initial Paderborn data inspection

The initial inspection used the healthy K001 recording `N15_M07_F10_K001_1.mat`. Its MATLAB structure contains `Info`, `X`, `Y` and `Description`. `Y` contains measurement channels; `X` contains their referenced axes.

Available channels include force, two motor phase currents, speed, bearing-module temperature, torque and vibration. The selected vibration channel has raster `HostService` and `XIndex = 2`, referencing the second axis entry at Python position `1`. Its stored unit field is empty.

| Timing item | Initial-recording observation |
|---|---|
| Vibration samples | 256,001 |
| Nominal sampling interval | 15.625 microseconds |
| Stored time-axis span | Approximately 4 seconds |
| Rate from complete axis span | 64,000.0205 Hz |
| Maximum deviation from nominal grid | 1.374 microseconds |

For this recording, signal and time-array lengths matched, values were finite, and stored time increased throughout. Stored increments varied; their cause was not established. The reciprocal of their median was not substituted for the nominal sampling rate.

The complete-axis rate is calculated as `(N - 1) / (last_time - first_time)`. Original stored timestamps remain in the raw files. Constructing nominal coordinates with `np.arange(N) / fs` does not resample the vibration samples.

Initial waveform plots showed recurring oscillation bursts, with no obvious clipping or long flat dropout in the inspected views. The healthy label came from dataset metadata, not waveform appearance. These observations did not establish the cause of the bursts or rule out sensor errors. No preprocessing or feature extraction was performed in the initial inspection stage.

## Current project files

- `metadata/recording_registry.csv`: recording identities, partitions and eligibility metadata.
- `metadata/window_registry.csv`: identities and locations of development windows.
- `data/interim/windows/`: one NumPy window array per processed recording.
- `data/processed/development_features.csv`: calculated features with window metadata.
- `reports/tables/development_model_comparison.csv`: fold-level development results.
- `reports/tables/waveform_shape_errors_by_setting.csv`: operating-setting error analysis for the K002/KA04 fold.

Raw recordings and generated arrays should remain outside source control. Keep the code, documentation and appropriate metadata needed to reproduce the analysis.

## Limitations and next steps

- Development currently contains only four physical bearings; every fold trains on just one healthy and one faulty bearing.
- Holding out KA04 or KI04 also tests transfer to a different fault type.
- Feature distributions vary with bearing identity and operating settings. More features did not consistently improve transfer.
- Physical units, calibration and some timestamp discrepancies remain unresolved.
- The current strongest candidate still has substantial false alarms and missed faults.
- Final-test bearings have not been used for exploratory feature analysis or model fitting; final-test classification results are not yet available.

Next, inspect waveform-feature overlap at N15_M01_F10, assess justified feature improvements or additional development-bearing diversity, and document any protocol changes. Envelope features remain planned. Freeze the selected pipeline before final-test evaluation, then report errors by bearing, recording and operating condition.

## Out of scope

- Remaining useful life prediction.
- Fault severity estimation.
- Hardware deployment.
- Claims of industrial reliability without independent validation.
