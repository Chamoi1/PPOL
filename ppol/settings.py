import importlib.util
import os
import shutil
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde archivo .env si existe
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me-ppol-ucc-2026")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "core",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    *(
        ["whitenoise.middleware.WhiteNoiseMiddleware"]
        if importlib.util.find_spec("whitenoise")
        else []
    ),
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "ppol.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "core.context_processors.ppol_context",
    ]},
}]
WSGI_APPLICATION = "ppol.wsgi.application"

IS_VERCEL = bool(os.environ.get("VERCEL") or str(BASE_DIR).startswith("/var/task"))

# Base de datos: SQLite por defecto para Vercel o MySQL
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "ppol_db"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
elif DB_ENGINE == "sqlite":
    src_db = BASE_DIR / "db.sqlite3"
    # En Vercel (/var/task) solo se permite escribir en /tmp
    if IS_VERCEL:
        tmp_db = Path("/tmp/db.sqlite3")
        if not tmp_db.exists() and src_db.exists():
            shutil.copy2(src_db, tmp_db)
        db_name = tmp_db
    else:
        db_name = src_db

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_name,
        }
    }
else:
    raise ImproperlyConfigured(
        "DB_ENGINE debe ser 'mysql' para XAMPP o 'sqlite' para desarrollo local."
    )

# Usar sesiones en cookies firmadas por defecto con SQLite para que en entornos
# serverless (Vercel) la sesión no dependa de /tmp/db.sqlite3 (que es efímero y aislado por instancia).
SESSION_ENGINE = os.getenv(
    "SESSION_ENGINE",
    "django.contrib.sessions.backends.signed_cookies"
    if DB_ENGINE == "sqlite"
    else "django.contrib.sessions.backends.db",
)

AUTH_USER_MODEL = "core.User"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
if IS_VERCEL:
    src_media = BASE_DIR / "media"
    MEDIA_ROOT = Path("/tmp/media")
    if not MEDIA_ROOT.exists() and src_media.exists():
        shutil.copytree(src_media, MEDIA_ROOT, dirs_exist_ok=True)
    (MEDIA_ROOT / "cvs").mkdir(parents=True, exist_ok=True)
else:
    MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Las notificaciones por correo se imprimen en la consola (prototipo)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-responder@ppol.local"
