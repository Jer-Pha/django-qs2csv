"""
This Django project is only to run tests through GitHub's continuous
integration (CI) when this repo receives pull requests. It is not part
of the PyPI package: qs2csv. The only directory in the PyPI package is
qs2csv/src/. All other contents of this Django project are for testing
purposes only.
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = ["qs2csv"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
