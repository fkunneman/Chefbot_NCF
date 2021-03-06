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

class ConfirmNORecipe(Move):
    """
    ConfirmRecipe
    =====
    Class to model the preconditions and effects of a confirm recipe move
    """

    def __init__(self):
        Move.__init__(self,
            name = 'confirm_no_recipe',
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
        pm = False
        if Move.preconditions_met(self, infostate):
           if ['A', 'confirm_step'] not in infostate['shared']['moves'] and infostate['shared']['entities'][-1]['recept'] ==  '' :
                pm = True
        #print (infostate['shared']['moves'])
        return pm

        #return Move.preconditions_met(self, infostate)

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
        Move.effects(self, infostate)
        # qud
        infostate['shared']['qud'] = '_howto'
        infostate['private']['plan'] = ["1"]
        infostate['plan_wide'] = {}
        infostate['agenda'] = None
        infostate['shared']['beliefs']['task'] = []

class NoNewRecipe(Move):
    """
    ConfirmRecipe
    =====
    Class to model the preconditions and effects of a confirm recipe move
    """

    def __init__(self):
        Move.__init__(self,
            name = 'no_new_recipe',
            prior_moves = ['Kook recept'],
            context = [['recept_confirm',1,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['volgende stap']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state
        No further preconditions should be met other than the presence of a particular prior move: the intent of the user to cook a certain recipe
        """
        pm = False
        if Move.preconditions_met(self, infostate):
            if ['A', 'confirm_step'] not in infostate['shared']['moves'] and infostate['shared']['entities'][-1]['recept'] != '' and infostate['private']['agenda'] != None:
                if len(infostate['shared']['moves']) >= 4:
                    if 'Welke recepten' not in [x[1] for x in infostate['shared']['moves'][-4:]]:
                        pm = True
                else:
                    pm = True
        return pm
        #return Move.preconditions_met(self, infostate)

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
        pm = False
        if Move.preconditions_met(self, infostate):
            if infostate['shared']['entities'][-1]['recept'] != '':
                if len(infostate['shared']['beliefs']['task']) == 0:
                    pm = True
                else:
                    if len(infostate['shared']['moves']) >= 4:
                        if 'Welke recepten' in [x[1] for x in infostate['shared']['moves'][-4:]]:
                            pm = True
                    regex = '(' + '|'.join('instruct_step') + ')'
                    if re.search(regex,infostate['shared']['moves'][-1][1]):
                        if len(infostate['private']['plan_wide']) == 1:
                            pm = True
                    else:
                        if len(infostate['private']['plan_wide']) == 0:
                            pm = True 
        return pm
        
        # return Move.preconditions_met(self, infostate)

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
            if step == "preliminaries":
                infostate['private']['preliminaries'] = sorted([k for k in recipedict[step].keys() if recipedict[step][k]])
            elif step == "Recipe_steps":
                infostate['private']['plan_wide'] = [k for k in recipedict[step].keys() if recipedict[step][k]]
                infostate['private']['explanations'] = recipedict[step]

class OtherRecipe(Move):
    """
    ClarifyQuantity
    =====
    Class to model the preconditions and effects of the move to clarify the quantity of a step
    """

    def __init__(self):
        Move.__init__(self,
            name = 'other_recipe',
            prior_moves = ['ander recept'],
            context = [['recept_confirm',1,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = []
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there is knowledge of the quantity of the ingredients in the current steps
        """
        return Move.preconditions_met(self, infostate)

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effect:
            - the quantity clarification is added to the shared questions under discussion
        """
        Move.effects(self, infostate)
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
            prior_moves = ['Recept continueerder'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_quantity',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_skill',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['volgende stap','vorige stap','hoe','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there are still steps to explain
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if len(infostate['private']['plan_wide']) > 1:
                pm = True
            else:
                pm = False
            if 'determination' in list(infostate['private']['preliminaries']):
                pm = False
            else:
                pm = True
        return pm


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
        if 'cooking_utensils' in list(infostate['private']['preliminaries']): #get first recipe step
            del(infostate['private']['preliminaries'][0])
        else:
            infostate['shared']['beliefs']['done'].append(infostate['private']['plan_wide'].pop(0))
            print(infostate['private']['plan_wide'])

class InstructLastStep(Move):
    """
    InstructStep
    =====
    Class to model the preconditions and effects of the move to instruct a step
    """

    def __init__(self):
        Move.__init__(self,
            name = 'instruct_last_step',
            prior_moves = ['Vorige stap'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_quantity',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_skill',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['volgende stap','vorige stap','hoe','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there are still steps to explain
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if not '1' in infostate['private']['plan_wide'] and len(infostate['private']['preliminaries']) == 0:
                pm = True
        return pm

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
        current_step = min([int(x) for x in infostate['private']['plan_wide']])
        previous_step = str(current_step - 1)
        infostate['private']['plan_wide'].insert(0,previous_step)

class InstructLastStepFallback(Move):
    """
    InstructStep
    =====
    Class to model the preconditions and effects of the move to instruct a step
    """

    def __init__(self):
        Move.__init__(self,
            name = 'instruct_last_step_fallback',
            prior_moves = ['Vorige stap'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_quantity',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_skill',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['volgende stap','vorige stap','hoe','hoeveel','waarom','kun je dat nog een keer herhalen','wat bedoel je']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        In addition to the specified prior moves, the precondition should be met that there are still steps to explain
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if '1' in infostate['private']['plan_wide']:
                pm = True
        return pm

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
            if infostate['private']['explanations'][infostate['private']['plan_wide'][0]]['txt_howmuch']:
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
            if not infostate['private']['explanations'][infostate['private']['plan_wide'][0]]['txt_howmuch']:
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
            if infostate['private']['explanations'][infostate['private']['plan_wide'][0]]['txt_detail']:
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
            suggestions = ['volgende stap','duidelijk','dankje']
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
            if infostate['private']['explanations'][infostate['private']['plan_wide'][0]]['txt_howto']:
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

class ClarifyCookingTechniquesExplain(Move):
    """
    ClarifyExplain
    =====
    Class to model the preconditions and effects of the move to explain how a step is conducted
    """
    def __init__(self):
        Move.__init__(self,
            name = 'clarify_cooking_techniques_explain',
            prior_moves = ['Recept howto'],
            context = [['recept_toelichting',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['volgende stap','duidelijk','dankje', 'ander recept']
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
            if 'determination' in infostate['private']['preliminaries']:
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
            if not infostate['private']['explanations'][infostate['private']['plan_wide'][0]]['txt_howto']:
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
            if infostate['private']['explanations'][infostate['private']['plan_wide'][0]]['txt_motivate']:
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

class ClarifyMotivateFallback(Move):
    """
    ClarifyMotivate
    =====
    Class to model the preconditions and effects of the move to motivate why a step is important
    """

    def __init__(self):
        Move.__init__(self,
            name = 'clarify_step_motivate_fallback',
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
            if not infostate['private']['explanations'][infostate['private']['plan_wide'][0]]['txt_motivate']:
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
            prior_moves = ['instruct_step','Recept continueerder'],
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
        pm = False
        if Move.preconditions_met(self,infostate):
            regex = '(' + '|'.join('instruct_step') + ')'
            if re.search(regex,infostate['shared']['moves'][-1][1]):
                if len(infostate['private']['plan_wide']) == 1:
                    pm = True
            else:
                if len(infostate['private']['plan_wide']) == 0:
                    pm = True 
        return pm

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

class SelectRecipe(Move):
    """
    SelectRecipe
    =====
    Class to model the preconditions and effects of a select recipe move
    """

    def __init__(self):
        Move.__init__(self,
            name = 'select_recipe',
            prior_moves = ['Welke recepten'],
            context = [],
            suggestions = ['pasta', 'pannenkoeken', 'noedels', 'sate', 'ovenschotel']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state
        No further preconditions should be met other than the presence of a particular prior move: the intent of the user to ask for recipe options
        """
        #print("Prior moves of SelectRecipe:", self.prior_moves)
        return Move.preconditions_met(self,infostate)

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state
        """
        Move.effects(self,infostate)

class CookingUtensilsList(Move):
    def __init__(self):
        Move.__init__(self,
            name= 'cooking_utensils_list',
            prior_moves= ['Recept continueerder'],
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_cooking_utensils',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions= ['volgende', 'duidelijk', 'dankje']
        )
    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state
        In addition to the specified prior moves, the precondition should be met that there is knowledge of the quantity of the ingredients in the current steps
        """

        pm = False
        if Move.preconditions_met(self, infostate):
            if len(infostate['private']['preliminaries']) == 2:
                pm = True
            else:
                pm = False
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
        del(infostate['private']['preliminaries'][1])


class IngredientStep(Move):
    """
    IngredientStep
    =====
    Class to model the preconditions and effects of the move to show ingredients in a step
    """

    def __init__(self):
        Move.__init__(self,
            name = 'ingredient_steps',
            prior_moves = ['Recept continueerder'],   #Recept continueerder is intent,   confirm_recipe is agent move
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
        # pm = False
        # if Move.preconditions_met(self,infostate):
        #     if 'ingredients' in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
        #         pm = True
        # return pm
        pm = False
        if Move.preconditions_met(self, infostate):
            if len(infostate['private']['preliminaries']) == 3:
                pm = True
            else:
                pm = False
        return pm

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
        del (infostate['private']['preliminaries'][1])

class DeterminationStep(Move):
    def __init__(self):
        Move.__init__(self,
            name = 'determination_step',
            prior_moves = ['confirm_recipe'],   #Recept continueerder is intent,   confirm_recipe is agent move
            context = [['recept_stappen',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_quantity',5,{'no-input': 0.0, 'no-match': 0.0}],['recept_skill',5,{'no-input': 0.0, 'no-match': 0.0}]],
            suggestions = ['volgende','hoe']
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state
        In addition to the specified prior moves, the precondition should be met that there are still steps to explain
        """
        # pm = False
        # if Move.preconditions_met(self,infostate):
        #     if 'ingredients' in infostate['private']['plan_wide'][infostate['private']['plan'][0]]:
        #         pm = True
        # return pm
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
