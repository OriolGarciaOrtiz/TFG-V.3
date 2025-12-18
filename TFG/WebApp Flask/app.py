
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fotos/<path:filename>')
def fotos(filename):
    return send_from_directory("fotos", filename)

@socketio.on('choose_role')
def handle_role(data):
    role = data['role']
    sid = request.sid

    if role == 'transmitter':
        rooms['transmitter'] = sid
        join_room('session')
        emit('waiting', {'msg': 'Esperando receptor...'}, to=sid)

    elif role == 'receiver':
        rooms['receiver'] = sid
        join_room('session')
        emit('waiting', {'msg': 'Esperando transmisor...'}, to=sid)

    if 'transmitter' in rooms and 'receiver' in rooms:
        emit('ready', {'msg': 'Conexión establecida'}, room='session')

@socketio.on('send_image')
def handle_image(data):
    if 'receiver' in rooms:
        emit('show_image', {'image': data['image']}, to=rooms['receiver'])


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)


# Movil: http://192.168.1.132:5000
# Movil si estamos en red local: http://10.219.188.39:5000
# PC: http://127.0.0.1:5000/



#Movil: http://192.168.1.132:5000
#Movil si estamos en red local (con los datos del movil: http://10.219.188.39:5000
#Pc:http://127.0.0.1:5000/
