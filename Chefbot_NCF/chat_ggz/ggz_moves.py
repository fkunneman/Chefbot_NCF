#title           : standard_moves.py
#description     : Classes to model conversation moves, with their own preconditions and effects to the information state
#author          : Florian Kunneman
#date            : 20200330
#version         : 0.1
#usage           : 
#notes           : 
#python_version  : >= 3.7.4 
#==============================================================================

from Chefbot_NCF.core.standard_moves import Move

###################################
### moves #########################
###################################

class Answer(Move):
    """
    Answer
    =====
    Class to model the preconditions and effects of an answer move
    """

    def __init__(self):
        Move.__init__(self,
            name = 'answer',
            prior_moves = ['inquiry_*'],
            context = [],
            suggestions = []
        )

    def preconditions_met(self,infostate,knowledge):
        """
        preconditions_met
        =====
        Boolean function to return if the preconditions of this move have been met given the current information state

        No further preconditions should be met other than the presence of a particular prior move: a question of the user
        """
        pm = False
        if Move.preconditions_met(self,infostate):
            if infostate['shared']['moves'][-1][2] > 0.70: # the confidence of the question should be high enough
                pm = True
        return pm

    def effects(self,infostate,knowledge):
        """
        effects
        =====
        Function to apply this move's effects to the information state

        In addition to adding this move to the shared conversation information state, it has the following effects:
            - the question under discussion is updated
        """
        Move.effects(self,infostate)
        infostate['shared']['qud'] = [infostate['shared']['moves'][-2][1]]
