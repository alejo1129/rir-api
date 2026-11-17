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

- [x] Confirmar revisión y aprobación de los PR.
- [x] Verificar que no existan conflictos entre ramas.
- [x] Integrar las funciones de procesamiento acústico.
- [x] Revisar las marcas `XFAIL` de las pruebas ya implementadas.
- [x] Ejecutar Ruff y la suite completa de Pytest.
- [x] Verificar los endpoints de M3.
- [x] Registrar los resultados finales de validación.
- [x] Actualizar la documentación de entrega.

## Comandos de validación

Ejecutar desde la raíz del repositorio:

```powershell
uv run ruff check app/ tests/
uv run ruff format --check app/ tests/
uv run pytest -q
```

## Criterio de finalización

M3 se considera integrado con todas las funciones incorporadas a `main`, los 80 tests pasando sin fallos, los endpoints operativos y la documentación actualizada.
