import numpy as np
import pandas as pd

class Agent:
    ### START CODE HERE ###

    def __init__(self, actions):
        self.actions = actions
        self.epsilon = 1
        self.decay = 0.9
        self.rate = 0.1
        self.q_table = pd.DataFrame(columns = self.actions ,dtype=np.float64)
        self.action_table = pd.DataFrame(columns = self.actions, dtype=np.object)
        self.ob_table = {}
        self.func_table = pd.DataFrame(columns = self.actions , dtype=np.float64)

    def choose_action(self, observation):
        if observation not in self.q_table.index:
            self.q_table = self.q_table.append(pd.Series([0]*len(self.actions),index=self.q_table.columns,name=observation,))
        if observation not in self.ob_table.keys():
            self.ob_table[observation]=1
        if observation not in self.func_table.index:
            self.func_table = self.func_table.append(pd.Series([1]*len(self.actions),index=self.func_table.columns,name=observation))

        if np.random.uniform() < self.epsilon:
            action = self.func_table.ix[observation,:]
            if action[0] == action[1] and action[1] == action[2] and action[2] == action[3]:
                action = np.random.choice(self.actions)
            else:
                action = action.reindex(np.random.permutation(action.index))
                action = action.argmax()

        else:
            action = np.random.choice(self.actions)    #随机选择一个动作
  
        self.ob_table[observation] += 1    
        return action

    def update(self, s, a, r, s_):
        if s_ not in self.q_table.index:
            self.q_table = self.q_table.append(pd.Series([0]*len(self.actions),index=self.q_table.columns,name=s_))
        if s_ not in self.ob_table.keys():
            self.ob_table[s_]=1
        if s_ not in self.func_table.index:
            self.func_table = self.func_table.append(pd.Series([1]*len(self.actions),index=self.func_table.columns,name=s_))

        coe = 1
        func_update = -100
        for action in self.actions:
            func_tmp = r + self.decay * (self.q_table.ix[s_,action] + coe/self.ob_table[s_])
            if func_update < func_tmp:
                func_update = func_tmp
        self.func_table.ix[s, a] = (1 - self.rate) * self.func_table.ix[s,a] + self.rate * (func_update - self.func_table.ix[s,a])

        q_update = -100
        for action in self.actions:
            q_tmp = r + self.decay * self.q_table.ix[s_,action]
            if q_update < q_tmp:
                q_update = q_tmp
        self.q_table.ix[s, a] = (1 - self.rate) * self.q_table.ix[s,a] + self.rate * (q_update - self.q_table.ix[s,a])

    def store(self,s,a,r,s_):
        if s not in self.action_table.index:
            self.action_table = self.action_table.append(pd.Series([None]*len(self.actions),index=self.action_table.columns,name=s,))
        self.action_table.set_value(s,a,(r,s_))

    def simulation(self):
        while True:
            s_simu = np.random.choice(self.action_table.index)
            a_simu = np.random.choice(self.action_table.loc[s_simu].index)
            if self.action_table.ix[s_simu,a_simu] != None:
                break
        r_simu,ns_simu = self.action_table.ix[s_simu,a_simu]
        return s_simu,a_simu,r_simu,ns_simu

    ### END CODE HERE ###