#title           : dialog_manager.py
#description     : Class to coördinate the dialog between incoming user utterances from a dialogue interface and the outgoing responses
#author          : Florian Kunneman
#date            : 20200316
#version         : 0.1
#usage           : dm = dialog_manager.DialogManager(); fulfillmentText, suggestions, output_contexts = dm.manage(query)
#notes           : 
#python_version  : 3.7.4  
#==============================================================================


import os
import json
import random

from . import infostate_tracker
from . import natural_language_generator
from . import standard_moves

# the content utterered by the dialogue agent is stored in separate files: recipes and general responses
script_dir = os.path.dirname(__file__)
recipepath = script_dir + '/../example_data/agent_recipes.json'
responsepath = script_dir + '/../example_data/agent_responses.json'

class DialogManager:
    """
    DialogManager
    =====
    Class to coördinate the dialog between incoming user utterances from a dialogue interface and the outgoing responses

    Parameters
    -----
    recipefile : str
        Path to the file that stores the recipes, with steps and explanations.
        The example file with one short recipe is used by default. 
    responsefile : str
        Path to the file that stores the general responses (e.g.: fall-back options, acceptation of gratitude, etc.
        The example file is used by default. 

    Attributes
    -----
    self.recipes : dict
        object that stores all recipes
    self.responses : dict
        object that stores all general responses
    self.ISU : ISU
        Object of class ISU that stores and manages the information state, which guides the conversation
    self.NLG : NLG
        Object of class NLG that composes the agent's utterances from the steps and responses specified in the recipe and responsefile, 
            based on the selected moves
    self.active_recipe : dict
        object that stores the selected recipe by the user, if any
    self.active_processed : dict
        object that stores the current user's utterance, intent and entities
    self.active_response : dict
        object that stores the current agent's response, move and context
    """

    def __init__(self,recipefile=recipepath,responsefile=responsepath,moveset=False):
        self.recipes = self.load_data(recipefile)
        self.recipe_options = self.recipes["Recipe"].keys()
        self.responses = self.load_data(responsefile)
        self.other_recipe_list = []
        self.current_recipe_list = []
        for x in self.recipes['Recipe']:
            self.other_recipe_list.append(x)
        #self.other = random.choice(self.other_recipe_list)


        if not moveset:
            moveset = standard_moves
        self.ISU = infostate_tracker.ISU(self.recipes,moveset)
        self.NLG = natural_language_generator.NLG(self.responses, self.recipe_options)
        self.active_recipe = {}
        self.active_processed = {}
        self.active_response = ''
        self.active_images = False

    ###################################
    ### Main functions ################
    ###################################

    def manage(self,utterance):
        """
        manage
        =====
        Main function of the DialogManager, to process an incoming utterance and return the proper response

        Parameters
        -----
        utterance : dict
            The user's utterance, forwarded from the server webhook. 

        Function calls
        -----
        self.process : 
            parsing the text, intent and entities from the utterance
        self.update_processed :
            communicating with the ISU object to update the information state based on the incoming utterance,
                and selecting the subsequent agent moves
        self.formulate_response :
            communicating with the NLG object to compose the agent's textual response based on the selected moves
        self.update_response :
            communicating with the ISU object to update the information state based on the agent's response

        Returns
        -----
        self.active_response : dict
            The agent's moves and textual response to communicate to the user
        self.ISU.return_suggestions() : list
            The suggested user's response to the agent's utterance, that will be displayed in the chat window
        self.ISU,return_context() : list
            The context that comes with the agent's utterance, to facilitate intent recognition by the dialog service used 
        """
        self.process(utterance)
        self.update_processed()
        self.formulate_response()
        self.update_response()
        active_images_send = self.active_images
        self.active_images = False
        return self.active_response, active_images_send, self.ISU.return_suggestions(), self.ISU.return_context()

    def process(self,utterance):
        """
        process
        =====
        function to parse an incoming utterance

        Parameters
        -----
        utterance : dict
            The user's utterance, forwarded from the server webhook. 

        Returns
        -----
        self.active_processed : dict
            dictionary with the parsed components of the user's utterance, e.g.:
                intent : the intent, as specified in the dialog interface (Google Dialog Flow by default); 
                    the intent is stored as the user's dialog move
                text : the text of the utterance, as decoded by the ASR component of the dialog interface
                entities : the entities in the utterance, if any, as specified in the dialog interface (Google Dialog Flow by default)
        """
        intent = utterance['intent']['displayName']
        text = utterance['queryText']
        entities = utterance['parameters']
        self.active_processed = {'utterance':utterance,'move':intent,'entities':entities,'text':text}

    def update_processed(self):
        """
        update_processed
        =====
        function to update the information state based and select the subsequent agent moves

        Function calls
        -----
        self.start_recipe : 
            Only called when the intent of the user is to start a new recipe
            Sets the active recipe (also for the NLG object), and clears the plan in the information state. 
        self.ISU.update : 
            For updating the information state, registering the last speaker, move, entities and utterance
        self.ISU.update speaker: 
            For updating the speaker back to the agent (needed for the agent move effects) 
        self.ISU.next_moves :
            For deciding on the agent moves based on the user's utterance - 
                selecting one or more moves for which the preconditions are met, and applying their effects
        """
        # if (self.ISU.infostate['shared']['moves'] == [] or self.ISU.infostate['shared']['moves'][-1] == ['A', 'close_activity']):
        #     #print ("JA DIT WERKT")
        #     if self.active_processed['move'] == 'Kook recept' :
        #         if self.active_processed['utterance']['parameters']['recept'] not in self.recipes['Recipe']:
        #             print("DM")
        #         else:
        #             self.start_recipe()
        # if self.active_processed['move'] == 'Recept update':
        #     print("HIER MOET EEN UPDATE STAAN:", self.active_processed['move'], "????????")


        if self.active_processed['move'] == 'ander recept':
            print (self.other_recipe_list)
            self.other = random.choice(self.other_recipe_list)
            self.start_other_recipe()
            self.active_processed['entities']['recept'] = self.other

        self.ISU.update('U',self.active_processed['move'],self.active_processed['entities'],self.active_processed['text'])
        self.ISU.update_speaker('A')
        self.ISU.next_moves()
        if 'confirm_recipe' in self.ISU.return_agent_moves():
            self.start_recipe()

    def formulate_response(self):
        """
        formulate_response
        =====
        function to compose the agent's textual response based on the selected moves

        Function calls
        -----
        self.NLG.formulate_response : 
            communicate with NLG object to formulate a response based on the selected move and current position in the recipe

        Transforms
        -----
        self.active_response :
            update with the textual response as returned by the NLG object
        """
        print('preliminaries status', self.ISU.infostate['private']['preliminaries'])
        self.active_response, self.active_images = self.NLG.formulate_response(self.ISU.return_agent_moves(), self.ISU.return_current_step())

    def update_response(self):
        """
        update_response
        =====
        function to update the information state based on the agent's response

        Function calls
        -----
        self.ISU.update_utterance : x
            Update the past conversation with the text to be returned by the agent
        """
        self.ISU.update_utterance(self.active_response)
    ###################################
    ### Helper functions ##############
    ###################################

    def start_recipe(self):
        """
        start_recipe
        =====
        function to set the active recipe based on the user's intent

        Function calls
        -----
        self.NLG.set_recipe :
            set the active recipe in the NLG object 
        self.ISU.clear : 
            clear the information state (new recipe is seen as new conversation plan)

        Transforms
        -----
        self.active_recipe : dict
            The steps and the name of the active recipe are updated according to the choice of the user
        """
        name = self.active_processed['utterance']['parameters']['recept']
        if self.active_processed['entities']['recept'] in self.other_recipe_list:
            self.other_recipe_list.remove(self.active_processed['entities']['recept'])
        self.active_recipe['Recipe_steps'] = self.recipes['Recipe'][name]['Recipe_steps']
        self.active_recipe['preliminaries'] = self.recipes['Recipe'][name]['preliminaries']
        self.active_recipe['steps'] = self.recipes['Recipe'][name]
        self.active_recipe['name'] = name
        self.NLG.set_recipe(self.active_recipe)
        #self.ISU.clear()


    def start_other_recipe(self):
        """
        start_recipe
        =====
        function to set the active recipe based on the user's intent

        Function calls
        -----
        self.NLG.set_recipe :
            set the active recipe in the NLG object
        self.ISU.clear :
            clear the information state (new recipe is seen as new conversation plan)

        Transforms
        -----
        self.active_recipe : dict
            The steps and the name of the active recipe are updated according to the choice of the user
        """
        #name = self.active_processed['utterance']['parameters']['recept']
        name = self.other
        self.active_recipe['steps'] = self.recipes['Recipe'][name]
        self.active_recipe['name'] = name
        self.NLG.set_recipe(self.active_recipe)
        self.ISU.clear()

    def load_data(self,path):
        """
        load_data
        =====
        function to read a json file and return a dict object

        Parameters
        -----
        path : str
            Path to the json file 

        Returns
        -----
        json_data_formatted : dict
            The parsed json file as a dict object
        """
        with open(path,'r',encoding='utf-8') as file_in:
            json_data = file_in.read().strip()
        json_data_formatted = json.loads(json_data)
        return json_data_formatted
