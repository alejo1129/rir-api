

# M3 — Guía de integración y validación

## Objetivo

Documentar el proceso de integración de los componentes del Milestone 3 de RIR-API, verificar su funcionamiento conjunto y facilitar la revisión de los Pull Requests antes de la entrega.

## Componentes y contribuciones

| Componente | Contribución | Referencia |
|---|---|---|
| Suavizado | Pruebas de validación de entradas | PR de validación de smoothing |
| Integral de Schroeder | Pruebas matemáticas | PR #65 |
| Regresión lineal | Pruebas de pendiente negativa e invariancia de orden | PR #66 |
| Parámetros acústicos | Pruebas de invariancia de amplitud y comparación de T30 | PR #67 |
| Integral de Schroeder | Implementación y pruebas de robustez | PR #68 |

Los PR deben revisarse y aprobarse antes de considerarlos integrados en `main`.

## Checklist de integración

- [ ] Confirmar revisión y aprobación de los PR.
- [ ] Verificar que no existan conflictos entre ramas.
- [ ] Integrar las funciones de procesamiento acústico.
- [ ] Revisar las marcas `XFAIL` de las pruebas ya implementadas.
- [ ] Ejecutar Ruff y la suite completa de Pytest.
- [ ] Verificar los endpoints de M3.
- [ ] Registrar los resultados finales de validación.
- [ ] Actualizar la documentación de entrega.

## Comandos de validación

Ejecutar desde la raíz del repositorio:

```powershell
uv run ruff check app/ tests/
uv run ruff format --check app/ tests/
uv run pytest -q
```

Para verificar Schroeder después de integrar su implementación:

```powershell
uv run pytest -v tests/test_analisis.py -k "schroeder" --runxfail
```

La opción `--runxfail` permite ejecutar temporalmente como pruebas normales aquellas que todavía tengan la marca `XFAIL`.

## Consideraciones técnicas

La integral de Schroeder debe devolver una curva de decaimiento energético normalizada en dB.

Se deben verificar:

- Longitud de salida igual a la entrada.
- Valor inicial de 0 dB.
- Decaimiento energético monótono.
- Invariancia frente al escalado de amplitud.
- Comportamiento definido ante entradas inválidas y señales silenciosas.

La implementación propuesta en el PR #68 devuelve `ValueError` para señales completamente silenciosas. Este criterio debe confirmarse durante la revisión.

## Criterio de finalización

M3 se considerará integrado cuando las funciones requeridas estén incorporadas a `main`, los tests correspondientes pasen sin fallos inesperados, los endpoints funcionen y la documentación refleje el estado real del proyecto.