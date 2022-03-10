from flask import session , redirect , url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio

import QKD

from pymongo import MongoClient
uri = "mongodb+srv://cluster0.lqhp7.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='X509-cert-6149628929739843258.pem')
db = client['UserDB']
data = db['user_data']





@socketio.on('create')
def create_user(nickname):
    """Creating a user id."""
    from random import randint
    user_id = str(randint(1000, 9999))
    user_name = nickname + user_id

    payload = {"_id": user_name, "friend_requests": [], "keys": {}, "friends" : []}

    data.insert_one(payload)




    return redirect(url_for(f'.{user_name}'))








#Frined req tuple contain three thing - (friend_id , qubits , indices)

@socketio.on('connect')
def connect(friend_id):
    user_name = session.get('user_name')
    if user_name == "":
        return redirect(url_for('./home'))

    friend_data = data.find_one({"_id": str(friend_id)})

    if friend_data is None:
        print("the username you typed is not registerd")

    #Alice here refers to the person who is sending the friend request
    else:
        qubits, alice_bases = QKD.genkey()
        indices = QKD.compute_indices(alice_bases)
        package = (user_name, qubits, indices)

        friend_requests = friend_data['friend_requests']
        friend_requests.append(package)

        data.update_one({"_id": friend_id}, {"$set": {"friend_requests": friend_requests}})

        print("Sent Friend Request")



@socketio.on('accept_connection')
def accept_connection():
    """This will be triggered when a friend request has been accepted"""

    user_name = session['user_name']

    personal_data = data.find_one({"_id": user_name })
    friend_requests = personal_data['friend_requests']
    for x in friend_requests: #X is a tuple here

        alice_id, qubits, indices = x
        key = QKD.construct_key_from_indices(qubits, indices)

        #Tuple with Username and Key
        key_for_alice = (user_name, key)

        alice_data = data.find_one({"_id": alice_id})
        alice_keys = alice_data['keys']
        alice_keys[user_name] = key


        

        bob_data = data.find_one({"_id": user_name})
        bob_keys = bob_data['keys']

        bob_keys[alice_id] = key

        #sending the data to the database
        data.update_one({"_id": user_name}, {"$set": {"keys": bob_keys}})

        data.update_one({"_id": alice_id}, {"$set": { "keys": alice_keys }})



    

