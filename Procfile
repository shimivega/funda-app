web: gunicorn main:app
release: python -c "from main import app, db; with app.app_context(): db.create_all()"