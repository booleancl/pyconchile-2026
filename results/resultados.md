# Resultados de las mediciones

- **Fecha:** 2026-11-13
- **Equipo:** Apple M1 (iMac21,2), 8 GB de RAM, macOS 26.6.1
- **Versiones:** Python 3.11.13, rustc 1.99.1 (`rustc -C opt-level=3`), Pydantic 1.10.27 (compilado, `venv-v1`), Pydantic 2.14.3 con pydantic-core 2.50.4 (`venv-v2`)
- **Método:** 5 ejecuciones por caso, se reporta la mediana y el rango (mín–máx). Una sola pasada, sin pausas entre ejecuciones y con el equipo en uso normal.

## Demo 1: contar múltiplos de 7 hasta N = 100.000.000 (resultado 14285714 en ambos)

Tiempo de pared del proceso completo (incluye el arranque del intérprete o del binario).

| Lenguaje | Mediana | Rango | Factor |
|---|---|---|---|
| Python (`count.py`) | 5,04 s | 4,84–5,23 s | referencia |
| Rust (`count`) | 0,062 s | 0,062–0,064 s | unas 81 veces más rápido |

## Demo 2: validar 100.000 respuestas (95.020 válidas, 4.980 inválidas en todos los casos)

Tiempo medido por el script (solo validación, sin leer el archivo). El script imprime con 2 decimales.

| Motor | Mediana | Rango | µs por respuesta | Factor frente a V2 |
|---|---|---|---|---|
| Pydantic 1.10.27, **compilado** (PyPI) | 2,00 s | 1,96–2,02 s | 20,0 | 6,3× |
| Pydantic 1 vía `pydantic.v1` (Python puro, compilado: False) | 2,66 s | 2,65–2,67 s | 26,6 | 8,3× |
| Pydantic 2.14.3 (núcleo Rust) | 0,32 s | 0,31–0,33 s | 3,2 | referencia |

### Lectura

- V1 está compilado con Cython en el caso principal (`compiled: True`), por eso el factor es 6,3× y no el cercano a 10× de las cifras de referencia, que usaban `pydantic.v1` en Python puro.
- Con `pydantic.v1` el factor sube a 8,3×. Ese caso solo conviene mencionarlo si se aclara qué V1 se usó.
- El factor es del orden de 6×, no una cifra que valga para cualquier modelo ni tamaño de respuesta. Las variantes del paso 4 lo van a matizar.

## Demo 3: streaming

La salida coincide con la de referencia (nada válido hasta los 36 caracteres; `priority` a los 48; primer producto a los 96; segundo a los 132; `notes` a los 164). A los 60 caracteres aparece `'items': []` antes del primer producto. No se midió tiempo: la demo usa pausas de 0,3 s por diseño.

## Variantes (paso 4)

Mismo equipo y versiones. Mediana de 5 ejecuciones dentro de un solo proceso (rango en la última columna), sin leer archivo en el tiempo medido.

### A. Tamaño de cada respuesta (20.000 pedidos válidos por caso)

| Productos por pedido | Bytes por respuesta | V1 compilado (µs) | V2 (µs) | Factor |
|---|---|---|---|---|
| 1 | 257 | 12,3 | 1,9 | 6,4× |
| 5 | 612 | 25,9 | 3,9 | 6,6× |
| 20 | 1.944 | 78,1 | 11,3 | 6,9× |

El factor casi no cambia con el tamaño (6,4× a 6,9×). Los dos crecen de forma proporcional.

### B. ¿Cuánto es `json.loads` y cuánto es validación? (98.700 respuestas con JSON bien formado)

| Paso | V1 compilado | V2 |
|---|---|---|
| `json.loads` solo (C, de la biblioteca estándar) | 0,32 s | 0,32 s |
| Validar desde el dict (`parse_obj` / `model_validate`) | 1,55 s | 0,24 s |
| Texto a objeto en una llamada (`parse_raw` / `model_validate_json`) | 1,93 s | 0,30 s |

- En V1, `json.loads` es cerca del 17% del total y la validación cerca del 80%. La validación es lo que domina.
- En V2, `model_validate_json` (parsea y valida) tarda lo mismo que `json.loads` solo. Hacer `json.loads` y luego `model_validate` en V2 costaría unos 0,56 s (suma de las dos filas), cerca del doble de la llamada única; esa suma no se midió directamente.
- La validación desde el dict es unas 6,5 veces más rápida en V2 (1,55 s frente a 0,24 s).

### C. 10.000 frente a 100.000 respuestas

| Respuestas | V1 compilado | V2 | Factor |
|---|---|---|---|
| 10.000 | 0,19 s | 0,030 s | 6,3× |
| 100.000 | 1,93 s | 0,30 s | 6,3× |

### D. Tiempo de cada validación parcial (demo 3, mediana de 2.000 repeticiones por punto)

Entre 0,5 y 1,5 µs por validación, desde los 12 hasta los 164 caracteres. Crece con el texto recibido pero sigue en microsegundos. Excluye `print` y la pausa de 0,3 s.

## Recomendaciones

1. **Demo 2: usar 100.000.** Con 10.000 los tiempos son 0,19 s y 0,03 s: terminan antes de que el público los registre. Con 100.000 son 2 s y 0,3 s, y se nota. El factor es el mismo.
2. **No mostrar otras variantes en vivo.** Tamaño y `json.loads` frente a validación son material para preguntas (o notas de orador): el factor no depende del tamaño y la validación es la parte cara de V1.
3. **Demo 3: mostrar el tiempo por validación solo si hay tiempo.** Es opcional y no cambia el mensaje.
