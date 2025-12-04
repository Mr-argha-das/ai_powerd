import sys
import os
from mangum import Mangum

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

try:
    from main import app
    application = Mangum(app)
except Exception:
    import traceback
    with open(os.path.join(PROJECT_DIR, "app_error.log"), "w") as f:
        f.write(traceback.format_exc())
    raise
