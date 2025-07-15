web: gunicorn main:app
web: gunicorn --bind 0.0.0.0:$PORT main:app
release: flask db upgrade