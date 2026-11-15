# AI_LOG.md

# Registro de uso de herramientas de inteligencia artificial

Durante el desarrollo del proyecto RIR-API, correspondiente a la materia Señales y Sistemas (UNTREF), el equipo utilizó herramientas de inteligencia artificial como recurso de apoyo para interpretar consignas, analizar errores, revisar implementaciones, proponer pruebas y mejorar la documentación.

La inteligencia artificial se utilizó como asistente y no como sustituto del trabajo del equipo. Las propuestas obtenidas fueron revisadas por los integrantes y verificadas mediante ejecución local, pruebas automatizadas, controles de calidad, revisión de código y comparación con los requisitos de la cátedra.

## Herramientas utilizadas

- ChatGPT (OpenAI).
- Otras herramientas de asistencia basadas en inteligencia artificial utilizadas por los integrantes durante el desarrollo.

## M0 - Arquitectura y configuración inicial

Durante M0 se utilizó IA como apoyo para:

- Interpretar la estructura general del trabajo práctico y el checklist de arquitectura.
- Organizar la separación entre routers, services y schemas.
- Revisar la documentación inicial del repositorio y el diagrama de arquitectura en Mermaid.
- Analizar el flujo de trabajo con ramas, Pull Requests, reviews y protección de la rama `main`.
- Resolver dudas relacionadas con Git, GitHub y la configuración inicial del proyecto.

Las decisiones finales sobre la arquitectura, distribución de tareas y configuración del repositorio fueron revisadas por el equipo antes de incorporarse a `main`.

## M1 - Generación de señales

Durante M1 se utilizó IA como apoyo para:

- Interpretar los requisitos de generación de ruido rosa y sine sweep con filtro inverso.
- Analizar y depurar el funcionamiento de `play_and_record`.
- Revisar tests automatizados y el uso de marcas `xfail`.
- Detectar errores de implementación y proponer formas de verificarlos.
- Revisar docstrings y documentación de las funciones de generación.
- Organizar la evidencia correspondiente a las señales generadas y sus verificaciones.

Los resultados fueron comprobados mediante `pytest`, Ruff, CI y pruebas sobre los endpoints implementados.

## M2 - Procesamiento de la respuesta al impulso

Durante M2 se utilizó IA como apoyo para:

- Interpretar los requisitos de carga, filtrado y procesamiento de respuestas al impulso.
- Revisar la implementación del filtro de banda de una octava.
- Detectar y corregir casos límite relacionados con la frecuencia de Nyquist.
- Analizar la deconvolución mediante sine sweep y filtro inverso.
- Revisar el recorte de la respuesta al impulso para conservar aproximadamente 5 ms antes del pico principal.
- Diseñar y revisar tests para los servicios y endpoints de procesamiento.
- Organizar la validación con respuestas al impulso reales y la comparación con REW y el frontend de referencia.
- Revisar la documentación y evidencia correspondiente al milestone.

Las correcciones se verificaron mediante pruebas automatizadas, Ruff, CI, revisión por Pull Request y comparación con resultados de referencia.

## M3 - Producto final y análisis acústico

Durante M3 se utilizó IA como apoyo para:

- Interpretar los requisitos de cálculo de EDT, T10, T20, T30, D50 y C80 por banda.
- Revisar la integral de Schroeder, el suavizado y la regresión lineal.
- Analizar el criterio de rango dinámico mínimo y la devolución de `None` cuando un tiempo de reverberación no puede calcularse de forma válida.
- Revisar el contrato del endpoint `/api/v1/acoustics/parameters`.
- Implementar y verificar el schema `BandAnalysisResponse` y su documentación en OpenAPI.
- Revisar la serialización de valores `None` como `null` en JSON.
- Analizar el manejo de errores previsibles del procesamiento acústico mediante respuestas HTTP apropiadas.
- Diseñar y ampliar tests de API y de procesamiento acústico.
- Revisar la cobertura de tests del proyecto y localizar líneas sin cobertura.
- Auditar requisitos pendientes de la entrega final, documentación y preparación del repositorio.

Las implementaciones fueron verificadas mediante `pytest`, Ruff, cobertura de tests, CI, revisión de código y Pull Requests aprobados por otros integrantes.

## Criterio de utilización y validación

Las respuestas de las herramientas de IA no se incorporaron automáticamente al proyecto.

Para cada cambio relevante se siguió, según correspondiera, el siguiente proceso:

1. Comparación de la propuesta con la consigna y documentación oficial de la cátedra.
2. Revisión manual del código o documentación.
3. Ejecución de pruebas automatizadas.
4. Ejecución de Ruff y controles de formato.
5. Revisión del diff de Git antes de realizar el commit.
6. Integración mediante Pull Request y review de otro integrante cuando correspondía.
7. Validación adicional con señales, respuestas al impulso o software de referencia cuando la tarea lo requería.

Las decisiones finales de diseño, implementación, validación y documentación fueron responsabilidad del equipo.
