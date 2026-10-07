# Documentacion de RIR-API

## Estructura

Este directorio contiene la documentacion del proyecto. Se recomienda organizar los
archivos de la siguiente manera:

```
docs/
├── README.md              # Este archivo
├── teoria/                # Notas teoricas y referencias
│   ├── iso_3382.md        # Resumen de la norma ISO 3382
│   └── parametros.md      # Explicacion de EDT, T20, T30
├── mediciones/            # Reportes de mediciones realizadas
│   └── sala_ejemplo.md    # Informe de una medicion
└── imagenes/              # Graficos y diagramas generados
```

## API de referencia

Explorar la [documentacion interactiva de la API de la catedra](https://rir-api.onrender.com/docs)
para entender la estructura de endpoints, schemas y respuestas esperadas.

## Referencias utiles

- **ISO 3382-1:2009** — Acoustics — Measurement of room acoustic parameters.
- Farina, A. (2000). *Simultaneous measurement of impulse response and distortion
  with a swept-sine technique.*
- Schroeder, M. R. (1965). *New method of measuring reverberation time.*
  The Journal of the Acoustical Society of America.
- Lundeby, A. et al. (1995). *Uncertainties of measurements in room acoustics.*
  Acta Acustica.
- [FastAPI: documentacion oficial](https://fastapi.tiangolo.com/)
- [Pydantic: validacion de datos](https://docs.pydantic.dev/)

## Notas

Cada milestone deberia documentarse brevemente en este directorio, incluyendo:

1. Decisiones de diseno tomadas.
2. Resultados de validacion (graficos, tablas comparativas).
3. Problemas encontrados y como se resolvieron.
