# GCU-BookHaven – Book Platform with unique exchange feature

<p align="center">
  <img src="static/icon.svg" alt="BookHaven Icon" width="500" height="500"/>
</p>

<p align="center">
  BookHaven is a full‑stack web platform for academic content discovery and exchange. Students can browse and purchase books, stream audiobooks in the browser, list second‑hand books for donation or swap, and discover nearby bookstores on an interactive map. Admins manage catalog, orders, exchanges, and users via a secured dashboard.
</p>

---

## Overview
BookHaven is a full‑stack web platform for academic content discovery and exchange. Students can browse and purchase books, stream audiobooks in the browser, list second‑hand books for donation or swap, and discover nearby bookstores on an interactive map. Admins manage catalog, orders, exchanges, and users via a secured dashboard.

## Features
- **Catalog & Search**: title/author/genre search, filters by format (audio/physical), rating, availability, trending.
- **Audiobook Streaming**: HTML5 audio player with seek and volume controls.
- **Cart & Checkout**: add/remove items, order history, JazzCash sandbox integration.
- **Exchange & Donation**: list used books with condition/status; admin moderation.
- **Map Store Locator**: Leaflet.js + OpenStreetMap with pins and details.
- **Auth & Roles**: email/password + (optional) Google OAuth2; RBAC for admin.
- **Recommendations**: trending and recently viewed sections, ready for ML later.
- **Responsive UI**: mobile‑first pages for all common browsers.
- **Security**: HTTPS-ready, CSRF protection, PBKDF2 password hashing.
- **Admin Dashboard**: CRUD for books, users, genres, orders, exchanges.

## Tech Stack
- **Backend**: Python 3.11, Django 5.x, Django ORM
- **Database**: MySQL 8 (SQLite for local dev ok)
- **Frontend**: HTML5, CSS3/Bootstrap, Jinja templates, vanilla JS
- **Maps**: Leaflet.js + OpenStreetMap
- **Payments**: JazzCash (sandbox mode for test flows)
- **Auth**: Django auth; optional `django-allauth` for Google OAuth2
- **Misc**: Pydub for audio processing, Celery (optional) for async tasks

## Architecture
- Presentation: HTML, CSS, JS
- Application: Django views + services, RBAC, session management
- Data: SQLite
- Integrations: JazzCash (redirect + server‑side verification), Leaflet map
- Media: protected image/audio delivery; static/media separation for production

## Quickstart
### Prerequisites
- Python 3.11+
- MySQL 8 (or SQLite for local dev)

### Setup
```bash
git clone https://github.com/mE-uMAr/GCU-BookHaven
cd bookhaven

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

#DB migrations:
python manage.py makemigrations
python manage.py migrate

#Sample data seeding
python manage.py seed

#Models activations and recommendations generations
python manage.py build_recommendations

#For production
python manage.py collectstatic --noinput

python manage.py runserver
```

Open http://127.0.0.1:8000 and /admin.

## Configuration
Use environment variables (via `python-decouple` or `django-environ`):

| Key | Example | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | `django-insecure-...` | Django secret |
| `DEBUG` | `True` | Set `False` in production |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma‑sep hosts |
| `DB_ENGINE` | `django.db.backends.mysql` | DB engine |
| `DB_NAME` | `bookhaven` | Database name |
| `DB_USER` | `bookhaven` | DB user |
| `DB_PASSWORD` | `********` | DB password |
| `DB_HOST` | `127.0.0.1` | DB host |
| `DB_PORT` | `3306` | DB port |
| `JAZZCASH_MERCHANT_ID` | `...` | Sandbox merchant id |
| `JAZZCASH_PASSWORD` | `...` | Sandbox password |
| `JAZZCASH_INTEGERITY_SALT` | `...` | Sandbox integrity salt |
| `SITE_URL` | `http://127.0.0.1:8000` | Public base URL used for callbacks |
| `GOOGLE_CLIENT_ID` | `...` | Optional OAuth |
| `GOOGLE_CLIENT_SECRET` | `...` | Optional OAuth |

Create a `.env.example` and keep real keys in `.env` (untracked).

### Static & Media
- `STATIC_ROOT` for collected static files
- `MEDIA_ROOT` for user uploads (covers + audio)

Ensure your web server serves `/static/` and `/media/` efficiently (e.g., via Nginx).

## Payments: JazzCash (Sandbox)
Flow:
1. Create transaction metadata server‑side (amount, txn ref, hashes).
2. Redirect user to JazzCash sandbox URL.
3. JazzCash returns result to your backend callback.
4. Verify response (integrity) and mark order paid/unpaid.
5. Store gateway logs for audit.

> Keep gateway credentials in `.env`. Never expose hashes in client code.

## Map & Geolocation
- Leaflet.js + OSM tiles for store pins.
- Store model includes latitude/longitude; markers rendered dynamically.
- Graceful degradation if geolocation is blocked.

## Audiobooks
- Store audio files under `MEDIA_ROOT` with protected URLs.
- HTML5 audio player in book detail view.
- Optionally pre‑process via `pydub` for consistent bitrate/duration.

## Testing
```bash
pytest -q        # or: python manage.py test
```
## Coverage targets:
- models, forms, views
- purchase flow (cart → payment → order)
- exchange listing submission and moderation
- audio streaming permission checks

## Security Notes
- Enforce HTTPS in production.
- CSRF enabled on forms and cookie‑secured sessions.
- Validate and sanitize all uploads; restrict audio/image MIME types.
- Rotate JazzCash keys; store minimal PII; follow local data laws.

## Deployment
- Render/Railway/Dokku/Generic VPS with Gunicorn + Nginx
- `.env` for secrets, `collectstatic`, DB migrations, backups, log rotation

## Roadmap
- EasyPaisa and card gateways
- Real‑time store inventory sync
- ML recommendations and spam/abuse detection
- Native mobile apps (Flutter/React Native)
- Push notifications and live chat

## License
This repository is delivered for client use. If you plan to open‑source, add a license (MIT/Apache‑2.0). Otherwise treat as **Proprietary**.

— Generated 2025-08-26
