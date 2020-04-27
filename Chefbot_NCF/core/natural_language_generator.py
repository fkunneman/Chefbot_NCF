#title           : natural_language_generator.py
#description     : class to compose the agent's utterances from given steps and responses based on a selection of moves
#author          : Florian Kunneman
#date            : 20200317
#version         : 0.1
#usage           : NLG = natural_language_generator.NLG(responsedict); NLG.formulate_response(agent_moves,current_step
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
    self.recipe : dict
        dictionary with the written steps of a selected recipe
    self.step : str
        the current step of the recipe
    self.responses : dict
        the written responses to draw from
    self.move_response : dict
        dictionary that links agent moves to functions in this class that collect the proper utterance
        add new moves / responses to this dictionary
    """

    def __init__(self,default_responses, recipe_options):
        self.response = []
        self.recipe = None
        self.recipe_options = recipe_options
        self.step = None
        self.responses = default_responses
        self.move_response = {
            'confirm_recipe'                    : self.confirm_recipe,
            'instruct_step'                     : self.instruct_step,
            'close_recipe'                      : self.close_recipe,
            'clarify_step_quantity'             : self.clarify_step_quantity,
            'clarify_step_quantity_fallback'    : self.fallback_quantity,
            'clarify_step_repeat'               : self.clarify_step_repeat,
            'clarify_step_elicit'               : self.clarify_step_elicit,
            'clarify_step_explain'              : self.clarify_step_explain,
            'clarify_step_explain_fallback'     : self.fallback_explain,
            'clarify_step_motivate'             : self.clarify_step_motivate,
            'close_clarification_gratitude'     : self.close_clarification_gratitude,
            'close_clarification_understood'    : self.close_clarification_understood,
            'close_clarification_acknowledged'  : self.close_clarification_acknowledged,
            'close_activity'                    : self.close_activity,
            'select_recipe'                     : self.select_recipe
        }

    def formulate_response(self,moves,index):
        print('NLG moves',moves,index)
        self.update_step(index)
        for move in moves:
            self.move_response[move]()

        # '[recipe]' naar een lijst van recipes?
        print("Recepten in NLG file:", self.recipe_options)
        print(self.recipe['name'])
        recipe_options_string = ', '.join(self.recipe_options)
        print("recipe_options_string:",recipe_options_string)
        #Error replace() argument 2 must be string not dictkeys (self.recipe_options is in de vorm van dictkeys)
        #oplossing?
        response_out = ' '.join(self.response).replace('[recipe]',self.recipe['name']).replace('[step]',self.step).replace('[recipe_options]',recipe_options_string)

        self.reset_response()
        return response_out

    def reset_response(self):
        self.response = []

    def set_recipe(self,recipe):
        self.recipe = recipe

    def set_recipe_options(self,recipe_options):
        print("Set recipe options in NLG boven:", recipe_options)
        self.recipe_options = recipe_options
        print("Set recipe options in NLG onder:", recipe_options)

    def set_responses(self,default_responses):
        self.responses = default_responses

    def update_step(self,index):
        self.step = index


    ###################################
    ### Response functions ############
    ###################################

    def confirm_recipe(self):
        """
        confirm_recipe
        =====
        function to retrieve the proper response for the move to confirm that a recipe has been chose by the user
        the response file might include different variants for variation purposes, which is why a random choice is made

        Transforms
        -----
        self.response : 
            adds the utterance to confirm a recipe to the active response
        """
        self.response.append(random.choice(self.responses['Confirm recipe']['regular']))

    def introduce_step(self):
        """
        introduce_step
        =====
        function to retrieve the proper response for the move to introduce a new recipe step
        the response file might include different variants for variation purposes, which is why a random choice is made
        a different introduction will be voiced in case of the first or last step

        Transforms
        -----
        self.response : 
            adds the utterance to introduce a step of the recipe to the active response
        """
        nrs = self.responses['New recipe step']
        options = nrs['last'] if int(self.step) == int(self.recipe['steps'][-1]) else nrs['first'] if self.step == '1' else nrs['regular'] 
        self.response.append(random.choice(options))

    def instruct_step(self):
        """
        instruct_step
        =====
        function to retrieve the proper response for the move to instruct a recipe step

        Transforms
        -----
        self.response : 
            adds the instruction to the active response
        """
        self.response.append(self.recipe['steps'][self.step]['txt_standard'])

    def clarify_step(self,clarification_type):
        """
        clarify_step
        =====
        abstract function to retrieve the proper response for the move to clarify a recipe step
        this function is the same for multiple types of clarifications (how, why, howmuch, etc.) and is called by these more specific functions

        Parameters
        -----
        clarification_type : list
            specification of the clarification type; a list of length 2 with as first entry the name of the clarification in the response dict,  
                and as second entry the name of the intent for the clarification to access the proper clarification of the recipe step 

        Transforms
        -----
        self.response : 
            adds the introduction to the clarification (if any), and the clarification itself to the active response
        """
        self.response.extend([random.choice(self.responses[clarification_type[1]]['regular']),self.recipe['steps'][self.step][clarification_type[0]]])

    def clarify_fallback(self,clarification_type):
        """
        clarify_fallback
        =====
        abstract function to retrieve the proper response if no proper clarification is known to answer a user request
        this function is the same for the fallback of multiple types of clarifications (how, why, howmuch, etc.) and is called by these more specific functions
        the response file might include different fallback utterances for variation purposes, which is why a random choice is made

        Parameters
        -----
        clarification_type : str
            specification of the clarification type to retrieve the proper fallback

        Transforms
        -----
        self.response : 
            adds the fallback to the clarification to the active response
        """
        self.response.append(random.choice(self.responses[clarification_type]['fallback']))

    def clarify_step_quantity(self):
        """
        clarify_step_quantity
        =====
        function to retrieve the proper response for the move to clarify the quantity of a recipe step

        Function calls
        -----
        self.clarify_step : 
            to retrieve the proper clarification with the specified keys
        """
        self.clarify_step(['txt_howmuch', 'Step quantity'])

    def fallback_quantity(self):
        """
        fallback_quantity
        =====
        function to retrieve the proper response if no proper clarification is known to answer a quantity clarification request by the user

        Function calls
        -----
        self.clarify_fallback : 
            to retrieve the proper fallback with the specified key
        """
        self.clarify_fallback('Explain quantity')

    def clarify_step_repeat(self):
        """
        clarify_step_repeat
        =====
        function to retrieve the proper response for the move to repeat a recipe step

        Function calls
        -----
        self.clarify_step : 
            to retrieve the proper clarification with the specified keys
        """
        self.clarify_step(['txt_standard','Repeat step'])

    def clarify_step_elicit(self):
        """
        clarify_step_elicit
        =====
        function to retrieve the proper response for the move to instruct a recipe step in more detail

        Function calls
        -----
        self.clarify_step_elicit : 
            to retrieve the proper clarification with the specified keys
        """
        self.clarify_step(['txt_detail','Elicit step'])

    def clarify_step_explain(self):
        """
        clarify_step_explain
        =====
        function to retrieve the proper response for the move to clarify the way to execute a recipe step

        Function calls
        -----
        self.clarify_step : 
            to retrieve the proper clarification with the specified keys
        """
        self.clarify_step(['txt_howto', 'Explain step'])

    def fallback_explain(self):
        """
        fallback_explain
        =====
        function to retrieve the proper response if no proper clarification is known to answer a 'howto' clarification request by the user

        Function calls
        -----
        self.clarify_fallback : 
            to retrieve the proper fallback with the specified key
        """
        self.clarify_fallback('Explain step')

    def clarify_step_motivate(self):
        """
        clarify_step_motivate
        =====
        function to retrieve the proper response for the move to explain why recipe step is necessary

        Function calls
        -----
        self.clarify_step : 
            to retrieve the proper clarification with the specified keys
        """
        self.clarify_step(['txt_motivate', 'Motivate step'])

    def close_clarification(self,third_position_intent):
        """
        close_clarification
        =====
        abstract function to close a clarification sequence in a way tuned towards the third position response of the user

        Parameters
        -----
        third_position_intent : str
            specification of the third position response of the user, to retrieve the proper clarification closure
            may have one of the following values: 'gratitude', 'understood', 'acknowledged'

        Transforms
        -----
        self.response : 
            adds the closure of the clarification sequence to the active response
        """
        self.response.append(random.choice(self.responses['Accept repair'][third_position_intent]))

    def close_clarification_gratitude(self):
        """
        close_clarification_gratitude
        =====
        function to retrieve the proper closure of a clarification sequence when the user has expressed gratitude

        Function calls
        -----
        self.close_clarification : 
            to retrieve the proper clarification with the specified key
        """
        self.close_clarification('gratitude')

    def close_clarification_understood(self):
        """
        close_clarification_understood
        =====
        function to retrieve the proper closure of a clarification sequence when the user has expressed understanding

        Function calls
        -----
        self.close_clarification : 
            to retrieve the proper clarification with the specified key
        """
        self.close_clarification('understood')

    def close_clarification_acknowledged(self):
        """
        close_clarification_acknowledged
        =====
        function to retrieve the proper closure of a clarification sequence when the user has expressed neutral acknowledgement

        Function calls
        -----
        self.close_clarification : 
            to retrieve the proper clarification with the specified key
        """
        self.close_clarification('acknowledged')

    def close_recipe(self):
        """
        close_recipe
        =====
        function to retrieve the utterance when the instruction of a recipe has come to an end, typically when the last step has been explained
        the response file might include different variants for variation purposes, which is why a random choice is made

        Transforms
        -----
        self.response : 
            adds the recipe closure to the active response
        """
        self.response.append(random.choice(self.responses['Confirm end recipe']['regular']))

    def close_activity(self):
        """
        close_activity
        =====
        function to retrieve the utterance when the agent is moving towards an ending of the conversation 
        the response file might include different variants for variation purposes, which is why a random choice is made

        Transforms
        -----
        self.response : 
            adds the activity closure to the active response
        """
        self.response.append(random.choice(self.responses['Close activity']['regular']))

    def select_recipe(self):
        """
        select_recipe
        =====
        function to retrieve the proper response for the move to select a recipe from a list of available recipes
        the response file might include different variants for variation purposes, which is why a random choice is made

        Transforms
        -----
        self.response :
            adds the utterance to show options of recipes to the active response
        """
        self.response.append(random.choice(self.responses['Select recipe']['regular']))