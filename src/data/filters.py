from scipy.signal import butter, filtfilt

def apply_lowpass_filter(series, cutoff=0.1, fs=1.0, order=2):
    """
    Applies a Butterworth low-pass filter to smooth out mobile sensor noise.
    Handles short signals gracefully.
    """
    if len(series) < 15:
        # Too short for filtfilt; return original series
        return series.values
    b, a = butter(order, cutoff, btype='low', fs=fs)
    return filtfilt(b, a, series)
