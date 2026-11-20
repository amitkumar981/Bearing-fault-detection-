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

## Dataset inventory

The recording registry contains 560 recordings from seven physical bearings.
Each bearing has 80 recordings: 20 repetitions under four operating conditions.

Only vibration will be used as model input.

## Fixed partition plan

| Bearing | Condition | Partition | Recordings |
|---|---|---|---:|
| K001 | Healthy | Development | 80 |
| K002 | Healthy | Development | 80 |
| KA04 | Faulty — outer-ring damage | Development | 80 |
| KI04 | Faulty — inner-ring damage | Development | 80 |
| K003 | Healthy | Final test | 80 |
| KA15 | Faulty — outer-ring damage | Final test | 80 |
| KI14 | Faulty — inner-ring damage | Final test | 80 |

Development: 320 recordings from four bearings.
Final test: 240 recordings from three bearings.

## Registry checks

- No missing values in the current registry fields.
- No duplicate recording IDs.
- Every bearing belongs to exactly one partition.
- Registry saved to metadata/recording_registry.csv.

## Evaluation boundaries

- Keep all windows and recordings from each bearing together.
- Use development bearings for exploration and model selection.
- Keep final-test signals out of preprocessing decisions and feature selection.
- Three final-test bearings provide limited evidence of generalization.

## Remaining metadata work

- Verify sampling rates and vibration-channel availability across recordings.
- Resolve physical measurement units and calibration where possible.
- Verify physical values represented by the operating-condition codes.
- Record sources and unresolved assumptions.

## Data-preparation findings

- Registered 560 recordings from seven physical bearings.
- Development: 320 recordings from K001, K002, KA04 and KI04.
- Final test: 240 recordings from K003, KA15 and KI14.
- Bearing identities do not cross partition boundaries.
- All referenced recording files were found.
- All recordings have matching vibration and time-array lengths.
- All vibration and time values are finite.
- All stored time axes increase strictly.
- Channel and axis raster names match in every recording.
- Operating-condition codes were mapped to documented physical settings.

## Timing limitations

The documented nominal vibration sampling rate is 64,000 Hz.

Using a provisional 0.1% full-span rate-difference threshold:
- 481 recordings are within the screening tolerance.
- 79 recordings require timing review.

Passing this screening does not establish uniform timestamp spacing.
The cause of the discrepancies remains unresolved.

No samples have been trimmed, resampled or automatically excluded.

## Measurement units

Physical vibration amplitude units remain unverified.
Use "recorded units" until calibration and units are established.

## Saved outputs

- metadata/recording_registry.csv
- metadata/timing_audit.csv
- metadata/quality_audit.csv

## Provisional timing-handling policy

The documented nominal sampling rate is 64,000 Hz.

Recordings whose axis-derived rate differs from nominal by more than
0.1% are held from the initial frequency-based analysis.

This is a provisional screening rule, not a verified acquisition
tolerance or proof of file corruption.

The same eligibility rule applies to every partition. Original bearing
partitions remain unchanged.

### Development selection

- Original development recordings: 320.
- Held for timing review: 48.
- Provisionally selected: 272.
- Healthy recordings selected: 133.
- Faulty recordings selected: 139.

All four development bearings remain represented.

### Limitations

- Passing the full-span check does not prove uniform timestamp spacing.
- The cause of the timing discrepancies remains unresolved.
- Physical vibration amplitude units remain unverified.
- No samples have been trimmed, repaired or resampled.
- All 560 recordings remain in the master registry.
- Future evaluation must report coverage and held recordings.

## Analysis summary and decisions

### Objective

Explore the development vibration recordings before choosing
preprocessing steps, filter bands and features.

The analysis examined:
- Raw vibration waveforms.
- FFT amplitude spectra.
- Welch power spectral density.
- Spectrograms.
- Variation across repetitions and operating settings.

### Data used

Only development bearings were included:

| Bearing | Condition | Eligible recordings |
|---|---|---:|
| K001 | Healthy | 58 |
| K002 | Healthy | 75 |
| KA04 | Faulty | 72 |
| KI04 | Faulty | 67 |
| **Total** | | **272** |

The existing timing-screening rule held 48 of the 320 development
recordings for further review.

The final-test bearings were excluded from exploratory analysis.

### Sampling and measurement assumptions

- Channel: vibration_1.
- Documented nominal sampling rate: 64,000 Hz.
- Frequency and nominal time axes use this rate provisionally.
- Original stored timestamps and raw files remain unchanged.
- Passing the timing screen does not establish perfectly uniform sampling.
- Physical amplitude units and calibration remain unverified.
- Amplitudes are therefore reported in recorded units.

## What each analysis contributed

| Method | Purpose |
|---|---|
| Full-record waveform | Inspect overall amplitude, offsets and large events. |
| Waveform zoom | Examine short bursts and oscillations hidden in the full view. |
| FFT amplitude spectrum | Locate individual frequency components and spectral clusters. |
| Welch PSD | Estimate how mean-square vibration is distributed across frequency. |
| Spectrogram | Examine when particular frequency regions become stronger or weaker. |
| Median PSD and percentile range | Check whether spectral patterns recur across recordings. |

