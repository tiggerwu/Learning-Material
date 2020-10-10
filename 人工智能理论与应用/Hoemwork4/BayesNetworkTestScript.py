#!/usr/bin/env python3

from BayesianNetworks import *
import numpy as np
import pandas as pd
import sys,os
path = os.path.abspath(os.path.dirname(sys.argv[0]))

#############################
## Example Tests from Bishop Pattern recognition textbook on page 377
#############################
BatteryState = readFactorTable(['battery'], [0.9, 0.1], [[1, 0]])
FuelState = readFactorTable(['fuel'], [0.9, 0.1], [[1, 0]])
GaugeBF = readFactorTable(['gauge', 'battery', 'fuel'], [0.8, 0.2, 0.2, 0.1, 0.2, 0.8, 0.8, 0.9], [[1, 0], [1, 0], [1, 0]])



carNet = [BatteryState, FuelState, GaugeBF] # carNet is a list of factors 
## Notice that different order of operations give the same answer
## (rows/columns may be permuted)
joinFactors(joinFactors(BatteryState, FuelState), GaugeBF)
joinFactors(joinFactors(GaugeBF, FuelState), BatteryState)

tmp1 = joinFactors(GaugeBF, BatteryState)
tmp2 = marginalizeFactor(joinFactors(GaugeBF, BatteryState), 'gauge')

marginalizeFactor(joinFactors(GaugeBF, BatteryState), 'gauge')
joinFactors(marginalizeFactor(GaugeBF, 'gauge'), BatteryState)

joinFactors(marginalizeFactor(joinFactors(GaugeBF, BatteryState), 'battery'), FuelState)
marginalizeFactor(joinFactors(joinFactors(GaugeBF, FuelState), BatteryState), 'battery')

marginalizeFactor(joinFactors(marginalizeFactor(joinFactors(GaugeBF, BatteryState), 'battery'), FuelState), 'gauge')
marginalizeFactor(joinFactors(marginalizeFactor(joinFactors(GaugeBF, BatteryState), 'battery'), FuelState), 'fuel')

evidenceUpdateNet(carNet, ['fuel'], [1])
evidenceUpdateNet(carNet, ['fuel', 'battery'], [1, 0])

## Marginalize must first combine all factors involving the variable to
## marginalize. Again, this operation may lead to factors that aren't
## probabilities.
marginalizeNetworkVariables(carNet, ['battery']) ## this returns back a list
marginalizeNetworkVariables(carNet, ['fuel']) ## this returns back a list
marginalizeNetworkVariables(carNet, ['battery', 'fuel'])

# inference
print("inference starts")
print(inference(carNet, ['battery', 'fuel'], [], []) )        ## chapter 8 equation (8.30)
print(inference(carNet, ['battery'], ['fuel'], [0]))           ## chapter 8 equation (8.31)
print(inference(carNet, ['battery'], ['gauge'], [0]))          ##chapter 8 equation  (8.32)
print(inference(carNet, [], ['gauge', 'battery'], [0, 0]))    ## chapter 8 equation (8.33)
print("inference ends")
###########################################################################
#RiskFactor Data Tests
###########################################################################
riskFactorNet = pd.read_csv(path+'/RiskFactorsData.csv')

# Create factors

income      = readFactorTablefromData(riskFactorNet, ['income'])
smoke       = readFactorTablefromData(riskFactorNet, ['smoke', 'income'])
exercise    = readFactorTablefromData(riskFactorNet, ['exercise', 'income'])
bmi         = readFactorTablefromData(riskFactorNet, ['bmi', 'income'])
diabetes    = readFactorTablefromData(riskFactorNet, ['diabetes', 'bmi'])
## you need to create more factor tables

risk_net = [income, smoke, exercise, bmi, diabetes]
print("income dataframe is ")
print(income)
factors = riskFactorNet.columns

# example test p(diabetes|smoke=1,exercise=2)

margVars = list(set(factors) - {'diabetes', 'smoke', 'exercise'})
obsVars  = ['smoke', 'exercise']
obsVals  = [1, 2]

p = inference(risk_net, margVars, obsVars, obsVals)
print(p)


### Please write your own test scrip similar to  the previous example 
###########################################################################
#HW4 test scrripts start from here
###########################################################################
defualt_connection = {'income':[],'bmi':['income','exercise'],'exercise':['income'],\
            'smoke':['income'],'bp':['income','exercise','smoke'],'cholesterol':['income','exercise','smoke'],\
            'diabetes':['bmi'],'stroke':['bmi','bp','cholesterol'],'attack':['bmi','bp','cholesterol'],'angina':['bmi','bp','cholesterol']}

class RiskFactorNet(object):
    def __init__(self,connection=defualt_connection):
        self.data = pd.read_csv(path+'/RiskFactorsData.csv')
        
        self.connection = connection
        self.BayesNet = []
        for item in self.connection.keys():
            node = self.connection[item].copy()
            node.insert(0,item)
            factor = readFactorTablefromData(self.data,node)
            self.BayesNet.append(factor)
    
    def Count_probility(self,query, evidenceVars, evidenceVals):
        Vars = list(self.connection.keys())
        hiddenVar = Vars
        for var in evidenceVars:
            hiddenVar.remove(var)
        if query in hiddenVar:
            hiddenVar.remove(query)

        return inference(self.BayesNet,hiddenVar,evidenceVars,evidenceVals)
    
    def Add_edge(self,edge):
        new_connection = self.connection.copy()
        for key in edge.keys():
            new_connection[key].extend(edge[key])
        new_net = RiskFactorNet(new_connection)

        return new_net

