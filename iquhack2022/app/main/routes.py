from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm

import os

from pymongo import MongoClient
uri = "mongodb+srv://cluster0.lqhp7.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='X509-cert-6149628929739843258.pem') #SECRET TO HIDE 
db = client['UsersDB']
data = db['user_data']


#mod.update_one({"_id" : user.id}, {"$set":{"user": warned_user,"warns" : warns_no, "reason":reason_list, "date" : date_list, "mod" : reason_mods }})



@main.route('/', methods=['GET', 'POST'])
@main.route('/home', methods=['GET', 'POST'])
def home():
    """Login form to enter the room"""


    form = LoginForm()
    if form.validate_on_submit():
        from random import randint


        nickname = form.name.data
        user_name = "DEFAULT"

        while user_name is not None:
            user_id = randint(1000, 9999)
            user_name = data.find_one({"_id": f"{nickname}#{user_id}" })
        
        user_name = str(nickname) + "#" + str(user_id) 
        payload = {"_id": user_name, "friend_requests": [], "keys": {}, "friends" : []}

        data.insert_one(payload)
        session['user_name']  = user_name #what is fspace in nickname 
        print(user_name)

        return redirect(f"/{user_name}")

    elif request.method == 'GET':
        form.name.data = session.get('name', '')
    return render_template('home.html', form=form)







@main.route('/<client>')
def client_page(client):
    """Client can connect with friends and generate Keys"""

    


    client = session['user_name']

    client_data = data.find_one({"_id":client })


    friend_req = client_data['friend_requests']
    #Friend Req is a list of tuples (friend_id , qubits, bases)
    


    return render_template('client.html', client = client, friend_requests = friend_req)
    #Pasing the friend req to the page




"""
@main.route('/<client>/<friend>')
def chat(client, friend):
    #Chat room. Key must be stroed in session
    name = session.get('name', '')
    room = session.get('key', '')
    if name == '' or room == '':
        return redirect(url_for('.home'))
    return render_template('chat.html', name=name, friend_id = friend, user_id =  client)
"""
