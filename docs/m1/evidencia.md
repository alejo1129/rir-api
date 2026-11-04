# Evidencias de validación — M1

## 1. Objetivo

Documentar las pruebas realizadas durante el milestone M1 — Generación de señales, incluyendo la validación automatizada y la prueba de reproducción y grabación con hardware real.

## 2. Validación de reproducción y grabación

Se realizó una prueba de la funcionalidad `play_and_record()` utilizando una interfaz de audio Focusrite, un parlante y un micrófono.

### Configuración registrada

| Parámetro | Valor |
|---|---|
| Frecuencia de muestreo | 48.000 Hz |
| Duración del tono | 0,5 s |
| Duración de grabación | 1,5 s |
| Muestras grabadas | 72.000 |
| Dispositivo de entrada | Focusrite Analogue 1 + 2 |
| Dispositivo de salida | Focusrite Altavoces |

### Resultados registrados

| Parámetro | Valor |
|---|---|
| Amplitud máxima | 0,0030517578125 |
| RMS | 0,000604360131546855 |

La prueba permitió registrar una señal de audio mediante el hardware utilizado. El informe de QA de M1 documenta la validación de `play_and_record()` con hardware real.

Los valores registrados no constituyen, por sí solos, una medición de latencia ni de relación señal/ruido.

### Evidencias

![Captura de la prueba de reproducción y grabación](qa_play_and_record_real.png)

- [Registro de la prueba de audio](qa_play_and_record_real.txt)

## 3. Validación automatizada

El informe de validación final de M1 registra los siguientes resultados:

| Verificación | Resultado |
|---|---|
| Pytest | 19 passed, 18 xfailed, 14 xpassed, 1 warning |
| Ruff check | All checks passed |
| Ruff format --check | 24 files already formatted |
| Estado del repositorio | Working tree clean en main |

Según el informe de QA, los tests correspondientes a M1 quedaron aprobados. Los resultados de `xfail` y `xpass` corresponden al estado del proyecto en el momento de aquella validación y no representan necesariamente su estado actual.

- [Informe original de validación final de M1](qa_validacion_final_m1.txt)

## 4. Evidencias gráficas pendientes de incorporar

Se deberá verificar la disponibilidad de las siguientes evidencias de procesamiento digital de señales antes de dar por completa la documentación gráfica de M1:

- Espectro del ruido rosa.
- Espectrograma del sine sweep.
- Resultado de la convolución del sweep con su filtro inverso.

Estas evidencias no se incluyen todavía porque no fueron identificadas entre los archivos disponibles de `docs/m1/`.

## 5. Conclusión

La documentación disponible respalda la ejecución de pruebas automatizadas de M1 y la realización de una prueba de reproducción y grabación con hardware real.

La incorporación de las evidencias gráficas de DSP queda pendiente de verificación con el equipo.