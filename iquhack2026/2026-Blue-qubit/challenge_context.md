Join our one-of-a-kind quantum hackathon, where you’ll put your quantum computing skills to test and solve Peak Circuit challenges. The competition is open to all experience levels - anyone from quantum enthusiasts to seasoned researchers is welcome.
🆕 Discord

Join our Discord for latest updates ➡️ JOIN DISCORD
📅 Schedule

    Jan 31st 10:20am ET: Problems are released - Hacking begins 🚀

    Feb 1st 10:00am ET: Hackathon ends

🎯 Peaked Circuits Challenge

Participants will receive special quantum circuits (Peaked Circuits) in .qasm format where each circuit sets up a specific quantum state. Hidden within that state is a single bitstring that appears with high probability. 

Your mission is to find this bitstring!
notion image

In the example above, 0110 is the peak bitstring as it has comparatively much higher probability  to be measured than all the other bitstrings. And below you can find the .qasm file that prepared this state:

OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
x q[0];
x q[3];
ry(0.8*pi) q[0];
ry(0.8*pi) q[1];
ry(0.8*pi) q[2];
ry(0.8*pi) q[3];

🌟 Useful Resources

    Simulators: You are welcome to use BlueQubit’s quantum and simulation devices to tackle these circuits. To crack the hardest ones though - you have to get creative and you might need to use other simulation tools as well. 

    Hints: Pay attention to the problem descriptions as they usually contain hints!

    Tutorials: The Peaked Circuits Tutorial on the BlueQubit platform can be very handy on tackling most of the problems! You can actually copy and run this tutorial in the notebook environment explained below.

    Notebooks: You are also welcome to use BlueQubit’s Notebook Environment that has many quantum libraries setup and ready to go! 

🏆 Leaderboard

There are 2 metrics affecting your leaderboard position:

    Problems Solved: Each problem has points, and harder problems have more points. Your score is the sum of the points for the problems you solved.

    Time: The longer it takes you to solve a problem - the more time penalty you accumulate. this means the fastest solutions get ranked higher if the problem scores are the same!

📚 Peaked Circuits in a Nutshell

“Peaked circuits” are pre-constructed quantum circuits with a non-uniform distribution of measurement outcomes. They are designed in a way that one particular bitstring has a higher probability than others, e.g. O(1) as opposed to exponentially small amplitude. 

They were introduced by Scott Aaronson as a way to achieve verifiable quantum advantage. Carefully crafted peaked circuits look like random circuits  - like the one used by Google in their benchmark that would take supercomputers septillion=10²⁵ years to replicate. However, unlike random circuits - peaked circuits are much easier to verify: all you need to do is to run them on a quantum computer and verify you get the correct hidden bitstring!

This quantum hackathon aims to test the skills of quantum researchers and enthusiasts in how well they can use quantum computers and simulators to crack such peaked circuits. 
💬 Frequently Asked Questions
1. Can I participate with a team?

Absolutely! Only make sure to signup and make submissions from a single account. 
2. Do I need prior experience in quantum computing to join this hackathon?

Not really - all you need is to know what a quantum circuit is. Skills in quantum simulations and prior experience with different quantum simulators will definitely go a long way!
3. How long does the Hackathon last?

Our quantum computing hackathon will last 24 hours. 
4. What challenges can I expect in this quantum hackathon?

All problems in our hackathon will be related to peak circuits - you will need to find a way to simulate (or execute) a quantum circuit to find the hidden peak bitstring.
5. How do I prepare for the Hackathon if I’m new to quantum programming?

For beginners or budding enthusiasts, we recommend going through basic tutorials offered by Qiskit or PennyLane. Make sure to get familiar with quantum circuits and how they prepare a quantum state.
6. Can I use real quantum hardware?

Absolutely! You can also use the various simulators available on the BlueQubit platform!
7. How are winners selected?

Winners are chosen based on the highest number of problems they solve correctly in the shortest time. 
