from app import app, socketio

app.debug = True
socketio.run(app)
