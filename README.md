# Python + Rust: más allá del intérprete

Material de la charla de 20 minutos presentada en Python Conf Chile 2026 por Gonzalo Pincheira (Boolean Academia).

**Tesis:** Python y Rust no son alternativas excluyentes. Python conserva la interfaz y la productividad; los componentes críticos pueden correr en código nativo. Es una tradición que viene de C (NumPy) y que Rust continúa con PyO3 y maturin. Cruzar la frontera entre lenguajes tiene un costo, y conviene medirlo.

## Contenido

| Carpeta | Qué contiene |
|---|---|
| `demos/` | Las tres demos en vivo y el script que deja todo listo |
| `results/` | Mediciones con fecha, equipo y versiones (`resultados.md`) |
| `deck-snapshot/` | Copia en HTML de cada slide, con las notas de orador |

## Las demos

1. **Python contra Rust** (`count.py`, `count.rs`): contar los múltiplos de 7 entre 1 y N.
2. **Pydantic 1 contra Pydantic 2** (`llm_parser.py`): validar 100.000 respuestas simuladas de un LLM con el mismo modelo.
3. **Validación parcial en streaming** (`llm_stream.py`): validar un JSON mientras llega por partes, con Pydantic 2.10 o superior.

Ninguna demo llama a un modelo real: las respuestas son simuladas porque se mide el procesamiento, no la inferencia. Todos los datos son ficticios (clientes como ACME Ltda. o Demo Corp) y se generan con semilla fija en `make_responses.py`.

## Cómo ejecutarlas

Requisitos: Python 3.11, [uv](https://docs.astral.sh/uv/) y Rust (`rustc`).

```bash
cd demos
./prepare_live.sh        # crea los entornos, compila count.rs, genera los datos y verifica los resultados
```

Después, en el orden de la charla (más detalle en `demos/README.md`):

```bash
python3 count.py 100000000
./count 100000000
venv-v1/bin/python llm_parser.py v1 responses.jsonl
venv-v2/bin/python llm_parser.py v2 responses.jsonl
venv-v2/bin/python llm_stream.py
```

Si algo falla durante la charla, `./plan_b.sh 1|2|3` muestra la salida guardada de cada demo.

## Resultados

Las cifras medidas (mediana y rango de 5 ejecuciones, en un Apple M1) están en [`results/resultados.md`](results/resultados.md). Dependen del equipo y de las versiones: repite las mediciones antes de citarlas.

Un detalle importante: el Pydantic 1 de PyPI viene compilado con Cython, por lo que la diferencia con Pydantic 2 es menor que contra `pydantic.v1` en Python puro. Por eso la demo usa dos entornos separados.
