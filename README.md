# Perimetr — geofenced check-in

Django + SQLite + server-rendered templates. Users share their GPS in the
browser; the moment they walk into a zone you've drawn on the map, the
admin control room logs their username and the exact time. Maps on both
sides are Leaflet + OpenStreetMap (free, no API key). The landing page's
3D scenes are Three.js (also free, no API key).

**Everything here is free with no trial period and no card required.**
There is no Google Maps, no paid SDK, nothing that can suddenly start
billing you or expire mid-demo. The only things it talks to over the
network are: Google Fonts, the Leaflet/Three.js CDN scripts, and free
OpenStreetMap/CARTO map tiles.

## 1. Set up (one-time)

You need Python 3.10+ installed. Then, inside this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_admin        # creates the default admin account
```

That creates a default admin account — **username `admin`, password
`admin123`** — so you don't have to run `createsuperuser` by hand. It's
safe to run again later (on re-deploys, etc.): if the account already
exists it just skips and does nothing.

**Change that password before this goes anywhere public.** Easiest way:
log in as `admin` → go to `/admin/` → Users → admin → set a new password.
Or, set `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars *before* the first
time you run `seed_admin`, and it'll create the account with those
instead of the default.

## 2. Run it

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

- Log in with the superuser account → you land in the **control room**
  (`/control/`). Go to **Manage zones → + New zone**, click on the map to
  drop a center point, drag the slider for the radius, save.
- Open a second browser (or a private/incognito window, or your phone on
  the same Wi-Fi using your computer's local IP) and **register** a normal
  account → you land on the **live map** (`/dashboard/`). Click
  **Enable GPS**, allow location access, and walk toward (or simulate
  being inside) one of the zones the admin made.
- Back in the control room, the **live check-in feed** updates on its own
  every 5 seconds — no refresh needed — showing the username, zone, and
  timestamp.

## How roles work

There's no separate "admin" flag to set by hand for the first account —
whoever runs `createsuperuser` *is* the admin. To promote a regular
registered user to admin later, log in as the superuser, go to
`/admin/`, open **Users**, tick **"Staff status"** on their account, save.

## Two admin views

- **`/control/`** — the custom dark dashboard built for everyday use:
  live map, live polling feed, click-to-draw zones.
- **`/admin/`** — the full Django admin, skinned with **Jazzmin** (dark
  theme, branded sidebar) instead of the plain default admin. Use this
  for power-user stuff: bulk editing, deleting many rows at once,
  managing user accounts/permissions, exporting via the search/filter
  tools. Logging in from either `/login/` or `/admin/login/` works with
  the same account.

Both places where you create or edit a zone — `/control/zones/new/` and
`/admin/core/zone/add/` — show the same click-on-map picker. Latitude
and longitude are never typed by hand in either one; the map is the
only way to set them, which keeps the numbers honest.

## Testing GPS without actually traveling anywhere

Browsers let you fake your location for testing:
- **Chrome DevTools** → `⋮` → More tools → **Sensors** → set a custom
  latitude/longitude (use the exact coordinates you typed when creating
  the zone, give or take a tiny offset, to land "inside" it).
- On a phone, just physically being within the radius you set will work
  for real — handy for a live presentation.

## Project layout

```
geocheck/        Django settings & root URLs
core/             models, views, forms, urls (the actual app)
templates/        all HTML (dark "control-room" themed)
static/css        design system + jazzmin admin polish
static/js         the two Three.js scenes used on the landing page
```

## Deploying (Render or similar)

**Build command:**
```
pip install -r requirements.txt && python manage.py migrate && python manage.py seed_admin && python manage.py collectstatic --noinput
```

**Start command:**
```
gunicorn geocheck.wsgi:application
```

`seed_admin` creates the default admin (`admin` / `admin123`) the first
time it runs, then does nothing on every deploy after that — it never
touches an existing account, so it won't reset a password you've since
changed. To launch with different credentials from the start, set
`ADMIN_USERNAME` and `ADMIN_PASSWORD` as environment variables on the
host before the very first deploy.

Static files (including the Jazzmin admin assets) are served straight
out of gunicorn via **WhiteNoise**, compressed and cache-busted
(`STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"`)
— no separate static file host or CDN needed, still $0.

For production, set these environment variables on the host (all have
safe local defaults if you skip them, so nothing breaks while testing):

| Variable | Example | Why |
|---|---|---|
| `SECRET_KEY` | a long random string | Django needs a real one in production |
| `DEBUG` | `False` | Never leave debug pages on in production |
| `ALLOWED_HOSTS` | `your-app.onrender.com` | Comma-separated if more than one |
| `ADMIN_USERNAME` | (optional) | Used only the very first time `seed_admin` runs |
| `ADMIN_PASSWORD` | (optional) | Same — set both before the first deploy if you don't want `admin`/`admin123` |

## Notes for your presentation

- The geofence check is re-validated **server-side** (not just trusted
  from the browser), so it can't be faked by editing JavaScript.
- A cooldown (15 minutes by default, in `geocheck/settings.py` →
  `CHECKIN_COOLDOWN_MINUTES`) stops one person standing still from
  flooding the feed with duplicate entries.
- Timestamps are stored in UTC internally but always **displayed in
  Asia/Tashkent time** (`TIME_ZONE = 'Asia/Tashkent'` in settings) —
  correct for both Tashkent and Nukus/Karakalpakstan, since all of
  Uzbekistan uses one timezone.
