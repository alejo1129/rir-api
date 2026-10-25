import numpy as np

def generate_pink_noise(duration: float, fs: int) -> np.ndarray:
    # Usamos el método de Voss-McCartney en lugar de filtrar ruido blanco 
    # por FFT para trabajar directo en el dominio del tiempo. 
    # Con esto evitamos que el ruido se vuelva cíclico o repetitivo en 
    # archivos largos, logrando una señal continua y aperiódica.
    
    n_samples = int(duration * fs)
    num_rows = 16
    rng = np.random.default_rng()
    
    rows = rng.standard_normal(num_rows)
    running_sum = np.sum(rows)
    pink = np.zeros(n_samples, dtype=np.float64)
    
    for i in range(n_samples):
        if i == 0:
            idx = 0
        else:
            temp = i
            idx = 0
            while (temp & 1) == 0 and idx < num_rows - 1:
                temp >>= 1
                idx += 1
        
        running_sum -= rows[idx]
        rows[idx] = rng.standard_normal()
        running_sum += rows[idx]
        
        pink[i] = running_sum + rng.standard_normal()
        
    max_val = np.max(np.abs(pink))
    if max_val > 0:
        pink /= max_val
        
    return pink