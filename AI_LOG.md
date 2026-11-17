# Registro de Uso de Herramientas de IA (AI_LOG.md)

Registro estructurado de las consultas realizadas a asistentes de inteligencia artificial durante el desarrollo de **RIR-API** (Se?ales y Sistemas ? UNTREF, 2C 2026), cumpliendo con los cinco campos exigidos por la c?tedra para cada entrada.

---

## Entrada 1 ? Dise?o de arquitectura modular y diagrama Mermaid
- **Fecha y Milestone:** 05/10/2026 ? Milestone 0 (El plano)
- **Herramienta:** ChatGPT (OpenAI) / Gemini (Google)
- **Consulta realizada:** C?mo estructurar la separaci?n de responsabilidades entre routers HTTP (`FastAPI`), esquemas (`Pydantic`) y servicios (`NumPy`/`SciPy`), y c?mo diagramar el flujo de datos en Mermaid.
- **Resultado obtenido:** Esqueleto de paquetes (`app/routers`, `app/schemas`, `app/services`) y diagrama `flowchart TB` con las conexiones entre capas.
- **Evaluaci?n:** Fue ?til para establecer la base del proyecto. Se modificaron las etiquetas de las flechas para indicar el nombre exacto de cada funci?n invocada y se aprendi? a aislar la conversi?n de archivos WAV temporales en `audio_http.py`.

## Entrada 2 ? Algoritmo de Voss-McCartney y filtro inverso de Farina
- **Fecha y Milestone:** 22/10/2026 ? Milestone 1 (Generaci?n de se?ales)
- **Herramienta:** ChatGPT / Gemini
- **Consulta realizada:** Formulaci?n matem?tica de la envolvente de compensaci?n energ?tica del filtro inverso para un sine sweep logar?tmico y generaci?n temporal de ruido rosa mediante Voss-McCartney.
- **Resultado obtenido:** Implementaci?n vectorizada del barrido exponencial con modulaci?n `exp(-t * r / duration)` sobre el sweep invertido y suma acumulativa por octavas para el ruido rosa.
- **Evaluaci?n:** Muy ?til. Se ajust? la normalizaci?n a `float64` entre -1 y 1 y se verific? mediante `test_sweep_convolution_impulse` (relaci?n pico/resto de 89,1 dB, superando los 60 dB exigidos) y `test_pink_noise_spectrum` (-3,17 dB/oct).

## Entrada 3 ? Pre-roll en `play_and_record` y mocks para CI
- **Fecha y Milestone:** 27/10/2026 y 12/11/2026 ? Milestone 1 (Generaci?n de se?ales)
- **Herramienta:** ChatGPT
- **Consulta realizada:** C?mo compensar la latencia inicial de PortAudio en `sounddevice.playrec` y c?mo simular el dispositivo de audio en GitHub Actions sin hardware f?sico.
- **Resultado obtenido:** L?gica de padding con 0,5 s de silencio inicial (pre-roll) y creaci?n de un m?dulo falso con `monkeypatch` en `tests/test_generacion.py`.
- **Evaluaci?n:** Se adapt? el c?digo en `app/services/audio_io.py` para manejar arrays 1D y 2D y se valid? con una interfaz Focusrite USB Audio a 48 kHz registrando un pico de -6,02 dBFS y 0 muestras con clipping.

## Entrada 4 ? Filtrado Butterworth IEC 61260 y control de Nyquist
- **Fecha y Milestone:** 02/11/2026 y 15/11/2026 ? Milestone 2 (Procesamiento de la RI)
- **Herramienta:** ChatGPT / Gemini
- **Consulta realizada:** Dise?o del filtro pasabanda de octava de fase cero (`sosfiltfilt`) y manejo de errores cuando `center_freq` supera la frecuencia de Nyquist en el endpoint `/api/v1/filters/single-band`.
- **Resultado obtenido:** Validaci?n expl?cita `if f_low >= nyquist: raise ValueError(...)` en `filter.py` y captura de `ValueError` en el router para devolver HTTP 422 en lugar de HTTP 500.
- **Evaluaci?n:** Permiti? resolver la observaci?n de la c?tedra en la devoluci?n de M2. Se incorpor? el test `test_filter_frequency_above_nyquist_returns_422` para garantizar el contrato HTTP.

## Entrada 5 ? Ventana de pre-trigger de 5 ms en deconvoluci?n y an?lisis
- **Fecha y Milestone:** 03/11/2026 y 16/11/2026 ? Milestone 2 y Milestone 3
- **Herramienta:** ChatGPT / Gemini
- **Consulta realizada:** Efecto del recorte exacto en el pico directo sobre el transitorio de los filtros IIR bidireccionales (`sosfiltfilt`) en bandas bajas.
- **Resultado obtenido:** Recomendaci?n de conservar un margen de ~5 ms previo al pico m?ximo tanto en `get_impulse_response()` como al inicio de `calculate_parameters_from_ir()`.
- **Evaluaci?n:** Fundamental para estabilizar el EDT en 125 Hz y 250 Hz. Se implement? `start_idx = max(0, peak_idx - pretrigger_samples)` y se agregaron los tests unitarios de pre-trigger y silencio inicial.

## Entrada 6 ? Integral de Schroeder, criterio de rango din?mico y D50/C80 desde arribo directo
- **Fecha y Milestone:** 14/11/2026 al 17/11/2026 ? Milestone 3 (Producto final)
- **Herramienta:** ChatGPT / Gemini
- **Consulta realizada:** C?lculo de EDT, T10, T20, T30, D50 y C80 seg?n ISO 3382-1, verificaci?n de rango din?mico m?nimo (`abs(db_end) + 10 dB`) y punto de inicio para integraci?n de energ?a temprana/tard?a.
- **Resultado obtenido:** Implementaci?n de `_estimate_dynamic_range_db()`, retorno de `None` (`null` en JSON) cuando la relaci?n se?al/ruido es insuficiente, e inicio de integraci?n de D50 y C80 desde el pico de cada banda filtrada (`n0 = np.argmax(np.abs(band_ir))`).
- **Evaluaci?n:** Inicialmente D50 y C80 se integraban desde el ?ndice 0 (incluyendo el pre-trigger de 5 ms), lo que introduc?a diferencias en C80 frente a software de referencia. Se corrigi? en el PR #88 tomando `n0` por banda y se verific? con tests unitarios y de contrato OpenAPI.
