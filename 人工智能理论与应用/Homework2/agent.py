import random, re, datetime


class Agent(object):
    def __init__(self, game):
        self.game = game

    def getAction(self, state):
        raise Exception("Not implemented yet")


class RandomAgent(Agent):
    def getAction(self, state):
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)


class SimpleGreedyAgent(Agent):
    # a one-step-lookahead greedy agent that returns action with max vertical advance
    def getAction(self, state):
        legal_actions = self.game.actions(state)

        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        if player == 1:
            max_vertical_advance_one_step = max([action[0][0] - action[1][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[0][0] - action[1][0] == max_vertical_advance_one_step]
        else:
            max_vertical_advance_one_step = max([action[1][0] - action[0][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[1][0] - action[0][0] == max_vertical_advance_one_step]
        self.action = random.choice(max_actions)


class ArtificialFoolAgent(Agent):
    def getAction(self, state):
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        ### START CODE HERE ###

		#in the start of the game
        if self.count < 5:
            #self.action = self.GreedyMove(state,1)[1]
            self.action = self.minimax(state,2)[0]
        #in the mid and end of the game
        else:
            search_depth = 2
            decision = None
            decision, score = self.minimax(state, search_depth)
            self.action = decision

        if self.count_completeness(state) >= 9:
            self.count = 0

    def __init__(self, game,count=0):
        self.game = game
        self.count = count    #used to determine the start of the game

    #A greedy strategy with the depth of 0,1,2
    def GreedyMove(self,state,steps=1):
        if steps == 0:
            ver_move = 0
            optimal_move = [None,None]
        elif steps == 1:
            legal_actions = self.game.actions(state)
            player = self.game.player(state)
            if player == 1:
                max_vertical_advance_one_step = max([action[0][0] - action[1][0] for action in legal_actions])
                max_actions = [action for action in legal_actions if
                            action[0][0] - action[1][0] == max_vertical_advance_one_step]
            else:
                max_vertical_advance_one_step = max([action[1][0] - action[0][0] for action in legal_actions])
                max_actions = [action for action in legal_actions if
                            action[1][0] - action[0][0] == max_vertical_advance_one_step]
            ver_move = max_vertical_advance_one_step
            optimal_move = [max_actions,None]
        else:
            ver_move = 0
            player = self.game.player(state)
            legal_actions = self.game.actions(state)
            for action in legal_actions:
                if player == 1:
                    ver_firstmove = action[0][0] - action[1][0]
                else:
                    ver_firstmove = action[1][0] - action[0][0]
                state_tmp = self.game.succ(state,action)
                state_next = self.game.succ(state_tmp,random.choice(self.game.actions(state_tmp)))
                legal_actions_next = self.game.actions(state_next)
                for action_next in legal_actions_next:
                    if player == 1:
                        ver_secondmove = action_next[0][0] - action_next[1][0]
                        if ver_firstmove + ver_secondmove > ver_move:
                            ver_move = ver_firstmove + ver_secondmove
                            optimal_move = [action,action_next]
                    else:
                        ver_secondmove = action_next[1][0] - action_next[0][0]
                        if ver_firstmove + ver_secondmove > ver_move:
                            ver_move = ver_firstmove + ver_secondmove
                            optimal_move = [action,action_next]
            print(player)
        return (ver_move,optimal_move)

    #A sum max advance evaluation
    def sum_max_advance_eval(self, state):
        legal_actions = self.game.actions(state)
        max_sum = 0
        calculated = {}
        if state[0] == 2:
            for action in legal_actions:
                if action[0] not in calculated or (action[0] in calculated and calculated[action[0]] < action[1][0] - action[0][0]):
                    calculated[action[0]] = action[1][0] - action[0][0]
            for item in calculated:
                max_sum += calculated[item]
        else:
            for action in legal_actions:
                if action[0] not in calculated or (action[0] in calculated and calculated[action[0]] < action[0][0] - action[1][0]):
                    calculated[action[0]] = action[0][0] - action[1][0]
            for item in calculated:
                max_sum += calculated[item]
        return max_sum

    #Vertical evaluation function
    def ver_eval(self, my_pos, player):
        #considering that the column is not the same this eval can be more accurate
        partial_eval = 0
        assert player == 1 or player == 2, 'player number is incorrect!!'
        if player == 2:
            for chess in my_pos:
                partial_eval += chess[0]

        else:
            for chess in my_pos:
                partial_eval += 20 - chess[0]

        return partial_eval
    
    #Opponent's vertical evaluation function
    def opp_eval(self, opp_pos, player):
        partial_eval = 0
        if player == 2:
            for chess in opp_pos:
                partial_eval += chess[0]
        else:
            for chess in opp_pos:
                partial_eval += 20 - chess[0]
        return partial_eval

    #Horizontal evaluation function
    def hor_eval(self, my_pos, player):
        partial_eval = 0
        for chess in my_pos:
            col_num = self.game.board.getColNum(chess[0])
            mid_col = (col_num + 1) / 2
            partial_eval -= abs(chess[1] - mid_col) ** 2
        return partial_eval

    #The distance from current positions to destinaton corner evaluation function
    def L2_eval(self, my_pos, player):
        L2_dis = 0  #a new approach to count L2_dis
        if player == 2:
            for pos in my_pos:
                col_num = self.game.board.getColNum(pos[0])
                mid_col = (col_num + 1) / 2
                L2_dis += (pos[0]-19)**2 + (pos[1]-mid_col)**2
        if player ==1:
            for pos in my_pos:
                col_num = self.game.board.getColNum(pos[0])
                mid_col = (col_num + 1) / 2
                L2_dis += (pos[0]-1)**2 + (pos[1]-mid_col)**2
        return L2_dis

    #The final evaluation 
    def evaluation(self, state):
        evaluate = 0
        player = state[0]
        board = state[1]
        my_pos = board.getPlayerPiecePositions(state[0])
        opp_pos = board.getPlayerPiecePositions(3 - state[0])

        p1 = 20  #weights for each eval
        p2 = 1
        p3 = -2
        p4 = 10
        #evaluate = p1 * self.ver_eval(my_pos, player) + p2 * self.hor_eval(my_pos, player) + p3 * L2 + p4 * self.opp_eval(opp_pos, player)
        # In the end of the game, we change the evaluation as below
        if self.count_completeness(state) > 5:
            if player == 2:
                complete_state = [(19,1), (18,1), (18,2), (17,1), (17,2), (17,3), (16,1), (16,2), (16,3), (16,4)]
            else:
                complete_state = [(1,1), (2,1), (2,2), (3,1), (3,2), (3,3), (4,1), (4,2), (4,3), (4,4)]
            complete_dis = 0
            dif_set1 = list(set(complete_state) - set(my_pos))
            dif_set2 = list(set(my_pos) - set(complete_state))
            for pos in dif_set2:
                complete_dis += min([ (pos[0] - targ_pos[0])**2 + ((pos[1] - (self.game.board.getColNum(pos[0])+1)/2)+\
                ((self.game.board.getColNum(targ_pos[0])+1)/2-targ_pos[1]))**2  for targ_pos in dif_set1])
            #evaluate = p3 * complete_dis #it will have backforth situation
            evaluate = p2 * self.hor_eval(my_pos, player) + p3 * complete_dis + p4 * self.opp_eval(opp_pos, player)
        else:
            evaluate = p2 * self.hor_eval(my_pos, player) + p3 * self.L2_eval(my_pos, player) + p4 * self.opp_eval(opp_pos, player)
        return evaluate

    #Max layer function
    def max_layer(self, state, layer, alpha, beta):
        """mutual recursion with min_layer"""
        import sys
        if layer == 0:
            return self.evaluation(state)

        legal_actions = self.game.actions(state)
        value = sys.maxsize * (-1)

        from queue import PriorityQueue
        search_order = PriorityQueue()
        for action in legal_actions:
            search_order.put((self.evaluation(self.game.succ(state, action)), action))

        while not search_order.empty():
            action = search_order.get()[1]
            value = max(value, self.min_layer(self.game.succ(state, action), layer-1, alpha, beta))
            if value >= beta:
                if layer == 2:
                    return value, action
                else:
                    return value

            if value > alpha:
                alpha = value
                if layer == 2:
                    self.action = action
                best_action = action

        if layer == 2:
            return value, best_action
        else:
            return value

    #Min layer function
    def min_layer(self, state, layer, alpha, beta):
        
        import sys

        if layer == 0:
            return self.evaluation(state)

        legal_actions = self.game.actions(state)
        value = sys.maxsize

        if state[0] == 1:
            legal_actions.sort(key=self.weighted_search_order)
        else:
            legal_actions.sort(key=self.reversed_weighted_search_order)
        for action in legal_actions:
            value = min(value, self.max_layer(self.game.succ(state, action), layer-1, alpha, beta))
            if value <= alpha:
                return value

            beta = min(value, beta)
        return value

    import sys
    def minimax(self, state, layer, alpha=sys.maxsize*(-1), beta=sys.maxsize):
        value, action = self.max_layer(state, layer, alpha, beta)
        return action, value

    #This function is used to count the completeness
    def count_completeness(self, state):
        my_pos = state[1].getPlayerPiecePositions(state[0])
        if state[0] == 2:
            complete_state = [(19,1), (18,1), (18,2), (17,1), (17,2), (17,3), (16,1), (16,2), (16,3), (16,4)]
        else:
            complete_state = [(1,1), (2,1), (2,2), (3,1), (3,2), (3,3), (4,1), (4,2), (4,3), (4,4)]

        count = len(complete_state) - len(list(set(complete_state) - set(my_pos)))

        return count

    #Different search order we use to help pruning
    def search_order(self, legal_action):
        """
        During test, we find that inappropriate order will miss a better choice.(Especially if the value is the same)
        According to the textbook, we should try to examine first the successors that are likely to be best.
        In this way, we can also prune more branches, which makes our algorithm run faster.
        """
        return legal_action[1][0] - legal_action[0][0]

    def reverse_search_order(self, legal_action):
        return legal_action[0][0] - legal_action[1][0]

    def weighted_search_order(self, legal_action):
        return 20 * (legal_action[1][0] - legal_action[0][0]) + abs(legal_action[1][1] - self.game.board.getColNum(legal_action[1][0]))

    def reversed_weighted_search_order(self, legal_action):
        return 20 * (legal_action[0][0] - legal_action[1][0]) + abs(legal_action[1][1] - self.game.board.getColNum(legal_action[1][0]))

        ### END CODE HERE ###



