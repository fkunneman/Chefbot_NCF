#title           : infostate_tracker.py
#description     : Class to keep track and update the information state guiding a conversation
#author          : Florian Kunneman
#date            : 20200316
#version         : 0.1
#usage           : ISU = infostate_tracker.ISU(recipes); ISU.update(speaker,move,entities,text); ISU.next_moves(); ISU.return_agent_moves(); 
#notes           : 
#python_version  : 3.7.4  
#==============================================================================

import inspect

class ISU:
    """
    ISU
    =====
    Class to keep track and update the information state guiding a conversation

    Parameters
    -----
    knowledge : dict
        The knowledge of the agent (e.g.: the set of recipes it can instruct)

    Attributes
    -----
    self.knowledge : dict
        The knowledge base of the agent
    self.infostate : dict
        The information state, inspired on Larsson and Traum (2000), with the following components :
            * 'private' - the private information state of the agent, with the planned steps at its core
                * 'agenda' - the main agenda of the agent, the higher-level aim(s) like a recipe to instruct
                * 'plan' - the more detailed conversation plan of the agent, like the recipe steps that are yet to be instructed
                * 'plan_wide' - the side-directions that the agent can take per step, such as the quantity of an ingredient per step
            * 'shared' - the shared information state, with aspects of the conversation that the agent and user can both be aware of
                * 'beliefs' - the shared beliefs, like the current task that is pursued and the steps that have been completed
                * 'qud' - the question under discussion, if any
                * 'activity' - the current activity in the conversation (currently not being used or updated)
                * 'converstaion' - the conversation to this point, consisting of the utterances of the agent and user in sequence
                * 'moves' - the moves of the agent and user in sequence
                * 'entities' - the entities mentioned by the user in the conversation
                * 'context' - the active context attached by the agent to an utterance
                * 'suggestions' - the active suggestions attached by the agent to an utterance
                * 'ls' - the last speaker
    self.moves : list
        all move objects that the agent can select from 
    """

    def __init__(self,knowledge,moveset):
        self.knowledge = knowledge
        self.infostate = {
            'private': {
                'agenda':None,
                'plan':[],
                'plan_wide':[],
                'explanations': {},
                'preliminaries':{}
                },
            'shared': {
                'beliefs' : {'done':[], 'task':[]},
                'qud' : None,
                'activity' : None,
                'conversation' : [],
                'moves' : [],
                'entities' : [],
                'context' : [],
                'suggestions' : [],
                'ls' : 'A'
                }
            }
        self.moves = self.set_moves(moveset)


    ###################################
    ### move functions ################
    ###################################

    def set_moves(self,moveset):
        """
        set_moves
        =====
        function to return a selection of available move classes
        the agent will select from these moves after every updated user utterance
        when a new move class is made, add to the returned list in this function

        Returns
        -----
        list of all move objects
        """
        moves = []
        for move in inspect.getmembers(moveset):
            if not move[0][:2] == '__':
                if not move[0] == 'Move' and move[0][0].isupper():
                    print(move[0])
                    move_obj = move[1]()
                    moves.append(move_obj)
        return moves 

    def next_moves(self):
        """
        next_moves
        =====
        function to select the next agent moves from the available moves, based on the updated user utterance
        this function will append moves until none are meeting their preconditions, and subsequently apply the moves' effects

        Function calls
        -----
        self.next_move :
            deciding on the next agent move (the first that complies with its preconditions)
        """
        while True:
            move_obj = self.next_move()
            if not move_obj: break
            move_obj.effects(self.infostate,self.knowledge)
            print('effects after move',move_obj.name,self.infostate)

    def next_move(self):
        """
        next_move
        =====
        function to select the next agent move from the available moves, based on the updated information state
        for each of the known move classes, their preconditions are compared to the information state and knowledge
        if the preconditions are met, the effects of the move (e.g.: changes to the information state) are applied 

        Returns
        -----
        move : the first move in the list for which the preconditions are met
        OR
        False : if none of the moves have their preconditions met 
        """
        for move in self.moves:
            print('Checking move',move.name)
            if move.preconditions_met(self.infostate,self.knowledge):
                return move
        return False

    ###################################
    ### infostate updates #############
    ###################################

    def update(self,speaker,move,entities,text):
        """
        update
        =====
        function to update the fluid components of the information state - the last speaker, utterance, entities and move

        Parameters
        -----
        speaker : str
            the last speaker, either 'U' (user) or 'A' (agent)
        move : str
            the name of the last move, either agent move or user intent
        entities : list
            the entities mentioned in the last utterance, like the name of a recipe, cooking utensil or ingredient
        text : str
            the text of the last utterance

        Function calls
        -----
        self.update_speaker :
            updating the 'ls' field in the information state based on the speaker that was given as an attribute
        self.update_move : 
            adding the latest move to the shared 'moves' field in the information state
        self.update_entities :
            adding the latest mentioned entities to the shared 'entities' field in the information state
        self.update_utterance :
            adding the text of the latest utterance to the shared 'conversation' field in the information state 
        """
        self.update_speaker(speaker)
        self.update_move(move)
        self.update_entities(entities)
        self.update_utterance(text)

    def clear(self):
        """
        clear
        =====
        function to empty the information state, typically done when a new recipe is instructed
        note that a previous information state is not stored anywhere, should be implemented in a subsequent version of this code

        Transforms
        -----
        self.infostate : dict
            the information state is reset to the version it had when initializing the ISU class
        """
        self.infostate = {
            'private': {
                'agenda':None,
                'plan':[],
                'plan_wide':[],
                'explanations': {},
                'preliminaries':{}
                },
            'shared': {
                'beliefs' : {'done':[], 'task':[]},
                'qud' : None,
                'activity' : None,
                'conversation' : [],
                'moves' : [],
                'entities' : [],
                'context' : [],
                'suggestions' : [],
                'ls' : 'A'
                }
            }

    def update_speaker(self,speaker):
        """
        update_speaker
        =====
        function to update the 'ls' field in the information state based

        Attributes
        -----
        speaker : str
            the last speaker to set, either 'U' (user) or 'A' (agent)

        Transforms
        -----
        self.infostate : dict
            the shared 'ls' field in the information state is set to the last speaker
        """
        self.infostate['shared']['ls'] = speaker

    def update_move(self,move):
        """
        update_move
        =====
        function to add the latest move to the shared 'moves' field in the information state

        Attributes
        -----
        move : str
            the name of the last move, either agent move or user intent

        Transforms
        -----
        self.infostate : dict
           adding the given move to the shared 'moves' field in the information state
        """
        self.infostate['shared']['moves'].append([self.infostate['shared']['ls'],move])

    def update_entities(self,entities):
        """
        update_entities
        =====
        function to add the latest mentioned entities to the shared 'entities' field in the information state

        Attributes
        -----
        entities : list
            the entities mentioned in the last utterance, like the name of a recipe, cooking utensil or ingredient

        Transforms
        -----
        self.infostate : dict
           adding the latest mentioned entities to the shared 'entities' field in the information state
        """
        self.infostate['shared']['entities'].append(entities)

    def update_utterance(self,text):
        """
        update_utterance
        =====
        function to add the text of the latest utterance to the shared 'conversation' field in the information state 

        Attributes
        -----
        text : str
            the text of the last utterance

        Transforms
        -----
        self.infostate : dict
           adding the text of the latest utterance to the shared 'conversation' field in the information state 
        """
        self.infostate['shared']['conversation'].append(text)


    ###################################
    ### Retrieve infostate fields #####
    ###################################

    def return_context(self):
        """
        return_context
        =====
        function to return the context values of the shared infostate 

        Transforms
        -----
        self.infostate : dict
            given the changing nature of the context, the shared context value of the infostate is reset to an empty list

        Returns
        -----
        context : list
           list with context values to post to the reader along with the agent utterance
        """
        context = self.infostate['shared']['context']
        self.infostate['shared']['context'] = []
        return context

    def return_suggestions(self):
        """
        return_context
        =====
        function to return the suggestion values of the shared infostate 

        Transforms
        -----
        self.infostate : dict
            given the changing nature of the suggestions, the shared suggestions value of the infostate is reset to an empty list

        Returns
        -----
        suggestions : list
           list with suggestions to post to the reader along with the agent utterance
        """
        suggestions = self.infostate['shared']['suggestions']
        self.infostate['shared']['suggestions'] = []
        return suggestions

    def return_agent_moves(self):
        """
        return_agent_moves
        =====
        function to return the agent moves from the shared infostate 

        Returns
        -----
        agent_moves : list
           list with the names of the current agent's moves
        """
        last_user_occurence=len(self.infostate['shared']['moves'])-[x[0] for x in self.infostate['shared']['moves']][::-1].index('U')
        agent_moves = [x[1] for x in self.infostate['shared']['moves'][last_user_occurence:]]
        return agent_moves

    def return_current_step(self):
        """
        return_current_step
        =====
        function to return the current step in a recipe that is or will be instructed by the agent

        Returns
        -----
        current_step : str
           the index of the current step, which is the first entry in the plan
        """
        try:
            current_step = self.infostate['private']['plan_wide'][0]
        except:
            current_step = False
            print('return current step, step not found')
        return current_step

    def return_qud(self):
        """
        return_qud
        =====
        function to return the current question under discussion

        Returns
        -----
        qud : str
           the question under discussion
        """
        qud = self.infostate['shared']['qud'][-1]
        return qud
