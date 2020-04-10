#title           : dm_ggz.py
#description     : Class to coördinate the dialog between incoming user utterances from a dialogue interface and the outgoing responses
#author          : Florian Kunneman
#date            : 20200402
#version         : 0.1
#usage           : dm = dm_ggz.DialogManager(); fulfillmentText, suggestions, output_contexts = dm.manage(query)
#notes           : 
#python_version  : 3.7.4  
#==============================================================================


import os
import json
import random

from Chefbot_NCF.core import infostate_tracker
from Chefbot_NCF.chat_ggz import nlg_ggz, ggz_moves

# the content utterered by the dialogue agent is stored in separate files: recipes and general responses
script_dir = os.path.dirname(__file__)
knowledgepath = script_dir + '/ggz_knowledge.json'
responsepath = script_dir + '/ggz_agent.json'

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

    def __init__(self,knowledgefile=knowledgepath,responsefile=responsepath,moveset=ggz_moves):
        self.knowledge = self.load_data(knowledgefile)
        self.default_responses = self.load_data(responsefile)
        self.ISU = infostate_tracker.ISU(self.knowledge,moveset)
        self.NLG = nlg_ggz.NLG(self.knowledge,self.default_responses)
        self.active_answers = {}
        self.active_processed = {}
        self.active_response = {}

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
        return self.active_response, self.ISU.return_suggestions(), self.ISU.return_context()

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
        intent = utterance['intent']
        text = utterance['text']
        entities = utterance['entities']
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
        # if self.active_processed['move'] == 'Kook recept':
        #     self.start_recipe()
        self.ISU.update('U',self.active_processed['move'],self.active_processed['entities'],self.active_processed['text'])
        self.ISU.update_speaker('A')
        self.ISU.next_moves()

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
        self.active_response = self.NLG.formulate_response(self.ISU.return_agent_moves(),self.ISU.return_qud())

    def update_response(self):
        """
        update_response
        =====
        function to update the information state based on the agent's response

        Function calls
        -----
        self.ISU.update_utterance : 
            Update the past conversation with the text to be returned by the agent
        """
        self.ISU.update_utterance(self.active_response)

    ###################################
    ### Helper functions ##############
    ###################################

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