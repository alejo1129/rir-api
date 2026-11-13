\# M3 — Evidencia de procesamiento y validación



\## 1. Objetivo



Documentar y evaluar el funcionamiento de los algoritmos de procesamiento acústico implementados en RIR-API durante el Milestone 3.



Se presentan resultados obtenidos a partir de una respuesta impulsiva sintética, cuyos tiempos de reverberación son conocidos, y una respuesta impulsiva real correspondiente a una escalera.



Se incluyen gráficos de decaimiento energético, análisis por bandas de octava y resultados numéricos de los parámetros acústicos.



\## 2. Metodología



Se utilizaron dos respuestas impulsivas:



\- \*\*Señal sintética:\*\* generada mediante `generate\_synthetic\_ir`, con frecuencia de muestreo de 32 kHz y duración de 4,5 segundos. Se asignaron los siguientes valores de T60 por banda:



| Banda (Hz) | T60 objetivo (s) |

|---:|---:|

| 125 | 1,80 |

| 250 | 1,70 |

| 500 | 1,60 |

| 1000 | 1,50 |

| 2000 | 1,30 |

| 4000 | 1,10 |



\- \*\*Señal real:\*\* respuesta impulsiva de una escalera, almacenada en `docs/m2/audio/ri\_t60\_largo\_stairwell.wav`, con frecuencia de muestreo de 32 kHz.



Para ambas señales se calcularon EDT, T10, T20, T30, D50 y C80 en las seis bandas de octava consideradas.



El procesamiento incluye filtrado por bandas, integración inversa de Schroeder y regresión lineal sobre el tramo de decaimiento correspondiente.



\## 3. Evidencia gráfica



\### 3.1. Curva de Schroeder y regresión lineal



!\[Curva de Schroeder](images/curva\_schroeder.png)



La curva representa el decaimiento energético obtenido mediante la integral de Schroeder. La línea punteada representa el ajuste por regresión lineal en el intervalo seleccionado entre -5 y -35 dB.



Resultados del ajuste:



\- Pendiente: -35,0238 dB/s.

\- Intercepto: valor registrado en `validacion\_schroeder.csv`.

\- Coeficiente de determinación: R² = 0,99618.



El valor de R² indica un buen ajuste lineal en el intervalo analizado.



\### 3.2. Comparación del decaimiento por bandas — señal sintética



!\[Comparación por bandas sintética](images/comparacion\_bandas\_sintetica.png)



Se observa el decaimiento energético de la respuesta sintética luego del filtrado en las seis bandas de octava. Las diferencias entre curvas responden a los distintos tiempos de reverberación asignados durante la generación de la señal.



\### 3.3. Comparación del decaimiento por bandas — señal real



!\[Comparación por bandas escalera](images/comparacion\_bandas\_escalera.png)



Se presenta el decaimiento energético de la respuesta impulsiva real filtrada por bandas de octava. Se observan diferencias entre bandas, con un decaimiento más rápido en las frecuencias altas.



\## 4. Validación de la señal sintética



Se comparó el T30 calculado por RIR-API con los valores de T60 establecidos como referencia al generar la señal.



| Banda (Hz) | T60 objetivo (s) | T30 calculado (s) | Error relativo |

|---:|---:|---:|---:|

| 125 | 1,80 | 1,896 | 5,3 % |

| 250 | 1,70 | 1,748 | 2,8 % |

| 500 | 1,60 | 1,573 | 1,7 % |

| 1000 | 1,50 | 1,527 | 1,8 % |

| 2000 | 1,30 | 1,306 | 0,5 % |

| 4000 | 1,10 | 1,101 | 0,1

