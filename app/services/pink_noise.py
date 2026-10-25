import numpy as np

def generate_pink_noise(duration: float, fs: int = 44100, amplitude: float = 1.0) -> np.ndarray:
    """
    Genera ruido rosa aplicando un filtro 1/sqrt(f) al ruido blanco en el dominio de la frecuencia.
    """
    num_samples = int(duration * fs)
    
    # 1. Ruido blanco
    white_noise = np.random.randn(num_samples)
    
    # 2. Transformada de Fourier
    x = np.fft.rfft(white_noise)
    
    # 3. Filtro 1/f en potencia (1/sqrt(f) en amplitud)
    frequencies = np.fft.rfftfreq(num_samples, d=1/fs)
    frequencies[0] = 1.0  # Evitar división por cero
    
    pink_filter = 1.0 / np.sqrt(frequencies)
    x_pink = x * pink_filter
    
    # 4. Transformada inversa
    pink_noise = np.fft.irfft(x_pink, n=num_samples)
    
    # 5. Normalización
    max_val = np.max(np.abs(pink_noise))
    if max_val > 0:
        pink_noise = (pink_noise / max_val) * amplitude
        
    return pink_noise.astype(np.float32)