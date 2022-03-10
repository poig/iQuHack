# QuTech Challenges @ MIT iQuHACK 2022

<p align="left">
  <a href="https://qutech.nl" target="_blank"><img src="https://user-images.githubusercontent.com/10100490/151484481-7cedb7da-603e-43cc-890c-979fb66aeb60.png" width="25%" style="padding-right: 0%"/></a>
  <a href="https://iquhack.mit.edu/" target="_blank"><img src="https://user-images.githubusercontent.com/10100490/151647370-d161d5b5-119c-4db9-898e-cfb1745a8310.png" width="10%" style="padding-left: 0%"/> </a>
</p>


# Quantum Encryption 

This repository is for the submission from the Team NoSleep Consiting of ([Albert Lin](https://github.com/AlbertDoggyLin),[Jatin Khanna](https://github.com/Jatin-exe), [Tan Jun Liang](https://github.com/poig))

Why Quantum Encryption? 
Current Encryption algorithms assume that the breacher or eavesdropper does not has enough Computational Resources/Time or efficient algorithm to break the Encryption.

But the elegant part about Quantum Encryption is that it is based on assumption of the inability of the breacher/hacker to break the fundamental laws of physics.

This Repo is a Demonstration of an Online Chat Application using the BB84 Protocol


### BB84 Protocol
This Protocal utilizes the Heisenbergs Uncertainty Principle for its encryption.[BB84](https://www.cse.wustl.edu/~jain/cse571-07/ftp/quantum/)


## Description Of the Chat Application

This is a Web Application made on Flask Library as the UI for the Application. 

*the application is currenlty incomplete but we will finish it soon*

Flow of the Application:
*The Proposal is that every users has access to a Quantum Computer or a Quantum Channel which allows transfer of Photons which we will be using as our Qubits

Imagine two Users Alice and Bob, now imagine you are Alice.
-First head on to https://qkd.herokuapp.com/ and login with a Nickname, The Server will provide you a username accordingly, 
Now you can share your username to anyone you would like to talk to, 

- On  https://qkd.herokuapp.com/client you can add someone friend through their user_name. (ofc)

- Lets say you addded Bob#0007 as your Friend
- Once you sent the Friend Req, You are generating in the backend a random string of 500 qubits and measuring them in a random bias and sending the qubits to Bob through the Quantum Channle ( Optical Fibe. new breakthroughs here) to Bob$0007 he recives this as a Friend Request 

If he accepts your Friend Request, he will generate his own random bias ans measure the qubits , Then both the biases of Alice and Bob are shared and the identical indexes are noted the corresponding qubits of these identical Indices will be the key. 


Once both of the parties have the key they can use it to encrypt their messages and talk freely. (antman in the quantum realm might be able to tresspass, no gurantee)

Breacher has access to the Quantum Channel but if he decides to observe the state of the Qubit, there is a 50% chance that he will corrupt the Information being transfered and Alice and Bob will realise about the Tresspasser, This can be futher improved with better Error Correction to prevent false positives, Long bits

## Actual Workings

**The Ipynb contains a better demonstration of Qunatum Circuits**

The Program can be run locally by acquiring the requiremnets in `requirements.txt` and running `python run.py`

^^
The Application currently remains incomplete as of now.

The Encryption and Quantum Inspire and the circuit is useable and works its just the webserver we couldnt finish.
The vision was of a cool website accessible to everyone but it remains incomplete as of now


It was intended to be polished and deployed on heroku or aws but time didnt allow us.





## Team NoSleep

### Tan Jun Liang
though the hackethon, I meet some new friends who is very hard working, and two team mates absent without inform, causing a lot of hard working though there, I am woking on the struture and almost everything of the BB84 protocol. We tried to make it happen on website interface, but sadly no one firmiliar with it, making hard time, with uncomplete project, but atleast we finish the goal.

### Albert Lin
This is my first hackthone, regretly the result is not really ideal since I have too little experience in not only in quantum computing, the relative knowledge about web framework as well, thus we can't complete our project in time. I might work harder on all of these and aim for a better result for all the following hackerthone or coding events. Thanks to my teamates who are hard-working. The co working experience is a really good one for me.


### Jatin Khanna
Indeed my first hackathon as well, first time I've stayed up for more than 24hrs awake and still i'm not feeling sleepy. Had the opportunity to meet and work with great people in MIT iQuHack22. Looking forward for more Hackathons and learning more about Quantum Computing. The Mentors were of great guidance as well , My Favourite part was actually the Gather.town, it was fun meeting people passionate about Science. This shall serve as a springboard for my grand entry in the world of Quantum Mechanics
