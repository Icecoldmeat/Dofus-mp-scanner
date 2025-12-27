

## Start script using git bash

1) move to dofus-mp-scanner repo
2) source `.venv/Scripts/activate`
3) `export PYTHONPATH="$(pwd)/src:$(pwd)"`
4) `python commands/scanner.py`
5) check your path `python -c "import sys; print('\n'.join(sys.path))"`
