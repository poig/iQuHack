"""This is the Client Side File, Alice here refers to the client and bob is the second person Alice is talking to"""


from random import getrandbits
import qiskit as q
import binascii


KEY_LENGTH = 500
SECURE_LENGTH = 50
QUANTUM_CHANNEL = []
CLASSICAL_CHANNEL = []



def timedec(func):
    def wrap(*args, **kwargs):
        import time
        t = time.time()
        ret = func(*args, **kwargs)
        print(f'Time taken when running {func.__name__}: {time.time() - t}')
        return ret
    return wrap





quantum_backend = q.Aer.get_backend('qasm_simulator')
#call gen key when iniaizing communication with anew person (sending friend request)


@timedec
def friend_req(key_length= KEY_LENGTH):
    limit=30
    while limit > 0:
        # Step 1: Alice's Prepares encoding basis and choose a random btistring
        Alice_bitstring, Alice_bases = start_encoding(key_length+SECURE_LENGTH)
        encoded_qubits = encode(Alice_bitstring, Alice_bases)
        # Step 2: Alice sends the qubits (Through Optical Fibre or...)
        Bob_bases = select_measurement(KEY_LENGTH + SECURE_LENGTH)

        #Step 3: Alice Announces the bases used
        QUANTUM_CHANNEL = encoded_qubits


        #STEP 4: Alice Recives Accepted Key Indicies from Bob
        CLASSICAL_CHANNEL = Alice_bases

        return QUANTUM_CHANNEL, CLASSICAL_CHANNEL


@timedec
def genkey(key_length= KEY_LENGTH):
    limit=30
    while limit > 0:
        # Step 1: Alice's Prepares encoding basis and choose a random btistring
        Alice_bitstring, Alice_bases = start_encoding(key_length+SECURE_LENGTH)
        encoded_qubits = encode(Alice_bitstring, Alice_bases)
        Bob_bases = select_measurement(KEY_LENGTH + SECURE_LENGTH)
        # Step 2: Alice sends the qubits (Through Optical Fibre or...)
        QUANTUM_CHANNEL = encoded_qubits

        #Step 3: Alice Announces the bases used
        CLASSICAL_CHANNEL = Alice_bases


        #STEP 4: Alice Recives Accepted Key Indicies from Bob
        CLASSICAL_CHANNEL = Alice_bases

        Bob_bitstring = measure(Bob_bases, QUANTUM_CHANNEL, quantum_backend)
        agreeing_bases = bob_compare_bases(CLASSICAL_CHANNEL[:SECURE_LENGTH], Bob_bases[:SECURE_LENGTH])
        Alice_secure_check =  construct_key_from_indices(Alice_bitstring[:SECURE_LENGTH], agreeing_bases)
        Bob_secure_check = construct_key_from_indices(Bob_bitstring[:SECURE_LENGTH], agreeing_bases)
        if secure_check(Alice_secure_check,Bob_secure_check):
            CLASSICAL_CHANNEL = Alice_bases
            agreeing_bases = bob_compare_bases(CLASSICAL_CHANNEL, Bob_bases)
            break
    #STEP 4: Alice Recives Accepted Key Indicies from Bob
    if not limit:
        raise Exception('error when generating key')
    return construct_key_from_indices(Alice_bitstring, agreeing_bases)[SECURE_LENGTH:]

@timedec
def secure_check(Alice_secure_check, Bob_secure_check):
    counter=0
    for i in range(len(Alice_secure_check)):
        if Alice_secure_check[i]==Bob_secure_check[i]:
            counter+=1
    if counter/len(Alice_secure_check)>=0.9:
        return True
    return False

@timedec
def encode(alice_bitstring, alice_bases):
    encoded_qubits = []
    for i in range(len(alice_bitstring)):
        # create a brand new quantum circuit called qc. Remember that the qubit will be in state |0> by default
        qc = q.QuantumCircuit(1,1)

        if alice_bases[i] == "0":
            # 0 Means we are encoding in the z basis
            if alice_bitstring[i] == "0":
                # We want to encode a |0> state, as states are intialized
                # in |0> by default we don't need to add anything here
                pass
            
            elif alice_bitstring[i] == "1":
                # We want to encode a |1> state
                # We apply an X gate to generate |1>
                qc.x(0)
                
        elif alice_bases[i] == "1":
            # 1 Means we are encoding in the x basis
            if alice_bitstring[i] == "0":
                # We apply an H gate to generate |+>
                qc.h(0)
            elif alice_bitstring[i] == "1":
                # We apply an X and an H gate to generate |->
                qc.x(0)
                qc.h(0)
            
        # add this quantum circuit to the list of encoded_qubits
        encoded_qubits.append(qc)
        
    return encoded_qubits

@timedec
def select_measurement(length):
    # Similar to before we store the bases that Bob will measure in a list
    bob_bases = ""
    
    for i in range(length):
        # Again we use getrandbits to generate a 0 or 1 randomly
        bob_bases += (str(getrandbits(1)))
        
    # return the list of random bases to measure in
    return bob_bases

