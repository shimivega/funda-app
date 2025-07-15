web: gunicorn --bind 0.0.0.0:$PORT main:app
release: python -c "from app import app, db; app.app_context().push(); db.create_all()"