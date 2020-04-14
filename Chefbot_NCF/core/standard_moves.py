#title           : standard_moves.py
#description     : Classes to model conversation moves, with their own preconditions and effects to the information state
#author          : Florian Kunneman
#date            : 20200330
#version         : 0.1
#usage           : 
#notes           : 
#python_version  : >= 3.7.4 
#==============================================================================

import re

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
        regex = '(' + '|'.join(self.prior_moves) + ')'
        if re.search(regex,infostate['shared']['moves'][-1][1]):
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
        