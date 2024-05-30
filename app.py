from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send
from controller import execute_query
from config import SNOWFLAKE_CONNECTOR
from Patient.Users import users_api
from Doctor.Users import doctors_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc123d4'
app.register_blueprint(users_api)
app.register_blueprint(doctors_api)

socketio = SocketIO(app)

@app.route('/')
def home():
    if SNOWFLAKE_CONNECTOR:
        return render_template('index.html')
    else:
        return "Connection Issues"

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = data['username']
    message = f"{username}: {data['message']}"
    send(message, room=room)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)

@app.route('/joinRoom', methods = ['GET'])
def join_chat_rooms():
    return render_template('joinChatRoom.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
