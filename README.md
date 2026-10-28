## I am in no way associated with or sponsored by Kahoot!

## This is a program that I created to try to replicate the popular online quiz game platform Kahoot!
Currently, it has no GUI and uses the terminal to display output and take input, however I am still actively developing the project and hope to get (at least a basic) GUI working soon.\
I am slowly converting projects to use classes for an easier switch between console based and some more GUI action

## What are the different files?
### serverSQL.py
The program running on the device that hosts the quiz.<br>
It shows connection details and the players connect to it.<br>
It displays the questions and answers and the players select one on their devices.<br>
Any arguments passed to the client must be the same as the arguments passed to the server.

### ClientSQL.py
The program that runs on the players devices.<br>
They put in their answers using this script for each question displayed on the host's device.<br>
Any arguments passed to the server must be the same as the arguments passed to the client.<br>

### singlePlayerSQL.py
A program that allows one person to play the quiz on their local device by themselves.

### packCreatorSQL.py
Allows a user to create a question pack file which can then be handed to serverSQL.py or singlePlayerSQL.py to be played as a quiz.

## How to use?
You need AT LEAST 2 devices for multiplayer. One device to be the host and one to be a player (just like Kahoot! the host cannot play the quiz on the same device).<br>
When running the program it uses IPv4 and TCP (and UTF-8 encoding) by default. However, these can be changed by passing arguments to the program at runtime.

## Parsing Arguments
### Only clientSQL.py and serverSQL.py accept arguments
### The arguments passed to clientSQL.py and serverSQL.py MUST BE THE SAME
These arguments are for defining how the computers communicate with each other.
Arguments are OPTIONAL. If you do not pass any arguments, the default values will be used.<br>
Arguments:<br>
"--addrFamily" The method of communication (default=AF_INET)<br>
"--sockKind" The protocol for data transfer (default=SOCK_STREAM)<br>
"--enc" The encoding for data sent (default=utf-8)<br>
Usually, the default values are fine.

### Currently, I have only tested with the default values, so expect bugs if you pass different arguments