@timedec
def measure(bob_bases, encoded_qubits, backend):
    # Perform measurement on the qubits send by Alice
    # selected_measurements: 
    # encoded_qubits: list of QuantumCircuits received from Alice
    # backend: IBMQ backend, either simulation or hardware
    
    # Stores the results of Bob's measurements
    bob_bitstring = ''
    
    for i in range(len(encoded_qubits)):
        qc = encoded_qubits[i]
        
        if bob_bases[i] == "0":
            # 0 means we want to measure in Z basis
            qc.measure(0,0)

        elif bob_bases[i] == "1":
            # 1 means we want to measure in X basis
            qc.h(0)
            qc.measure(0,0)
        
        # Now that the measurements have been added to the circuit, let's run them.
        job = q.execute(qc, backend=backend, shots = 1) # increase shots if running on hardware
        results = job.result()
        counts = results.get_counts()
        measured_bit = max(counts, key=counts.get)

        # Append measured bit to Bob's measured bitstring
        bob_bitstring += measured_bit 
        
    return bob_bitstring

@timedec
def bob_compare_bases(Alices_bases, bobs_bases):
    indices = []
    
    for i in range(len(Alices_bases)):
        if Alices_bases[i] == bobs_bases[i]:
            indices.append(i)
    return indices

@timedec
def start_encoding(key_length):
    #Generating Alice bitstring and bases
    Alice_bitstring = ""
    Alice_bases = ""

    for i in range(key_length):
        Alice_bitstring += str(getrandbits(1))
        Alice_bases += str(getrandbits(1))

    #Encoding 
    encoded_qubits = []
    for i in range(len(Alice_bitstring)):

        qc = q.QuantumCircuit(1,1)

        if Alice_bases[i] == "0":
            if Alice_bitstring[i] == "1":
                qc.x(0)
        
        elif Alice_bases[i] == "1":
            if Alice_bitstring[i] == "0":
                qc.h(0)
            
            elif Alice_bitstring[i] == "1":
                qc.x(0)
                qc.h(0)

        encoded_qubits.append(qc)
    return encoded_qubits, Alice_bases


@timedec
def compare_bob_bases(Alice_bases, bobs_bases):
    indices = []
    for i in range(Alice_bases):
        if Alice_bases[i] == bobs_bases[i]:
            indices.append(i)

    return indices


@timedec
def construct_key_from_indices(bitstring, indices):
    key = ""
    for idx in indices:
        key = key + bitstring[idx]

    return key




@timedec
def compute_indices(Alice_bases):
    """This Function gets called by the Server,
    Function is basically the Classical Channel where alice and bob will figure out the indices"""
    #Generating Bob bitstring and bases
    bob_bases = ""

    for i in range(KEY_LENGTH):
        bob_bases += str(getrandbits(1))    

    
    indices = compare_bob_bases(Alice_bases, bob_bases)

    CLASSICAL_CHANNEL = indices


    return CLASSICAL_CHANNEL
    #Alice and Bob sending their indices 







"""

def send_message(send_to, content):


    key = getfromenv
    if not there:
        key = genkey(KEY_LENGTH)

    encrypted_message = encrypt_message(content, key)

    #send to server (to be implemented) (encrypted_message)


def receive_message():
    #decrypt_message()
    #send toe client
    pass
    #how the fuck wil be recive message

"""


def encrypt_message(unencrypted_string, key):
    bits = bin(int(binascii.hexlify(unencrypted_string.encode('utf_8', 'surrogate')))) #here wrong

    bitstring = bits.zfill(8* ((len(bits)*7 )//8))
    encrypted_string = ""

    for i in range(len(bitstring)):
        encrypted_string += str((int(bitstring[i])^int(key[i])  ))

    return encrypted_string


def decrypt_message(encrypted_bits, key):
    # created the unencrypted string using the key
    unencrypted_bits = ""
    for i in range(len(encrypted_bits)):
        unencrypted_bits += str( (int(encrypted_bits[i])^ int(key[i])) )
    i = int(unencrypted_bits, 2)
    hex_string = '%x' % i
    n = len(hex_string)
    bits = binascii.unhexlify(hex_string.zfill(n + (n & 1)))
    unencrypted_string = bits.decode('utf-8', 'surrogatepass')
    return unencrypted_string







"""


import numpy as np
# Importing standard Qiskit libraries
from qiskit import QuantumCircuit, transpile, Aer, IBMQ
from qiskit import *
from qiskit.tools.jupyter import *
from qiskit.visualization import *
#IBMQ.save_account('MY_TOKEN_NUMBER',overwrite=True)  #save your creds
#provider = IBMQ.load_account()
from quantuminspire.credentials import enable_account


import os

from qiskit import BasicAer, execute
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit

from quantuminspire.credentials import get_authentication
from coreapi.auth import BasicAuthentication
from quantuminspire.qiskit import QI



QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')


authentication = BasicAuthentication("laolianglaoliang@gmail.com", "PJYpXmuQaMmDUvwTh0Bh")
QI.set_authentication(authentication, QI_URL, 'trying')
#qi = QuantumInspireAPI(QI_URL, authentication, 'first trying')
enable_account('901fc459ba65108a4af3e9145481e0fc4527d818')







QUANTUM_CHANNEL.draw('text')
"""
















