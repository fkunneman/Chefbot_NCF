#title           : nlg_ggz.py
#description     : class to compose the agent's utterances from given answers and responses based on a selection of moves
#author          : Florian Kunneman
#date            : 20200402
#version         : 0.1
#usage           : NLG = nlg_ggz.NLG(responsedict); NLG.formulate_response(agent_moves,current_step
#notes           : 
#python_version  : 3.7.4  
#==============================================================================

import random

class NLG:
    """
    NLG
    =====
    Class to compose the agent's utterances from given steps and responses based on a selection of moves

    Parameters
    -----
    default_responses : dict
        dictionary with written responses as values to triggers as keys

    Attributes
    -----
    self.response : list
        the active response
    self.qa : dict
        dictionary that connects answers to intents
    self.responses : dict
        the written responses to draw from
    self.move_response : dict
        dictionary that links agent moves to functions in this class that collect the proper utterance
        add new moves / responses to this dictionary
    """

    def __init__(self,knowledge,default_responses):
        self.response = []
        self.knowledge = knowledge
        self.default_responses = default_responses
        self.move_response = {
            'answer' : self.answer_inquiry,
            'confirm_pre-inquiry' : self.confirm_preinquiry,
            'disconfirm_pre-inquiry' : self.disconfirm_preinquiry
        }

    def formulate_response(self,moves,qud):
        print('NLG moves',moves)
        print('NLG qud',qud)
        self.update_qud(qud)
        for move in moves:
            self.move_response[move]()
        response_out = ' '.join(self.response).replace('[topic]',qud['entity']).replace('[topics_known]',self.knowledge['known_topics'])
        self.reset_response()
        return response_out

    def reset_response(self):
        self.response = []

    def update_qud(self,qud):
        self.inquiry = qud

    ###################################
    ### Response functions ############
    ###################################

    def answer_inquiry(self):
        """
        answer_inquiry
        =====
        function to retrieve the proper response for the move to answer an inquiry

        Transforms
        -----
        self.response : 
            adds the answer to the active response
        """
        self.response.append(self.knowledge['answers'][self.inquiry]['answer_standard'])

    def confirm_preinquiry(self):
        """
        confirm_preinquiry
        =====
        function to retrieve the proper response for the move to confirm a pre-inquiry

        Transforms
        -----
        self.response : 
            adds the confirmation to the active response
        """
        self.response.append(random.choice(self.default_responses["Confirm Pre-inquiry"]))
