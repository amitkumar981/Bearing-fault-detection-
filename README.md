# Bearing Fault Detection

## Project objective

Build an offline machine-learning pipeline that classifies bearing vibration recordings as healthy or faulty.

## Intended use

An educational condition-monitoring prototype that demonstrates signal processing, mechanically interpretable features and evaluation on separate recordings and bearings.

## Inputs

- Bearing vibration samples.
- Verified sampling rate and measurement units, with unresolved metadata explicitly flagged.
- Sensor channel, recording identity and bearing identity.
- Operating speed and load, when available.

The initial model uses vibration only.

## Outputs

- Healthy or faulty prediction for each analysis window.
- Feature values supporting investigation.
- Evaluation results grouped by recording and operating condition.

## Initial approach

1. Inspect raw recordings and verify metadata.
2. Define development and final-test partitions.
3. Apply justified preprocessing and consistent windowing.
4. Extract time-domain, frequency-domain and envelope features.
5. Compare an RMS-only baseline with a multi-feature model.
6. Evaluate missed faults, false alarms and generalization.
7. Document errors, assumptions and limitations.

## Evaluation rules

- Keep related recordings and repeated measurements from the same physical bearing in the same partition.
- Windows from one recording must not cross train/test boundaries.
- Fit scaling and feature selection using training data only, separately within each validation fold.
- Keep final-test data out of exploratory analysis, preprocessing decisions and model tuning.
- Report bearing counts and recording counts as well as window counts.
- Report accuracy, balanced accuracy, fault recall, false alarms and missed faults.
- Do not treat multiple windows from one recording as independent experiments.

## Out of scope

- Remaining useful life prediction.
- Fault severity estimation.
- Hardware deployment.
- Claims of industrial reliability without independent validation.

# Paderborn Data Inspection

## Purpose

Inspect one K001 development recording to understand its MATLAB structure, identify the vibration channel and verify available metadata.

No filtering, resampling or feature extraction is performed at this stage.

## Recording details

- File: `N15_M07_F10_K001_1.mat`.
- Bearing identity: `K001`.
- Condition: healthy, according to dataset documentation.
- Selected channel: `vibration_1`.
- Other available channels: force, two phase currents, speed, bearing-module temperature and torque.
- Physical measurement units: unverified because the stored unit field is empty.
- Plot amplitude label: recorded units.

## MATLAB structure

- `Info`: recording identification and file information.
- `Y`: measurement channels and their metadata.
- `X`: axes referenced by the measurement channels.
- `Description`: additional experiment information.

For the vibration channel:

- `Data` contains the vibration samples.
- `XIndex = 2` references the second entry in `X`, accessed at Python position `1`.
- `Raster = HostService` identifies its acquisition sampling group.
- `t_stored` preserves the original time values.
- `x` contains the extracted vibration values.

## Timing inspection

- Sample count: 256,001.
- Nominal sampling rate: 64,000 Hz.
- Nominal sampling interval: 15.625 microseconds.
- Stored time-axis span: approximately 4 seconds.
- Sampling rate calculated from the complete axis span: 64,000.0205 Hz.
- Maximum deviation from the nominal grid: 1.374 microseconds.
- Individual stored increments vary; their cause is not established.

Analysis will use the nominal 64 kHz grid while preserving the original time axis.

Creating nominal time coordinates does not change or resample the vibration samples.

The rate check uses:

    fs_check = (N - 1) / time_span

N samples contain N - 1 intervals between the first and last sample.

## Data-quality checks

All checks passed:

- Vibration and time arrays have matching lengths.
- All vibration values are finite.
- All stored time values are finite.
- Stored time increases throughout the recording.

These checks do not rule out every acquisition problem or establish that clipping is absent.

## Initial visual observations

- Overall amplitude spread appears broadly consistent throughout the four-second recording.
- The signal fluctuates around zero without a large visually apparent constant offset.
- A 50-millisecond detail reveals recurring bursts of oscillation separated by quieter intervals.
- No obvious clipping or long flat dropout is visible in the inspected plots.
- The source of the recurring bursts remains unidentified.
- The healthy label comes from dataset documentation, not visual appearance.
