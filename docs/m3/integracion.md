

# M3 â€” GuÃ­a de integraciÃ³n y validaciÃ³n

## Objetivo

Documentar el proceso de integraciÃ³n de los componentes del Milestone 3 de RIR-API, verificar su funcionamiento conjunto y facilitar la revisiÃ³n de los Pull Requests antes de la entrega.

## Componentes y contribuciones

| Componente | ContribuciÃ³n | Referencia |
|---|---|---|
| Suavizado | Pruebas de validaciÃ³n de entradas | PR de validaciÃ³n de smoothing |
| Integral de Schroeder | Pruebas matemÃ¡ticas | PR #65 |
| RegresiÃ³n lineal | Pruebas de pendiente negativa e invariancia de orden | PR #66 |
| ParÃ¡metros acÃºsticos | Pruebas de invariancia de amplitud y comparaciÃ³n de T30 | PR #67 |
| Integral de Schroeder | ImplementaciÃ³n y pruebas de robustez | PR #68 |

Los PR deben revisarse y aprobarse antes de considerarlos integrados en `main`.

## Checklist de integraciÃ³n

- [x] Confirmar revisiÃ³n y aprobaciÃ³n de los PR.
- [x] Verificar que no existan conflictos entre ramas.
- [x] Integrar las funciones de procesamiento acÃºstico.
- [x] Revisar las marcas `XFAIL` de las pruebas ya implementadas.
- [x] Ejecutar Ruff y la suite completa de Pytest.
- [x] Verificar los endpoints de M3.
- [x] Registrar los resultados finales de validaciÃ³n.
- [x] Actualizar la documentaciÃ³n de entrega.

## Comandos de validaciÃ³n

Ejecutar desde la raÃ­z del repositorio:

```powershell
uv run ruff check app/ tests/
uv run ruff format --check app/ tests/
uv run pytest -q
```

Para verificar Schroeder despuÃ©s de integrar su implementaciÃ³n:

```powershell
uv run pytest -v tests/test_analisis.py -k "schroeder" --runxfail
```

La opciÃ³n `--runxfail` permite ejecutar temporalmente como pruebas normales aquellas que todavÃ­a tengan la marca `XFAIL`.

## Consideraciones tÃ©cnicas

La integral de Schroeder debe devolver una curva de decaimiento energÃ©tico normalizada en dB.

Se deben verificar:

- Longitud de salida igual a la entrada.
- Valor inicial de 0 dB.
- Decaimiento energÃ©tico monÃ³tono.
- Invariancia frente al escalado de amplitud.
- Comportamiento definido ante entradas invÃ¡lidas y seÃ±ales silenciosas.

La implementaciÃ³n propuesta en el PR #68 devuelve `ValueError` para seÃ±ales completamente silenciosas. Este criterio debe confirmarse durante la revisiÃ³n.

## Criterio de finalizaciÃ³n

M3 se considerarÃ¡ integrado cuando las funciones requeridas estÃ©n incorporadas a `main`, los tests correspondientes pasen sin fallos inesperados, los endpoints funcionen y la documentaciÃ³n refleje el estado real del proyecto.
