# PythonAnywhere Deployment

This project is set up to deploy on PythonAnywhere with the current Django version to minimize upgrade risk.

## 1. Create the web app

- Create a PythonAnywhere account.
- Create a new web app using manual configuration.
- Choose Python `3.8` or `3.9` so it stays compatible with `django==3.1.3`.

## 2. Upload the code

- Open a Bash console on PythonAnywhere.
- Clone your repository.
- Change into the project folder:

```bash
cd ~/your-repo/Exam
```

## 3. Create a virtual environment

```bash
mkvirtualenv --python=/usr/bin/python3.9 rankrush-env
pip install -r requirements.txt
```

If Python `3.9` is not available on your account, use Python `3.8` instead.

## 4. Configure environment variables

Create `.env` in the `Exam` folder. Start from `.env.example`.

Minimum production values:

```env
SECRET_KEY='replace-with-a-long-random-secret'
DEBUG='False'
ALLOWED_HOSTS='yourusername.pythonanywhere.com'
CSRF_TRUSTED_ORIGINS='https://yourusername.pythonanywhere.com'
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.example.com'
EMAIL_HOST_USER='your-email@example.com'
DEFAULT_FROM_EMAIL='your-email@example.com'
EMAIL_PORT='587'
EMAIL_USE_TLS='True'
EMAIL_HOST_PASSWORD='your-email-password'
```

If you are on a free PythonAnywhere account, standard SMTP can be limited. In that case use Gmail SMTP if allowed on your account, or switch to an email API provider.

## 5. Run Django setup commands

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Optional admin user:

```bash
python manage.py createsuperuser
```

## 6. Configure the WSGI file

In the PythonAnywhere web app tab, edit the WSGI file and make sure the project path is on `sys.path`, then point Django at your settings module:

```python
import os
import sys

path = '/home/yourusername/your-repo/Exam'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 7. Static and media mapping

In the PythonAnywhere web tab, add these mappings:

- URL `/static/` -> Directory `/home/yourusername/your-repo/Exam/staticfiles`
- URL `/media/` -> Directory `/home/yourusername/your-repo/Exam/media`

## 8. Reload the app

- Press Reload in the PythonAnywhere web tab.
- Visit `https://yourusername.pythonanywhere.com`

## Notes

- This project keeps SQLite for the first deployment because it is the lowest-risk option.
- Uploaded files live in `media/`, so keep backups if the site becomes important.
- A later upgrade to Django `5.2 LTS` would be a cleaner long-term maintenance step, but it is not required just to host the project.
