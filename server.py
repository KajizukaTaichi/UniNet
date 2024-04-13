from flask import Flask, render_template
import json
from users import users
from flask_socketio import SocketIO
from flask_httpauth import HTTPBasicAuth

app = Flask("UniNet")
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins="*")
auth = HTTPBasicAuth()

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

def save_message(message):
    with open("messages.txt", "a") as f:
        f.write(json.dumps(message) + '\n')

def load_messages():
    messages = []
    try:
        with open("messages.txt", "r") as f:
            for line in f.readlines():
                messages.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return messages

def delete_message(message_content):
    try:
        with open("messages.txt", "r") as f:
            lines = f.readlines()
        with open("messages.txt", "w") as f:
            for line in lines:
                if json.loads(line.strip())['message'] != message_content:
                    f.write(line)
    except FileNotFoundError:
        pass

@socketio.on("connect")
@app.route('/')
@auth.login_required
def index():
    messages = load_messages()
    return render_template('index.html', username=auth.username(), messages=messages)

@socketio.on('message')
@auth.login_required
def handle_message(message):
    print('Received message:', message)
    save_message({'username': auth.username(), 'message': message})
    socketio.emit('message', f'{auth.username()}: {message}', namespace="/")

@socketio.on('delete_message')
@auth.login_required
def handle_delete_message(message):
    delete_message(message)
    socketio.emit('message_deleted', message, namespace="/")

if __name__ == '__main__':
    socketio.run(app, debug=True)
