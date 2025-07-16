web: gunicorn --bind 0.0.0.0:$PORT app:app
release: python -c "from app import app, db; app.app_context().push(); db.create_all()"