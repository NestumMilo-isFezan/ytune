import locale
try:
    locale.setlocale(locale.LC_NUMERIC, 'C')
except Exception:
    pass

from .app import YTune

def main() -> None:
    app = YTune()
    app.run()
