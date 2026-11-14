#!/usr/bin/env bash
# Plan B: show the saved output of a demo (made by prepare_live.sh).
# Usage: ./plan_b.sh 1|2|3
cd "$(dirname "$0")"
case "${1:-}" in
    1) cat backup/demo1.txt ;;
    2) cat backup/demo2_v1.txt; echo; cat backup/demo2_v2.txt ;;
    3) cat backup/demo3.txt ;;
    *) echo "Usage: ./plan_b.sh 1|2|3"; exit 1 ;;
esac
echo
echo "(saved output from the rehearsal, not a live run)"
