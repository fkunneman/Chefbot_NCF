# Chefbot_NCF

This repository is intended for managing conversations that are interfaced through an application like Google Dialogflow. While such applications are mostly useful for modelling single adjacency pairs in the conversation, Chefbot_NFS is developed to enable the modelling of extended conversation plans, such as instructing a cooking recipe (hence the name chefbot). It is inspired on the Natural Conversation Framework (NFC) proposed by Moore (2019), where the content of the conversation is detached from the act of conversing itself. Furthermore, the Information State Update paradigm (Larsson, 2000) is adopted to keep track of the conversation and enable dynamic conversation management. The patterns of conversational activities and sequences, as proposed by Moore, can be modelled through conversational moves, with their own preconditions and effects.

## Outline

The basic architecture of most conversational systems consists of a dialog management core, a Natural Language Understanding (NLU) part for interpreting the user's utterances and a Natural Language Generation (NLG) part for formulating the intended response to the user utterance. Optionally, this may be appended with modules for decoding and synthesizing speech, gestures and other non-verbal types of communication. Chefbot_NFC is intended for modelling the dialog mangement and NLG. It should be connected to a dialog application that takes care of the NLU part, and possibly the other modules at the periphery of the architecture. 

In its current form, the system is designed for the application of a cooking assistent, in connection with Google Dialogflow. Dialogflow takes care of the NLU, including the recognition of the users intent, as well as Automatic Speech Recognition and Speech Synthesis. This information is communicated through the use of webhooks. 

Chefbot_NFC features the following components (in the 'core' directory):

* infostate_tracker.py - *for keeping track of and updating the information state, and for selecting the next conversation moves of the agent*
* natural_language_generator.py - *for selecting the proper agent responses based on the selected conversation moves*
* dialog_manager.py - *for connecting the agent to Google Dialogflow, parsing incoming messages and posting the agent's response*

The utterances of the agent can be written in two files: 

* a file with the standard responses
* a file with the recipes, each recipe consisting of steps and clarifications of steps

Examples of such files are given in the 'example_data' folder. These files are by default used by the dialogue agent. When writing your own content, it is important to use the exact same dictionary keys.

## Installation

A step-by-step guidance to set up the conversational agent:

1. Install the current github repository
  - python3 is required - install if you have not done so already.  
  - In the command line, clone this repository to a local folder of choice: `git clone git@github.com:fkunneman/Chefbot_NCF.git`
  - Install with `python3 setup.py install` in the command line, or add to your pythonpath (`export PYTHONPATH=$PYTHONPATH:<path_to_the repository>/Chefbot_NFC/:`) 
2. Install software to set up a server tunnel (current instructions are for setting up ngrok, but other services of choice would also do)
  - Download ngrok from https://ngrok.com/download
  - On Linux or OSX you can unzip ngrok from a terminal using the command `unzip /path/to/ngrok.zip`. On Windows, double click ngrok.zip. 
  - Signup to ngrok for a free account (https://dashboard.ngrok.com/signup), needed for authorization.
  - Copy your authtoken from https://dashboard.ngrok.com/auth
  - Connect the authtoken in the terminal (on Linux or OSX) or after running ngrok.exe (on Windows), with the following command: `./ngrok authtoken <YOUR_AUTH_TOKEN>`
  - Run the tunnel with the command `./ngrok http 80`
3. Now install Smoothbot, a repository for processing GET and POST requests, which is based on the Django Web framework (https://www.djangoproject.com/) 
  - Like the current repository, smoothbot is a custom repository available through github as https://github.com/fkunneman/smoothbot; clone the repository to a local folder of choice: `git clone git@github.com:fkunneman/smoothbot.git`
  - In the repository, open the file smoothbot/settings.py, this file needs two adjustments to adapt it to your personal environment and make the repository operational:
    - On line 23, specify the SECRET_KEY - this may be a random sequence of characters.
    - On line 29, specify the allowed host. If you completed step 2 and succesfully started the ngrok tunnel, the url can be found from ngrok session information: check the lines that starts with 'Forwarding' and copy the url that starts with 'https' and ends with 'ngrok.io'. On line 29 of the settings.py file, replace 'YOUR TUNNELING HOST' with this url. 
  - Now you can start the web server: in the command line when located at the root of this repository, run `python3 manage.py runserver`
4. When the webserver is set-up, you can finally connect this to a Google DialogFlow agent
* Contact f.a.kunneman@vu.nl to acquire access to an example agent.
* The intents, entities and context of the agent should align with those included in chefbot_NCF: the intents align with the user's moves, the entities align with the entities and the context aligns with the output context of each move.

* setup the webhook connection by adding the ngrok URL to Fulfillment - webhook - URL --> https://[SERVER_URL]/df_smoothbot/webhook/
* optionally add a basic authorization to the fulfillment and server
