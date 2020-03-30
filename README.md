# Chefbot_NCF

This repository is intended for managing conversations that are interfaced through an application like Google Dialogflow. While such applications are mostly useful for modelling single adjacency pairs in the conversation, Chefbot_NCF is developed to enable the modelling of extended conversation plans, such as instructing a cooking recipe (hence the name chefbot). It is inspired on the Natural Conversation Framework (NCF) proposed by Moore and Arar (2019), where the content of the conversation is detached from the act of conversing itself. Furthermore, the Information State Update paradigm (Larsson & Traum, 2000) is adopted to keep track of the conversation and enable dynamic conversation management. The patterns of conversational activities and sequences, as proposed by Moore, can be modelled through conversational moves, with their own preconditions and effects.

## Outline

The basic architecture of most conversational systems consists of a dialog management core, a Natural Language Understanding (NLU) part for interpreting the user's utterances and a Natural Language Generation (NLG) part for formulating the intended response to the user utterance. Optionally, this may be appended with modules for decoding and synthesizing speech, gestures and other non-verbal types of communication. Chefbot_NCF is intended for modelling the dialog mangement and NLG. It should be connected to a dialog application that takes care of the NLU part, and possibly the other modules at the periphery of the architecture.

In its current form, the system is designed for the application of a cooking assistent, in connection with Google Dialogflow. Dialogflow takes care of the NLU, including the recognition of the users intent, as well as Automatic Speech Recognition and Speech Synthesis. This information is communicated through the use of webhooks.

Chefbot_NCF features the following components (in the 'core' directory):

* infostate_tracker.py - *for keeping track of and updating the information state, and for selecting the next conversation moves of the agent*
* natural_language_generator.py - *for selecting the proper agent responses based on the selected conversational moves*
* dialog_manager.py - *for connecting the agent to Google Dialogflow, parsing incoming messages and posting the agent's response*

The utterances of the agent can be written in two files: 

* a file with the standard responses
* a file with the recipes, each recipe consisting of steps and clarifications of steps

Examples of such files are given in the 'example_data' folder. These files are by default used by the dialogue agent. When writing your own content, it is important to use the exact same dictionary keys.

## Installation

A step-by-step guidance to set up the conversational agent:

On Windows, use a Bash terminal (and you may have to use 'python' instead of 'python3 in the terminal').

1. Install the current github repository
  - python3 is required - install if you have not done so already.  
  - In the command line, clone this repository to a local folder of choice: `git clone git@github.com:fkunneman/Chefbot_NCF.git`
  - Install with `python3 setup.py install` in the command line, or add to your pythonpath (`export PYTHONPATH=$PYTHONPATH:<path_to_the repository>/Chefbot_NCF/:`)
  
2. Install software to set up a server tunnel (the current instructions are for setting up ngrok, but other services of choice would also do)
  - Download ngrok from https://ngrok.com/download
  - On Linux or OSX you can unzip ngrok from a terminal using the command `unzip /path/to/ngrok.zip`. On Windows, double click ngrok.zip. 
  - Sign up to ngrok for a free account (https://dashboard.ngrok.com/signup), needed for authorization.
  - Copy your authtoken from https://dashboard.ngrok.com/auth
  - Connect the authtoken in the terminal (on Linux or OSX) or after running ngrok.exe (on Windows from terminal: ngrok.exe http 80), with the following command: `./ngrok authtoken <YOUR_AUTH_TOKEN>`
  - Run the tunnel with the command `./ngrok http 8000`
  
3. Now install Smoothbot, a repository for processing the dialog webhooks, which is based on the Django Web framework 
  - if you haven't installed Django yet, run `pip install django'
  - Like the current repository, smoothbot is a custom repository available through github as https://github.com/fkunneman/smoothbot. Clone the repository to a local folder of choice: `git clone git@github.com:fkunneman/smoothbot.git`
  - In the repository, open the file smoothbot/settings.py, this file needs two adjustments to adopt it to your personal environment and make the repository operational:
    - On line 23, specify the SECRET_KEY - this may be a random sequence of characters (make sure you store the chosen sequence somewhere in a file). 
    - On line 29, specify the allowed host. If you completed step 2 and succesfully started the ngrok tunnel, the url can be found from ngrok session information: check the lines that start with 'Forwarding' and copy the url that ends with 'ngrok.io', but exclude the 'http(s)://' part. On line 29 of the settings.py file, replace 'YOUR TUNNELING HOST' (do not remove the quotes) with this url. 
  - Now you can start the web server. In the command line when located at the root of this repository, run `python3 manage.py runserver`
    - If the terminal returns the error "ModuleNotFoundError: No module named 'Chefbot_NFC.core'", this means that the Chefbot_NFC was not added to your pythonpath. Try to redo the last part of step 1, and confirm in the python shell by using the command 'from Chefbot_NFS.core import dialog_manager'. 
  - Check if it works by retrieving the following URL in your browser: https://<YOUR_NGROK_URL>/df_smoothbot/home/. If the browser displays a page that says 'Hello World!', the web server is properly launched through the tunnelling service. Otherwise, something might be wrong with the tunnelling URL or the web server itself. Carefully check the error message displayed in the browser, and contact f.a.kunneman@vu.nl in case the issues cannot be solved.  

4. When the webserver is set up, you can finally connect this to a Google Dialogflow agent
  - To set up an agent on Dialogflow, first sign up on https://dialogflow.cloud.google.com/
  - Choose 'Create new agent'
  - In the subsequent screen, start by choosing a name for your agent
  - Then give the preferred language. The example agent in this repository is targeted for the Dutch language, so this will have the preference for a first agent.
  - When finished setting up, click the 'Create' button
    - You will now see the general dashboard for creating the agent, with options to create your first intents or entities. 
  - To start off, you are advised to import the example agent from this repository. The agent is stored as a zip-file, and located in 'Chefbot_NFC/example_data/Chef.zip'. 
    - To import the example agent, click on the settings button (the icon next to the name of your agent, at the top left of your dashboard screen)
    - Then click the tab 'export and import'
    - Click 'import from zip'
    - Drop the example agent file 'Chef.zip' in the designated import window
    - Now type 'IMPORT' in the text box
    - Finally click the 'IMPORT' button
    - When the program is done importing, click on the 'Done' button
  - After the import you will see that a number of intents and entities are specified. The only thing you need to do next is connecting the agent to the server you have set up in step 3
    - Click on the 'fulfillment tab'
    - You will see a screen with the headers 'Webhook' and 'Inline Editor'; set the webhook to 'enabled'. 
    - Now enter your server URL: https://<YOUR_NGROK_URL>/df_smoothbot/webhook/ (e.g.: the same URL as the one you tested in the browser at the end of step three, but ending with 'webhook/' instead of home/).
    - At the bottom of the page, click 'Save' and then 'Done'
  - The basic cooking assistant should now be operational. Test by starting a conversation in the right-hand bar of the screen (text box that says 'Try it now'). 
    - Mentioning the word 'Pasta' will start the basic pasta recipe conversation (consisting of only three steps). 
    - Make sure to change the drop-down button that says 'default response' to 'ACTIONS ON GOOGLE'; the agent responses will be presented there.

## Extending the basic agent

* TODO

## References

Larsson, S., & Traum, D. R. (2000). Information state and dialogue management in the TRINDI dialogue move engine toolkit. Natural language engineering, 6(3-4), 323-340.

Moore, R. J., & Arar, R. (2019). Conversational UX Design: A Practitioner's Guide to the Natural Conversation Framework. Morgan & Claypool.

