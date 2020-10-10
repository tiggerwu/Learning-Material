from agent import Agent
import time

maze = '2'

if maze == '1':
    from maze_env1 import Maze
elif maze == '2':
    from maze_env2 import Maze


if __name__ == "__main__":
    ### START CODE HERE ###


    env = Maze()
    agent = Agent(actions=list(range(env.n_actions)))
    start = False

    for episode in range(300):
        s = env.reset()
        episode_reward = 0
        while True:
            a = agent.choose_action(str(s))
            s_, r, done = env.step(a)

            agent.update(str(s),a,r,str(s_))
            agent.store(str(s),a,r,s_)
            for simulation_times in range(30):
                s_simu,a_simu,r_simu,ns_simu = agent.simulation()
                agent.update(s_simu,a_simu,r_simu,str(ns_simu))
                
            episode_reward += r

            s = s_

            if done:
                break
            
        print('episode:', episode, 'episode_reward:', episode_reward)

    ### END CODE HERE ###
    
    print('\ntraining over\n')