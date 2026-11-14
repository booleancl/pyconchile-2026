#!/usr/bin/env bash
# Prepare everything for the live talk and save the plan B outputs.
# Safe to run many times: it only creates what is missing.
# Usage: ./prepare_live.sh
set -euo pipefail
cd "$(dirname "$0")"

fail() { echo "ERROR: $1" >&2; exit 1; }

for tool in python3 rustc uv; do
    command -v "$tool" >/dev/null || fail "$tool is not installed"
done

echo "1/5 Python environments"
if [ ! -x venv-v1/bin/python ]; then
    uv venv venv-v1 --python 3.11 -q
    uv pip install -q --python venv-v1/bin/python "pydantic<2"
fi
if [ ! -x venv-v2/bin/python ]; then
    uv venv venv-v2 --python 3.11 -q
    uv pip install -q --python venv-v2/bin/python "pydantic>=2.10"
fi
venv-v1/bin/python -c "import pydantic; assert pydantic.VERSION.startswith('1.') and pydantic.compiled, 'V1 must be compiled Pydantic 1'"
venv-v2/bin/python -c "import pydantic; assert not pydantic.VERSION.startswith('1.')"

echo "2/5 Rust binary"
rustc -C opt-level=3 count.rs

echo "3/5 Simulated responses"
if [ ! -s responses.jsonl ]; then
    python3 make_responses.py 100000 > responses.jsonl
fi
[ "$(wc -l < responses.jsonl)" -eq 100000 ] || fail "responses.jsonl must have 100000 lines"

echo "4/5 Checks"
[ "$(python3 count.py 100)" = "14" ] || fail "count.py 100 should print 14"
[ "$(./count 100)" = "14" ] || fail "./count 100 should print 14"
for engine in "v1 venv-v1" "v2 venv-v2"; do
    set -- $engine
    out="$("$2/bin/python" llm_parser.py "$1" responses.jsonl)"
    echo "$out" | grep -q "valid: 95,020   invalid: 4,980" || fail "$1: unexpected valid/invalid counts"
done

echo "5/5 Plan B outputs in backup/"
mkdir -p backup
{
    echo '$ python count.py 100'; python3 count.py 100
    echo '$ python count.py 100000000'; ( time python3 count.py 100000000 ) 2>&1
    echo '$ ./count 100000000'; ( time ./count 100000000 ) 2>&1
} > backup/demo1.txt
{ echo '$ python llm_parser.py v1 responses.jsonl'; venv-v1/bin/python llm_parser.py v1 responses.jsonl; } > backup/demo2_v1.txt
{ echo '$ python llm_parser.py v2 responses.jsonl'; venv-v2/bin/python llm_parser.py v2 responses.jsonl; } > backup/demo2_v2.txt
{ echo '$ python llm_stream.py'; venv-v2/bin/python llm_stream.py; } > backup/demo3.txt

echo
echo "Ready. Live commands:"
echo "  python3 count.py 100000000 ; ./count 100000000"
echo "  venv-v1/bin/python llm_parser.py v1 responses.jsonl"
echo "  venv-v2/bin/python llm_parser.py v2 responses.jsonl"
echo "  venv-v2/bin/python llm_stream.py"
echo "If something fails on stage: ./plan_b.sh 1|2|3"
