# Demos: Python + Rust, más allá del intérprete

## 1. Python vs Rust (slide 2)

```bash
rustc -C opt-level=3 count.rs        # compilar antes de la charla
python count.py 100                  # 14: el público lo puede comprobar
python count.py 100000000
./count 100000000
```

## 2. Parser de respuestas LLM: Pydantic 1 vs 2 (slides 13 a 15)

Dos entornos, para que V1 corra con su versión real:

```bash
python -m venv venv-v1 && venv-v1/bin/pip install "pydantic<2"
python -m venv venv-v2 && venv-v2/bin/pip install "pydantic>=2.10"

python make_responses.py 100000 > responses.jsonl   # una vez, unos 44 MB

venv-v1/bin/python llm_parser.py v1 responses.jsonl
venv-v2/bin/python llm_parser.py v2 responses.jsonl
```

Los dos deben mostrar 95.020 válidas y 4.980 inválidas: es el mismo trabajo.
Si solo tienes Pydantic 2, `llm_parser.py v1` usa `pydantic.v1` (Python puro, más lento que el Pydantic 1 compilado de PyPI).

## 3. Streaming con validación parcial (slide 16)

```bash
venv-v2/bin/python llm_stream.py
```

Ninguna demo llama a un modelo real: las respuestas son simuladas para medir el procesamiento, no la inferencia.
