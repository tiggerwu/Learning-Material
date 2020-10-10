import random
import numpy as np
import pandas as pd
import tensorflow as tf
import gym
from collections import deque
from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Activation, Flatten, Conv1D, MaxPooling1D,Reshape
import matplotlib.pyplot as plt

class DQN:
    ### TUNE CODE HERE ###
    def __init__(self, env):
        self.env = env
        self.memory = deque(maxlen=500000)
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min =0.01
        self.epsilon_decay = (self.epsilon-self.epsilon_min) / 1000000
                                                                    
        self.batch_size = 32
        self.train_start = 20000
        self.state_size = self.env.observation_space.shape[0]
        self.action_size =self.env.action_space.n
        self.learning_rate = 0.0001

        self.evaluation_model = self.create_model()
        self.target_model = self.create_model()
        
    def create_model(self):
        model = Sequential()
        model.add(Dense(128*2, input_dim=self.state_size,activation='relu', kernel_initializer="he_uniform"))
        model.add(Dense(128*2, activation='relu', kernel_initializer="he_uniform"))
        model.add(Dense(128*2, activation='relu', kernel_initializer="he_uniform"))
        model.add(Dense(128*2, activation='relu', kernel_initializer="he_uniform"))
        model.add(Dense(self.env.action_space.n, activation='linear'))
        optimizer = optimizers.Adam(lr=self.learning_rate)
        model.compile(loss='mean_squared_error', optimizer=optimizer)
        return model
    
    def choose_action(self, state, steps):
        if steps > 50000:
            if self.epsilon > self.epsilon_min:
                self.epsilon -= self.epsilon_decay
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        return np.argmax(self.evaluation_model.predict(state)[0])
        
    def remember(self, cur_state, action, reward, new_state, done):
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0
        
        transition = (cur_state, action, reward, new_state, done)
        self.memory.extend([transition])
        
        self.memory_counter += 1
    
    def replay(self):
        if len(self.memory) < self.train_start:
            return
        
        mini_batch = random.sample(self.memory, self.batch_size)
        
        update_input = np.zeros((self.batch_size, self.state_size))
        update_target = np.zeros((self.batch_size, self.action_size))
        
        for i in range(self.batch_size):
            state, action, reward, new_state, done = mini_batch[i]
            target = self.evaluation_model.predict(state)[0]
        
            if done:
                target[action] = reward
            else:
                target[action] = reward + self.gamma * np.amax(self.target_model.predict(new_state)[0])
            
            update_input[i] = state
            update_target[i] = target
    
        self.evaluation_model.fit(update_input, update_target, batch_size=self.batch_size, epochs=1, verbose=0)
    
    def target_train(self):
        self.target_model.set_weights(self.evaluation_model.get_weights())
        return
    
    def visualize(self, reward, episode):
        plt.plot(episode, reward, 'ob-')
        plt.title('Average reward each 100 episode')
        plt.ylabel('Reward')
        plt.xlabel('Episodes')
        plt.grid()
        plt.savefig("result.png")
        plt.show()
    ### END CODE HERE ###
    
        
def main():
    env = gym.make('Breakout-ram-v0')
    env = env.unwrapped
    
    episodes = 5000
    trial_len = 10000
    
    tmp_reward=0
    total_reward = 0
    
    graph_reward = []
    graph_episodes = []
    
    dqn_agent = DQN(env=env)

    ####### Training ######
    ### START CODE HERE ###
    
    ############To preprocess the input###########
    def preprocess(state):
        return np.float32(state/255.0)
    #############################################
    
    #############The frequency of replay and update evalaution network######## 
    T_target = 7000
    T_main = 16
    ##########################################################################

    episode100_reward = 0
    total_reward = 0
    update_count = 0
    sum_step = 0
    result=[]

    for episode in range(episodes):
        episode_reward = 0
        s = env.reset().reshape(1,128)
        s = preprocess(s)

        for step in range(trial_len):
            
            if episode >= 3000:
                env.render()
            
            update_count += 1
            sum_step += 1
            action = dqn_agent.choose_action(s, sum_step)
            s_, reward, done, info =env.step(action)
            s_ = s_.reshape(1,128)
            s_ = preprocess(s_)

            episode_reward += reward
            episode100_reward += reward
            total_reward += reward
            dqn_agent.remember(s, action, reward, s_,done)            

            if(step % T_main==0):
                dqn_agent.replay()

            s = s_
            
            if done:
                print("Episode ",episode,"'s reward:",episode_reward)         
                env.reset()
                if(update_count >= T_target):
                    update_count = 0
                    dqn_agent.target_train()
                if (episode+1) % 100 == 0: 
                    print("The average reward of latest 100 episodes to episode ",episode," is ",episode100_reward/100)
                    result.append([episode,episode100_reward/100])
                    episode100_reward = 0  
                break
        
            
    print("end of training, average total_reward : ",total_reward/5000)
    for i,score in result :
       print("The average reward of ",i," is : ",score)
    env.close()


    ### END CODE HERE ###

    dqn_agent.visualize(graph_reward, graph_episodes)
    
if __name__ == '__main__':
    main()