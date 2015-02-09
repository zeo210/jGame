web: gunicorn -k flask_sockets.worker app:app
init: python db_create.py
upgrade: python db_upgrade.py