#title           : infostate_tracker.py
#description     : Class to keep track and update the information state guiding a conversation
#author          : Florian Kunneman
#date            : 20200316
#version         : 0.1
#usage           : ISU = infostate_tracker.ISU(recipes); ISU.update(speaker,move,entities,text); ISU.next_moves(); ISU.return_agent_moves(); 
#notes           : 
#python_version  : 3.7.4  
#==============================================================================

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

    def __init__(self,knowledge):
        self.knowledge = knowledge
        self.infostate = {
            'private': {
                'agenda':None,
                'plan':[],
                'plan_wide':{}
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
        self.moves = self.set_moves()

    ###################################
    ### move functions ################
    ###################################

    def set_moves(self):
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
        confirm_recipe = ConfirmRecipe()
        instruct_step = InstructStep()
        clarify_quantity = ClarifyQuantity()
        clarify_step_quantity_fallback = ClarifyQuantityFallback()
        clarify_repeat = ClarifyRepeat()
        clarify_elicit = ClarifyElicit()
        clarify_explain = ClarifyExplain()
        clarify_step_explain_fallback = ClarifyExplainFallback()
        clarify_motivate = ClarifyMotivate()
        close_clarification_understood = CloseClarificationUnderstood()
        close_clarification_gratitude = CloseClarificationGratitude()
        close_clarification_acknowledged = CloseClarificationAcknowledged()
        close_recipe = CloseRecipe()
        close_activity = CloseActivity()

        return [
            confirm_recipe,
            instruct_step,
            clarify_quantity,
            clarify_step_quantity_fallback,
            clarify_repeat,
            clarify_explain,
            clarify_step_explain_fallback,
            clarify_motivate,
            clarify_elicit,
            close_clarification_understood,
            close_clarification_gratitude,
            close_clarification_acknowledged,
            close_recipe,
            close_activity
        ]

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
                'plan_wide':{}
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
        current_step = self.infostate['private']['plan'][0]
        return current_step


###################################
### moves #########################
###################################


class Move:
    """
    Move
    =====
    Abstract move class to model the preconditions and effects of a conversation move

    Parameters
    -----
    name : str
        the name of the move
    prior_moves : list
        the names of the moves that could precede the current move
    context : list
        the contexts that are attached to the move, as part of its effects
    suggestions : list
        the suggestions that are attached to the move, as part of its effects

    Attributes
    -----
    self.name : str
        the name of the move
    self.prior_moves : list
        the names of the moves that could precede the current move, as part if its preconditions
        Note: these names could apply to user intents or to agent moves that were selected
    self.context : list
        the contexts that are attached to the move, as part of its effects
    self.suggestions : list
        the suggestions that are attached to the move, as part of its effects
    """

    def __init__(self,name,prior_moves,context,suggestions):
        self.name = name
        self.prior_moves = prior_moves
        self.context = context
        self.suggestions = suggestions

    def preconditions_met(self,infostate):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        Parameters
        -----
        infostate : dict
            the current information state

        Returns
        -----
        Boolean : 
            True if the most basic preconditions, a match between the last move and the required prior moves, is met, False otherwise
        """
        if infostate['shared']['moves'][-1][1] in self.prior_moves: # first precondition
            return True
        else:
            return False

    def effects(self,infostate):
        """
        effects
        =====
        Function to apply the most basic move effects to the information state

        Parameters
        -----
        infostate : dict
            the current information state

        Transforms
        -----
        infostate : dict
            the name, context and suggestions of the move are added to the shared information state
        """
        infostate['shared']['moves'].append(['A',self.name])
        infostate['shared']['context'].extend(self.context),
        infostate['shared']['suggestions'].extend(self.suggestions)


class ConfirmRecipe(Move):
    """
    ConfirmRecipe
    =====
    Class to model the preconditions and effects of a confirm recipe move
    """

    def __init__(self):
        Move.__init__(self,
            name = 'confirm_recipe',
            prior_moves = ['Kook recept'],
            context = [['recept_confirm',1,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['ander recept']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        No further preconditions should be met other than the presence of a particular prior move: the intent of the user to cook a certain recipe
        """
        return Move.preconditions_met(self,infostate)

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effects:
            - the agenda will be set as the instruction of the recipe 
            - the name of the recipe and the fact that it is instructed is added to the shared beliefs
            - the recipe is loaded from the knowledge base and the plan and plan_wide are filled accordingly
        """
        Move.effects(self,infostate)
        recipe_name = infostate['shared']['entities'][-1]['recept']
        infostate['private']['agenda'] = recipe_name
        infostate['shared']['beliefs']['task'] = [recipe_name]
        infostate['private']['plan'] = list(knowledge['Recipe'][recipe_name].keys())
        recipedict = knowledge['Recipe'][recipe_name]
        for step in infostate['private']['plan']:
            infostate['private']['plan_wide'][step] = [k for k in recipedict[step].keys() if recipedict[step][k]] 

class InstructStep(Move):
    """
    InstructStep
    =====
    Class to model the preconditions and effects of the move to instruct a step
    """

    def __init__(self):
        Move.__init__(self,
            name = 'instruct_step',
            prior_moves = ['Recept continueerder','confirm_recipe'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_quantity',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_skill',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['volgende','hoe','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there are still steps to explain
        """
        if Move.preconditions_met(self,infostate):
            if len(infostate['private']['plan']) > 1:
                return True
            else:
                return False

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effects:
            - the last step will be removed from the plan
            - the last step will be signified as 'done' in the shared beliefs 
        """
        Move.effects(self,infostate)
        if not 'recept_confirm' in [x[0] for x in infostate['shared']['context']]: 
            infostate['shared']['beliefs']['done'].append(infostate['private']['plan'].pop(0))


class ClarifyQuantity(Move):
    """
    ClarifyQuantity
    =====
    Class to model the preconditions and effects of the move to clarify the quantity of a step
    """

    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_quantity',
            prior_moves = ['Recept howmuch'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','duidelijk','dankje']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is knowledge of the quantity of the ingredients in the current steps
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if 'txt_howmuch' in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
                pm = True
        return pm

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the quantity clarification is added to the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = infostate['private']['plan'][0] + '_howmuch'

class ClarifyQuantityFallback(Move):
    """
    ClarifyQuantityFallback
    =====
    Class to model the preconditions and effects of the move to fallback to a general response when no proper quantity specification of a step is known
    """

    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_quantity_fallback',
            prior_moves = ['Recept howmuch'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','duidelijk','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is no knowledge of the quantity of the ingredients in the current step
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if 'txt_howmuch' not in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
                pm = True
        return pm

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the quantity clarification is added to the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = infostate['private']['plan'][0] + '_howmuch'

class ClarifyRepeat(Move):
    """
    ClarifyRepeat
    =====
    Class to model the preconditions and effects of the move to repeat a step
    """

    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_repeat',
            prior_moves = ['Recept repeat'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','duidelijk','dankje']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        No further preconditions should be met other than the presence of a particular prior move: the intent of the user to hear the instruction step again
        """
        return Move.preconditions_met(self,infostate)

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the repeat clarification is added to the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = infostate['private']['plan'][0] + '_repeat'


class ClarifyElicit(Move):
    """
    ClarifyElicit
    =====
    Class to model the preconditions and effects of the move to explain a step in more detail
    """
    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_elicit',
            prior_moves = ['Recept elicit'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','duidelijk','dankje']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is knowledge of a detailed account of the current step
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if 'txt_detail' in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
                pm = True
        return pm

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the elicit clarification is added to the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = infostate['private']['plan'][0] + '_elicit'


class ClarifyExplain(Move):
    """
    ClarifyExplain
    =====
    Class to model the preconditions and effects of the move to explain how a step is conducted
    """
    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_explain',
            prior_moves = ['Recept howto'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','duidelijk','dankje']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is knowledge of the proper way to conduct the current step
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if 'txt_howto' in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
                pm = True
        return pm

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the explain clarification is added to the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = infostate['private']['plan'][0] + '_howto'


class ClarifyExplainFallback(Move):
    """
    ClarifyEplainFallback
    =====
    Class to model the preconditions and effects of the move to fallback to a general response when no proper explaination of a step is known
    """

    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_explain_fallback',
            prior_moves = ['Recept howto'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','duidelijk','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is no knowledge of the proper way to conduct the current step
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if 'txt_howto' not in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
                pm = True
        return pm

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the explain clarification is added to the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = infostate['private']['plan'][0] + '_howto'


class ClarifyMotivate(Move):
    """
    ClarifyMotivate
    =====
    Class to model the preconditions and effects of the move to motivate why a step is important
    """

    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_motivate',
            prior_moves = ['Recept motivate'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','duidelijk','dankje']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is knowledge of the reason why to conduct the current step
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if 'txt_motivate' in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
                pm = True
        return pm

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the motivate clarification is added to the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = infostate['private']['plan'][0] + '_motivate'

class CloseClarificationGratitude(Move):
    """
    CloseClarificationGratitude
    =====
    Class to model the preconditions and effects of the move to close a clarification sequence when the user expressed gratitude
    """

    def __init__(self):
        Move.__init__(self,
            name = 'close_clarification_gratitude',
            prior_moves = ['Recept accept repair gratitude'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','hoe','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        No further preconditions should be met other than the presence of a particular prior move: the expression of gratitude by the user after a clarification sequence
        """
        return Move.preconditions_met(self,infostate)

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the clarification is removed from the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = None

class CloseClarificationUnderstood(Move):
    """
    CloseClarificationUnderstood
    =====
    Class to model the preconditions and effects of the move to close a clarification sequence when the user expressed understanding
    """
    def __init__(self):
        Move.__init__(self,
            name = 'close_clarification_understood',
            prior_moves = ['Recept accept repair understood'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','hoe','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        No further preconditions should be met other than the presence of a particular prior move: the expression of understanding by the user after a clarification sequence
        """
        return Move.preconditions_met(self,infostate)

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the clarification is removed from the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = None

class CloseClarificationAcknowledged(Move):
    """
    CloseClarificationAcknowledged
    =====
    Class to model the preconditions and effects of the move to close a clarification sequence when the user expressed neutral acknowledgement
    """
    def __init__(self):
        Move.__init__(self,
            name = 'close_clarification_acknowledged',
            prior_moves = ['Recept accept repair acknowledged'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}]], 
            suggestions = ['volgende','hoe','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        No further preconditions should be met other than the presence of a particular prior move: the expression of neutral acknowledgement by the user after a clarification sequence
        """
        return Move.preconditions_met(self,infostate)

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the clarification is removed from the shared questions under discussion
        """
        Move.effects(self,infostate)
        # qud
        infostate['shared']['qud'] = None

class CloseRecipe(Move):
    """
    CloseRecipe
    =====
    Class to model the preconditions and effects of the move to announce that a recipe has come to an end
    """
    def __init__(self):
        Move.__init__(self,
            name = 'close_recipe',
            prior_moves = ['instruct_step'],
            context = [['recept_klaar',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['dankje','klaar']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is only one step left to explain
        """
        if Move.preconditions_met(self,infostate):
            if len(infostate['private']['plan']) == 1:
                return True
        else:
            return False

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        This moves has no effects other than adding it to the shared conversation information state
        """
        Move.effects(self,infostate)

class CloseActivity(Move):
    """
    CloseActivity
    =====
    Class to model the preconditions and effects of the move to close the conversation activity
    """
    def __init__(self):
        Move.__init__(self,
            name = 'close_activity',
            prior_moves = ['close_clarification_understood','close_clarification_acknowledged','close_clarification_gratitude','Recept continueerder','Sluit recept einde'],
            context = [['recept_klaar',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = []
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is one or no step to explain
        """
        if Move.preconditions_met(self,infostate):
            if len(infostate['private']['plan']) <= 1:
                return True
        else:
            return False

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the plan and agenda are cleared
            - the shared belief of the task at hand is cleared
        """
        Move.effects(self,infostate)
        infostate['plan'] = []
        infostate['plan_wide'] = {}
        infostate['agenda'] = None
        infostate['shared']['beliefs']['task'] = []
