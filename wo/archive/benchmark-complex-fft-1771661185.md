# Benchmark 2: Complex Task - FFT Waveform Analysis (REAL DATA)

## Task

Complete a complex signal processing task on TRULY RANDOM DATA:

1. **Generate random data** - Create 44,100 random samples (16-bit) simulating real audio capture
2. **Treat as audio** - Array of values representing unknown audio samples from real source
3. **Run FFT** - Apply Fast Fourier Transform to extract frequency components
4. **Extract peaks** - Identify frequency peaks that naturally emerge from the random data
5. **Analyze results** - Report what frequencies are actually present (unknown in advance)

### Requirements
- Generate truly random audio data (np.random or equivalent - NOT synthetic tones)
- Do NOT pre-generate known frequencies
- Run actual FFT (numpy/scipy OK)
- Identify natural frequency peaks in the spectrum
- Report top 5-10 frequency peaks found (unknown in advance)
- Explain what you discovered about the data

### Accept Criteria
- FFT runs successfully on random data
- Identifies natural frequency peaks (not planted)
- Reports actual spectrum analysis results
- Code is complete and runnable
- Shows real signal processing (not synthetic test)

## Work Log

Starting complex FFT waveform benchmark...
PID: 26128 agent: ollama-qwen starting at 2026-02-21 02:06:25