def question1(BayesNet):
    size = 0
    for factor in BayesNet.BayesNet:
        singlesize = factor.shape[0]
        size += singlesize
    print('The size of RiskFactorNet is :',size)

def question2(BayesNet):
    outcome_list = ['diabetes', 'stroke' , 'attack' , 'angina']
    evidenceVars = ['smoke','exercise']
    evidenceVals = [1,2]
    for outcome in outcome_list:
        print('What is the probability of the' , outcome , ' if I have bad habits (smoke and don’t exercise)?')
        print(BayesNet.Count_probility(outcome,evidenceVars,evidenceVals))
    evidenceVars = ['smoke','exercise']
    evidenceVals = [2,1]
    for outcome in outcome_list:
        print('What is the probability of the' , outcome , ' if I have good habits (don’t smoke and do exercise)?')
        print(BayesNet.Count_probility(outcome,evidenceVars,evidenceVals))
    evidenceVars = ['bp','cholesterol','bmi']
    evidenceVals = [1,1,3]
    for outcome in outcome_list:
        print('What is the probability of the' , outcome , ' if I have poor health (high blood pressure, high cholesterol, and overweight)?')
        print(BayesNet.Count_probility(outcome,evidenceVars,evidenceVals))
    evidenceVars = ['bp','cholesterol','bmi']
    evidenceVals = [3,2,2]
    for outcome in outcome_list:
        print('What is the probability of the' , outcome , ' if I have good health (low blood pressure, low cholesterol, and normal weight)?')
        print(BayesNet.Count_probility(outcome,evidenceVars,evidenceVals))

def question3(BayesNet):
    evidenceVars = ['income']
    outcome_list = ['diabetes', 'stroke' , 'attack' , 'angina']
    probability_dic = {}
    for outcome in outcome_list:
        probability_dic[outcome] = []
        for i in range(1,9):
            evidenceVals = [i]
            factor = BayesNet.Count_probility(outcome,evidenceVars,evidenceVals)
            print(factor)
            probability_dic[outcome].append(factor.loc[0,'probs'])
    
    import matplotlib.pyplot as plt
    x_axis = range(1,9)
    colors = ['red','green','blue','yellow']
    for i in range(4):
        plt.plot(x_axis,probability_dic[outcome_list[i]],color=colors[i],label=outcome_list[i])
    plt.legend()
    plt.xlabel('income')
    plt.ylabel('probability')
    plt.show()


def question4(BayesNet):
    edge = {'diabetes':['smoke','exercise'], 'stroke':['smoke','exercise'] , 'attack':['smoke','exercise'] , 'angina':['smoke','exercise']}
    new_BayesNet = BayesNet.Add_edge(edge)
    print('After adding the edges, we can get the probability as below : ')
    question2(new_BayesNet)
    return new_BayesNet

def question5(BayesNet):
    old_BayesNet = BayesNet
    print('After adding the edge to the BayesNetWork in question 4 , we can get the probability as below : ')
    evidenceVars = ['diabetes']
    evidenceVals = [1]
    print('The factor table for P(stroke |diabetes = 1) is as below : ')
    print(old_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals))
    factor = old_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals)
    print('P(stroke = 1 |diabetes = 1) = ',factor.loc[0,'probs'])
    evidenceVars = ['diabetes']
    evidenceVals = [3]
    print('The factor table for P(stroke|diabetes = 3) is as below : ')
    print(old_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals))
    factor = old_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals)
    print('P(stroke = 1 |diabetes = 3) = ',factor.loc[0,'probs'])

    edge = {'stroke':['diabetes']}
    new_BayesNet = BayesNet.Add_edge(edge)
    print('After adding the edge to the BayesNetWork in question 4 , we can get the probability as below : ')
    evidenceVars = ['diabetes']
    evidenceVals = [1]
    print('The factor table for P(stroke |diabetes = 1) is as below : ')
    print(new_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals))
    factor = new_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals)
    print('P(stroke = 1 |diabetes = 1) = ',factor.loc[0,'probs'])
    evidenceVars = ['diabetes']
    evidenceVals = [3]
    print('The factor table for P(stroke|diabetes = 3) is as below : ')
    print(new_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals))
    factor = new_BayesNet.Count_probility('stroke',evidenceVars,evidenceVals)
    print('P(stroke = 1 |diabetes = 3) = ',factor.loc[0,'probs'])

    
if __name__ == '__main__':
    net = RiskFactorNet()
    print('###########################################')
    print('The answer for question 1 is :')
    question1(net)
    print('###########################################')
    print('\n\n\n\n\n')
    print('###########################################')
    print('The answer for question 2 is :')
    question2(net)
    print('###########################################')
    print('\n\n\n\n\n')
    print('###########################################')
    print('The answer for question 3 is :')
    question3(net)
    print('###########################################')
    print('\n\n\n\n\n')
    print('###########################################')
    print('The answer for question 4 is :')
    new_net = question4(net)
    print('###########################################')
    print('\n\n\n\n\n')
    print('###########################################')
    print('The answer for question 5 is :')
    question5(new_net)
    print('###########################################')





