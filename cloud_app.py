"""Streamlit Community Cloud entrypoint. Never uses the shared local DB."""
import os
from pathlib import Path
import sys
# Explicit source path avoids reliance on editable installation in hosted builds.
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(key,'1')
from researchmind.ui.workspace import main
main(cloud=True)
