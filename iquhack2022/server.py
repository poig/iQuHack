"""The Server is the base for Classical Channel and due to the unavailbiltiy of physical quantum channel it mimics it in a classical manner"""

from datetime import timedelta
import requests
import os 

from random import getrandbits
import qiskit as q

#webserver imports
from flask import Flask, redirect , url_for , request, render_template , session
from flask_socketio import SocketIO

def timedec(func):
    def wrap(*args, **kwargs):
        import time
        t = time.time()
        ret = func(*args, **kwargs)
        print(f'Time taken when running {func.__name__}: {time.time() - t}')
        return ret
    return wrap




from ..main import socketio


@socketio.on('register')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    return "successfully joined"




KEY_LENGTH = 500
QUANTUM_CHANNEL = []
CLASSICAL_CHANNEL=[]



@timedec
def initialize_key (bob_id, encoded_qubits, Alice_bases):
    """This is initialization of key, server does not generate the key"""
    #contact bob_id an dsend qubits and bases
    #wait for reciing  indices from bob
    #send indices to Alice

    pass

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@timedec
def process_message(Alice, bob, content):
    #recive from Alice 
    #store maybe in db ?
    #send to bob 
    pass



@socketio.event
def create_user(data):
    print("New user created")
    print(data['user_name'])
















        
"""
@app.route("/dashboard/<int:guild_id>", methods= ['POST', 'GET'])
@app.route("/dashboard/<int:guild_id>/<module>", methods= ['POST', 'GET'])
@requires_authorization #bro if not autho then redirect to a diffrent page instead of sending them to discord like serioulsy
async def dashboard_modules(guild_id, module="overview"):

    if request.method == 'POST':
        data = await request.form
        print("[PAYLOAD RECIVED]", data.keys())

            



    return await render_template(
        f"{module}.html", guilds= guilds,
        user= user, title= "Leveling-Dashboard", username = "username",
        guild_id=guild_id, module=module,
        guild_channels = guild_channels, guild_roles= guild_roles, 
        guild_configs = guild_configs
        )


"""