### Raw waveform inspection

Four examples were selected at N15_M07_F10:
one eligible recording per development bearing, using the first
eligible repetition in numerical order.

Full recordings and matching 1.00–1.05 second intervals were plotted
with shared amplitude scales.

Healthy recordings also contained bursts and large peaks.
Waveform appearance or maximum amplitude alone was insufficient
to establish bearing condition.

Separate recordings were not synchronized to shaft angle.

### FFT method

For each recording:

1. Remove the recording mean.
2. Apply a periodic Hann window.
3. Calculate the real-valued FFT.
4. Construct the matching frequency axis.
5. Normalize FFT magnitudes by the window sum.
6. Double positive-frequency amplitudes, excluding DC and
   the Nyquist bin when present.

The Hann window reduces distant spectral leakage but broadens peaks.

The resulting spectrum provides peak-amplitude estimates,
not power spectral density. Estimates can be affected by
off-bin frequencies, overlapping components and broadband content.

For N15_M07_F10_K001_1:

- Samples: 256,001.
- FFT bin spacing: approximately 0.25 Hz.
- Strongest non-DC FFT bin: 7,747.72 Hz.
- Peak-amplitude estimate: 0.022688 recorded units.

This peak was observed in a healthy recording and was not
interpreted as a fault frequency.

### Welch PSD settings

| Parameter | Value | Reason |
|---|---|---|
| Segment length | 8,192 samples | Initial balance between spectral detail and averaging. |
| Segment duration | 128 ms | Derived from the nominal 64 kHz rate. |
| Overlap | 4,096 samples | Uses 50% overlap with the Hann window. |
| Window | Hann | Reduces distant spectral leakage. |
| Detrending | Constant | Removes each segment's mean. |
| Scaling | Density | Produces recorded units²/Hz. |

Frequency-bin spacing was 7.8125 Hz.
Actual frequency resolution also depends on the window.

PSD was displayed on a logarithmic vertical axis.
Band power must be calculated from the linear PSD values.

### Spectrogram settings

The spectrogram used the same segment length, overlap, window,
detrending and PSD scaling as Welch.

Welch averages segment PSDs; the spectrogram retains them
separately over time.

- Segment duration: 128 ms.
- Time between segment centres: 64 ms.
- Displayed frequency region for detailed comparison: 0–12 kHz.
- Shared colour limits: −80 to −35 dB.
- Reference: 1 recorded unit²/Hz.
- A small numerical floor avoided log10(0).

The frequency and colour limits changed only the display.
They did not filter or remove signal content.

Values outside the colour limits received endpoint colours.

Horizontal bands persisted across much of the example recordings,
with changes in brightness. This did not prove stationarity.

These settings could not precisely locate individual
millisecond-scale impacts.

## Repeatability and operating-condition comparisons

A separate Welch PSD was calculated for each eligible recording.

At each frequency, the median and 25th–75th percentile range
summarized variation within each bearing and operating setting.

The shaded range represented the middle 50% of recording PSDs.
It was not a confidence interval or the full range.

| Setting | K001 | K002 | KA04 | KI04 |
|---|---:|---:|---:|---:|
| N09_M07_F10 | 16 | 18 | 19 | 16 |
| N15_M01_F10 | 16 | 18 | 17 | 19 |
| N15_M07_F04 | 10 | 20 | 18 | 15 |
| N15_M07_F10 | 16 | 19 | 18 | 17 |

Documented operating settings:

| Setting | Speed | Torque | Radial force |
|---|---:|---:|---:|
| N09_M07_F10 | 900 rpm | 0.7 Nm | 1,000 N |
| N15_M01_F10 | 1,500 rpm | 0.1 Nm | 1,000 N |
| N15_M07_F04 | 1,500 rpm | 0.7 Nm | 400 N |
| N15_M07_F10 | 1,500 rpm | 0.7 Nm | 1,000 N |

These were documented settings, not measured channel values.

## Main observations

1. Healthy bearings K001 and K002 had noticeably different spectra.
2. Strong individual peaks occurred in healthy recordings.
3. Several recordings shared broad spectral regions near
   approximately 3–4, 6, 8 and 10 kHz.
4. KA04 showed pronounced low-frequency content and strong
   spectral clusters below approximately 11 kHz.
5. Many spectral patterns recurred across repetitions.
6. Spectral strength and shape changed with operating settings.
7. The high-frequency background differed between bearings and
   remained broadly repeatable. Its physical source was unresolved.

Observations were visual and exploratory. Numerical band-power
measurements are needed to quantify differences.

## Implications for the project

- Use several complementary features rather than assuming
  maximum amplitude alone identifies faults.
- Preserve operating-setting metadata for later evaluation.
- Investigate background-level differences as possible measurement
  or bearing-specific effects.
- Treat observed frequency regions as candidates for investigation,
  not confirmed fault bands.
- Retain bearing-separated evaluation to assess generalization.

The 272 recordings represent repeated measurements of only
four physical development bearings.

Results apply to the provisionally timing-screened subset.
Unequal exclusions may affect which recordings are represented.

