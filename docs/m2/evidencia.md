# Evidencias de validación — M2

## 1. Generación de respuesta al impulso sintética

Se generó una respuesta al impulso sintética utilizando `generate_synthetic_ir()`, con una frecuencia de muestreo de 44.100 Hz y un T60 objetivo de 0,8 segundos en la banda de 1.000 Hz.

Para validar el tiempo de reverberación se filtró la señal en dicha banda y se calculó la integral de Schroeder. Luego se estimó el T60 mediante regresión lineal sobre el tramo comprendido entre -5 dB y -25 dB.

**Resultados:**
- T60 objetivo: 0,800 s.
- T60 estimado: 0,844 s.
- Error relativo: 5,5 %.

El resultado presenta una buena concordancia con el valor configurado.

![Respuesta al impulso sintética y curva de decaimiento](images/ri_sintetica_t60.png)

## 2. Recuperación de la respuesta al impulso mediante deconvolución

Se generó una respuesta al impulso de referencia y un barrido senoidal (*sine sweep*) de 2 segundos, entre 20 Hz y 20.000 Hz, utilizando `generate_sine_sweep_pair()`.

Se simuló la grabación del barrido al atravesar un sistema cuya respuesta al impulso era conocida, mediante una convolución. Posteriormente, se aplicó el filtro inverso utilizando `get_impulse_response()` para recuperar la respuesta al impulso.

Se compararon ambas señales mediante el coeficiente de correlación.

**Resultado:**
- Correlación entre la RI original y la recuperada: 1,0000.

La correlación obtenida demuestra una coincidencia prácticamente perfecta entre ambas respuestas en esta simulación.

![Comparación entre respuesta al impulso original y recuperada](images/deconvolucion.png)

## 3. Validación del filtro de banda de octava IEC 61260

Se evaluó la respuesta en frecuencia de `filter_single_band()` utilizando un filtro centrado en 1.000 Hz, con frecuencia de muestreo de 44.100 Hz.

Para obtener la respuesta se aplicó el filtro a un impulso unitario y se calculó su transformada rápida de Fourier (FFT). La magnitud se normalizó y se expresó en decibeles.

**Resultados obtenidos:**

| Frecuencia | Ganancia |
|---:|---:|
| 500 Hz | -52,21 dB |
| 707,11 Hz | -6,02 dB |
| 1.000 Hz | 0,00 dB |
| 1.414,21 Hz | -6,02 dB |
| 2.000 Hz | -52,55 dB |

La respuesta presenta una ganancia máxima en la frecuencia central, una atenuación de aproximadamente 6 dB en los límites de la banda y una atenuación superior a 50 dB en las frecuencias adyacentes.

La atenuación de aproximadamente 6 dB en los límites se debe a la aplicación del filtro en ambos sentidos mediante `sosfiltfilt()`.

![Respuesta en frecuencia del filtro de banda de octava](images/filtro_octava_1000hz.png)