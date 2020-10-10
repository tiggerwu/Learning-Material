# -*- coding: utf-8 -*-
from queue import LifoQueue
from queue import Queue
from queue import PriorityQueue

class Graph:
    """
    Defines a graph with edges, each edge is treated as dictionary
    look up. function neighbors pass in an id and returns a list of 
    neighboring node
    
    """
    def __init__(self):
        self.edges = {}
    
    def neighbors(self, id):
        # check if the edge is in the edge dictionary
        if id in self.edges:
            return self.edges[id]
        else:
            print("The node ", id , " is not in the graph")
            return False


def reconstruct_path(came_from, start, goal):
    """
    Given a dictionary of came_from where its key is the node 
    character and its value is the parent node, the start node
    and the goal node, compute the path from start to the end

    Arguments:
    came_from -- a dictionary indicating for each node as the key and 
                 value is its parent node
    start -- A character indicating the start node
    goal --  A character indicating the goal node

    Return:
    path. -- A list storing the path from start to goal. Please check 
             the order of the path should from the start node to the 
             goal node
    """
    path = []
    ### START CODE HERE ### (≈ 6 line of code)
    path.append(goal)					#将goal添加到路径中
    while(goal != start):				#依次添加从goal到start的节点
    	goal = came_from[goal]
    	path.append(goal)
    path.reverse()						#逆序得到正确的路径
    ### END CODE HERE ###
    return path

def breadth_first_search(graph, start, goal):
    """
    Given a graph, a start node and a goal node
    Utilize breadth first search algorithm by finding the path from 
    start node to the goal node
    Use early stoping in your code
    This function returns back a dictionary storing the information of each node
    and its corresponding parent node
    Arguments:
    graph -- A dictionary storing the edge information from one node to a list 
             of other nodes
    start -- A character indicating the start node
    goal --  A character indicating the goal node

    Return:
    came_from -- a dictionary indicating for each node as the key and 
                value is its parent node
    """
    came_from = {}
    came_from[start] = None
    ### START CODE HERE ### (≈ 10 line of code)
    if start not in graph.edges.keys() or goal not in graph.edges.keys():   #检查start和goal是否为graph里的node
        print("Not valid node!")
        return False

    fringe = Queue()                                #Fringe List为一个FIFO队列，存储待扩展的节点
    closed = []                                     #Closed List为一个列表，存储已搜索的节点

    fringe.put(start)                               #放置start节点
    closed.append(start)                            #将start放置于已扩展列表中
    while not fringe.empty():                       #当Fringe List不空且未搜索到goal时，一直进行循环
    	current = fringe.get()
    	for child in graph.neighbors(current):      #对每个子节点进行：判断是否搜索过，若无则入队，并设为已搜索
    		if child not in closed:
    			fringe.put(child)
    			closed.append(child)
    			came_from[child] = current
    		if child == goal:                       #直到搜索到goal停止
    			break
    ### END CODE HERE ###
    return came_from




def depth_first_search(graph, start, goal):
    """
    Given a graph, a start node and a goal node
    Utilize depth first search algorithm by finding the path from 
    start node to the goal node
    Use early stoping in your code
    This function returns back a dictionary storing the information of each node
    and its corresponding parent node
    Arguments:
    graph -- A dictionary storing the edge information from one node to a list 
             of other nodes
    start -- A character indicating the start node
    goal --  A character indicating the goal node

    Return:
    came_from -- a dictionary indicating for each node as the key and 
                value is its parent node
    """
    came_from = {}
    came_from[start] = None
    ### START CODE HERE ### (≈ 10 line of code)
    if start not in graph.edges.keys() or goal not in graph.edges.keys():   #检查start和goal是否为graph里的node
        print("Not valid node!")
        return False

    fringe = LifoQueue()                            #Fringe List为一个FILO队列(栈)，存储待扩展的节点
    closed = []                                     #Closed List为一个列表，存储已搜索的节点

    fringe.put(start)                               #放置start节点
    closed.append(start)                            #将start放置于已扩展列表中
    while not fringe.empty():                       #当Fringe List不空且未搜索到goal时，一直进行循环
    	current = fringe.get()
    	for child in graph.neighbors(current)[::-1]:      #对每个子节点进行：判断是否搜索过，若无则入队，并设为已搜索
    		if child not in closed:
    			fringe.put(child)
    			closed.append(child)
    			came_from[child] = current
    		if child == goal:                       #直到搜索到goal停止
    			break
    ### END CODE HERE ###
    
    return came_from



# The main function will first create the graph, then use depth first search
# and breadth first search which will return the came_from dictionary 
# then use the reconstruct path function to rebuild the path.
if __name__=="__main__":
    small_graph = Graph()
    small_graph.edges = {
        'A': ['B','D'],
        'B': ['A', 'C', 'D'],
        'C': ['A'],
        'D': ['E', 'A'],
        'E': ['B']
    }
    large_graph = Graph()
    large_graph.edges = {
        'S': ['A','C'],
        'A': ['S','B','D'],
        'B': ['S', 'A', 'D','H'],
        'C': ['S','L'],
        'D': ['A', 'B','F'],
        'E': ['G','K'],
        'F': ['H','D'],
        'G': ['H','E'],
        'H': ['B','F','G'],
        'I': ['L','J','K'],
        'J': ['L','I','K'],
        'K': ['I','J','E'],
        'L': ['C','I','J']
    }
    print("Large graph")
    start = 'S'
    goal = 'E'
    came_fromDFS = depth_first_search(large_graph, start, goal)
    print("came from DFS" , came_fromDFS)
    pathDFS = reconstruct_path(came_fromDFS, start, goal)
    print("path from DFS", pathDFS)
    came_fromBFS = breadth_first_search(large_graph, start, goal)
    print("came from BFS", came_fromBFS)
    pathBFS = reconstruct_path(came_fromBFS, start, goal)
    print("path from BFS", pathBFS)

    print("Small graph")
    start = 'A'
    goal = 'E'
    came_fromDFS = depth_first_search(small_graph, start, goal)
    print("came from DFS" , came_fromDFS)
    pathDFS = reconstruct_path(came_fromDFS, start, goal)
    print("path from DFS", pathDFS)
    came_fromBFS = breadth_first_search(small_graph, start, goal)
    print("came from BFS", came_fromBFS)
    pathBFS = reconstruct_path(came_fromBFS, start, goal)
    print("path from BFS", pathBFS)
