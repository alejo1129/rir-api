# Evidencias de validación — Milestone 1

Este documento reúne las validaciones realizadas sobre las funcionalidades implementadas en M1: generación de ruido rosa, generación de sine sweep y filtro inverso, y reproducción/grabación de audio.

## 1. Validación del ruido rosa

Se generó una señal de ruido rosa de 10 segundos a una frecuencia de muestreo de 44.100 Hz.

Para verificar su comportamiento espectral se calculó la densidad espectral de potencia mediante el método de Welch entre 100 Hz y 10 kHz.

La pendiente obtenida fue:

- Pendiente medida: **-3,17 dB/octava**

El resultado es consistente con el comportamiento esperado de un ruido rosa y se encuentra dentro del rango utilizado por los tests automáticos de M1.

![Espectro del ruido rosa](pink_noise_spectrum.png)

---

## 2. Validación del sine sweep

Se generó un sine sweep logarítmico con los siguientes parámetros:

- Frecuencia inicial: **20 Hz**
- Frecuencia final: **20.000 Hz**
- Frecuencia de muestreo: **44.100 Hz**
- Duración: **5 s**

Se calculó el espectrograma de la señal para verificar que la frecuencia aumente progresivamente desde el extremo inferior hasta el superior del rango especificado.

![Espectrograma del sine sweep](sine_sweep_spectrogram.png)

---

## 3. Validación del filtro inverso

Se convolucionó el sine sweep generado con su filtro inverso mediante `scipy.signal.fftconvolve()`.

El resultado esperado es una señal aproximadamente impulsiva, con un pico claramente dominante respecto del resto de la señal.

Resultado obtenido:

- Relación pico/resto: **89,1 dB**

Los tests automáticos de M1 requieren una relación mínima de **60 dB**, por lo que el resultado supera ampliamente el criterio de validación.

![Convolución del sweep con su filtro inverso](sweep_inverse_convolution.png)

---

## 4. Validación real de reproducción y grabación

La función `play_and_record()` también fue validada utilizando hardware de audio real.

Equipamiento utilizado:

- Interfaz de audio: **Focusrite**
- Entrada: **Focusrite Analogue 1 + 2**
- Salida: **Focusrite Altavoces**
- Frecuencia de muestreo: **48.000 Hz**

Prueba realizada:

- Duración de la señal reproducida: **0,5 s**
- Duración solicitada de grabación: **1,5 s**
- Muestras grabadas: **72.000**
- Valor máximo registrado: **0,0030517578125**
- RMS registrado: **0,000604360131546855**

La prueba confirmó que la función puede reproducir una señal mediante la interfaz física y mantener la grabación durante un tiempo superior al de la señal reproducida.

![Validación real de play_and_record](qa_play_and_record_real.png)

Los resultados numéricos de esta prueba se encuentran también en:

- `docs/m1/qa_play_and_record_real.txt`
- `docs/m1/qa_validacion_final_m1.txt`

---

## 5. Reproducibilidad

Las tres validaciones gráficas pueden regenerarse mediante:

```bash
uv run python -m scripts.generate_m1_evidence
```

El script utilizado se encuentra en:

`scripts/generate_m1_evidence.py`

Las mismas comprobaciones empleadas para generar estas evidencias están basadas en los criterios implementados en `tests/test_generacion.py`.