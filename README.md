# RankRush Exam Portal

This project is an online examination portal built with Django.

## Requirements

- Python 3.8.2 is needed to run this project.
- Install dependencies from `requirements.txt`.

## Run The Project

1. Open a terminal in the `Exam` folder.
2. Install the required packages.
3. Copy `.env.example` to `.env` and fill in the values.
4. Run:

```powershell
python manage.py runserver
```

If there are no errors, the website will run on:

```text
http://127.0.0.1:8000/
```

## Project Folder

The main Django project is inside the `Exam` directory.

## Deployment

This repo is prepared for low-risk deployment on PythonAnywhere without a Django upgrade first.

- Set `DEBUG=False`
- Set `ALLOWED_HOSTS` to your domain, for example `yourusername.pythonanywhere.com`
- Run `python manage.py migrate`
- Run `python manage.py collectstatic`

See `DEPLOY_PYTHONANYWHERE.md` for the full checklist.
