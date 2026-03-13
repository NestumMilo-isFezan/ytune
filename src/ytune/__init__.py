import locale
import os

os.environ["LC_NUMERIC"] = "C"
os.environ["LC_ALL"] = "C"
try:
    locale.setlocale(locale.LC_NUMERIC, "C")
    locale.setlocale(locale.LC_ALL, "C")
except Exception:
    pass

from .app import YTune


def main() -> None:
    app = YTune()
    app.run()
