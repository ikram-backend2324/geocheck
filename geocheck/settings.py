"""
Django settings for geocheck project.
"""

import dj_database_url
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# In production (Render, etc.) set real values for these via environment
# variables. Locally, the fallbacks below just work out of the box.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-u^vwcd9!g-qe4a-3d&5oo7jv9ic(9ck8f_em8e4%l8ij5jljsu"
)
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")


INSTALLED_APPS = [
    'jazzmin',                       # must be above django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serves static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'geocheck.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'geocheck.wsgi.application'


DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get("DATABASE_URL")
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 4},
    },
]


LANGUAGE_CODE = 'en-us'

# Uzbekistan / Karakalpakstan — both use the same single timezone.
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise serves compressed, cache-busted static files directly from
# gunicorn in production — no separate nginx/CDN needed, and it's free.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
# Kept for compatibility with older tooling that still reads this setting
# directly instead of STORAGES["staticfiles"]["BACKEND"].
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Auth redirects ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'post_login_redirect'
LOGOUT_REDIRECT_URL = 'landing'

# How long (minutes) before the same user can log a fresh entry into the
# same zone again. Stops the GPS watcher from flooding the log every
# few seconds while someone just stands inside a zone.
CHECKIN_COOLDOWN_MINUTES = 15

# ---------------------------------------------------------------------------
# Jazzmin — drop-in replacement skin for the Django admin (used as the
# "control room" power-tools view at /admin/, alongside the custom
# /control/ dashboard built for everyday use).
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Perimetr Admin",
    "site_header": "Perimetr",
    "site_brand": "PERIMETR",
    "welcome_sign": "Welcome to the Perimetr control room",
    "copyright": "Perimetr",
    "search_model": ["auth.User", "core.Zone"],
    "user_avatar": None,

    "topmenu_links": [
        {"name": "Live feed (control room)", "url": "admin_dashboard"},
        {"name": "Zones", "url": "zone_list"},
        {"model": "auth.user"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "core", "core.zone", "core.entrylog"],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.zone": "fas fa-draw-polygon",
        "core.entrylog": "fas fa-satellite-dish",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "custom_css": "css/jazzmin-custom.css",
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "default_theme_mode": "dark",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "footer_fixed": False,
    "sidebar": "sidebar-dark-success",
    "sidebar_fixed": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "accent": "accent-success",
    "button_classes": {
        "primary": "btn-success",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
