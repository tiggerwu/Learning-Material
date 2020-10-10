import numpy as np
import pandas as pd
from functools import reduce

## Function to create a conditional probability table
## Conditional probability is of the form p(x1 | x2, ..., xk)
## varnames: vector of variable names (strings) first variable listed 
##           will be x_i, remainder will be parents of x_i, p1, ..., pk
## probs: vector of probabilities for the flattened probability table
## outcomesList: a list containing a vector of outcomes for each variable
## factorTable is in the type of pandas dataframe
## See the test file for examples of how this function works
def readFactorTable(varnames, probs, outcomesList):
    factorTable = pd.DataFrame({'probs': probs})

    totalfactorTableLength = len(probs)
    numVars = len(varnames)

    k = 1
    for i in range(numVars - 1, -1, -1):
        levs = outcomesList[i]
        numLevs = len(levs)
        col = []
        for j in range(0, numLevs):
            col = col + [levs[j]] * k
        factorTable[varnames[i]] = col * int(totalfactorTableLength / (k * numLevs))
        k = k * numLevs

    return factorTable

## Build a factorTable from a data frame using frequencies
## from a data frame of data to generate the probabilities.
## data: data frame read using pandas read_csv
## varnames: specify what variables you want to read from the table
## factorTable is in the type of pandas dataframe
def readFactorTablefromData(data, varnames):
    numVars = len(varnames)
    outcomesList = []

    for i in range(0, numVars):
        name = varnames[i]
        outcomesList = outcomesList + [list(set(data[name]))]

    lengths = list(map(lambda x: len(x), outcomesList))
    m = reduce(lambda x, y: x * y, lengths)
   
    factorTable = pd.DataFrame({'probs': np.zeros(m)})

    k = 1
    for i in range(numVars - 1, -1, -1):
        levs = outcomesList[i]
        numLevs = len(levs)
        col = []
        for j in range(0, numLevs):
            col = col + [levs[j]] * k
        factorTable[varnames[i]] = col * int(m / (k * numLevs))
        k = k * numLevs

    numLevels = len(outcomesList[0])

    # creates the vector called fact to index probabilities 
    # using matrix multiplication with the data frame
    fact = np.zeros(data.shape[1])
    lastfact = 1
    for i in range(len(varnames) - 1, -1, -1):
        fact = np.where(np.isin(list(data), varnames[i]), lastfact, fact)
        lastfact = lastfact * len(outcomesList[i])

    # Compute unnormalized counts of subjects that satisfy all conditions
    a = (data - 1).dot(fact) + 1
    for i in range(0, m):
        factorTable.at[i,'probs'] = sum(a == (i+1))

    # normalize the conditional probabilities
    skip = int(m / numLevels)
    for i in range(0, skip):
        normalizeZ = 0
        for j in range(i, m, skip):
            normalizeZ = normalizeZ + factorTable['probs'][j]
        for j in range(i, m, skip):
            if normalizeZ != 0:
                factorTable.at[j,'probs'] = factorTable['probs'][j] / normalizeZ

    return factorTable


## Join of two factors
## factor1, factor2: two factor tables
##
## Should return a factor table that is the join of factor 1 and 2.
## You can assume that the join of two factors is a valid operation.
## Hint: You can look up pd.merge for mergin two factors
def joinFactors(factor1, factor2):
    # your code
    #We use pd.DataFrame.copy() to avoid changing the original factor table
    factor1_copy = pd.DataFrame.copy(factor1)
    factor2_copy = pd.DataFrame.copy(factor2)
    #Figure the same column for factor1 and factor2
    samecolumn = list(column for column in factor1_copy.columns if column in factor2_copy.columns)
    samecolumn.remove('probs')
    #Discuss whether factor1 and factor2 has same column name besides 'probs' 
    if len(samecolumn) == 0:
        #Plus 'augxiliary' column to pd.merge
        factor1_copy['augxiliary'] = 0
        factor2_copy['augxiliary'] = 0
        factor = pd.merge(factor1_copy,factor2_copy,how='outer',on=['augxiliary'])
        #Count the new probability
        factor['probs_x'] *= factor['probs_y']
        #Drop the unnecessary columns
        factor = factor.drop(['probs_y','augxiliary'],axis=1)
        factor = factor.rename(columns = {'probs_x':'probs'}) 
    else:
        #pd.merge by same column
        factor = pd.merge(factor1_copy,factor2_copy,how='outer',on=samecolumn)
        #Count the new probability
        factor['probs_x'] *= factor['probs_y']
        #Drop the unnecessary columns
        factor = factor.drop(['probs_y'],axis=1)
        factor = factor.rename(columns = {'probs_x':'probs'}) 

    return factor

## Marginalize a variable from a factor
## table: a factor table in dataframe
## hiddenVar: a string of the hidden variable name to be marginalized
##
## Should return a factor table that marginalizes margVar out of it.
## Assume that hiddenVar is on the left side of the conditional.
## Hint: you can look can pd.groupby
def marginalizeFactor(factorTable, hiddenVar):
    # your code 
    #We use pd.DataFrame.copy() to avoid changing the original factor table
    factor = pd.DataFrame.copy(factorTable) 
    column = list(factor.columns)
    column.remove('probs')
    column.remove(hiddenVar)
    #The columns we need is remained
    factor = factor.drop(hiddenVar,axis=1)
    #Group by the columns, sum the 'probs' up
    factor = factor[factor.columns].groupby(column,as_index=False).sum()
    #Put the 'probs' column to the first
    probs_content = factor['probs']
    factor = factor.drop('probs',axis=1)
    factor.insert(0,'probs',probs_content,True)

    return factor

## Marginalize a list of variables 
## bayesnet: a list of factor tables and each table is in dataframe type
## hiddenVar: a string of the variable name to be marginalized
##
## Should return a Bayesian network containing a list of factor tables that results
## when the list of variables in hiddenVar is marginalized out of bayesnet.
def marginalizeNetworkVariables(bayesNet, hiddenVar):
    # your code 
    bayesNet_update = bayesNet.copy()
    #Figure out all the column names
    column = []
    for factor in bayesNet_update:
        column.extend(list(factor.columns))
    column = set(column)
    #For every hidden variable, firstly join the factors related to it, then marginalize it
    for var in hiddenVar:
        if var in column:
            bayesNet_left = bayesNet_update.copy()
            factor_update = pd.DataFrame(columns=['probs'])
            #Consider the factor in net, whether it's related to hidden variable
            for factor in bayesNet_left:
                if var in factor.columns:
                    #If the factor is related to hidden variable, delete it in net
                    for j in range(len(bayesNet_update)):
                        if list(bayesNet_update[j].columns) == list(factor.columns):
                            del bayesNet_update[j]
                            break
                    #Join it with updated factor
                    if factor_update.empty:
                        factor_update = factor
                    else:
                        factor_update = joinFactors(factor_update,factor)
            #Marginalize the hidden variable
            factor_update = marginalizeFactor(factor_update,var)
            #Put the new factor into the net
            bayesNet_update.append(factor_update)
    
    return bayesNet_update
    

## Update BayesNet for a set of evidence variables
## bayesNet: a list of factor and factor tables in dataframe format
## evidenceVars: a vector of variable names in the evidence list
## evidenceVals: a vector of values for corresponding variables (in the same order)
##
## Set the values of the evidence variables. Other values for the variables
## should be removed from the tables. You do not need to normalize the factors
def evidenceUpdateNet(bayesNet, evidenceVars, evidenceVals):
    # your code 
    bayesNet_update = bayesNet.copy()
    #Consider the evidence variable one by one
    for i in range(len(evidenceVars)):
        bayesNet_left = bayesNet_update.copy()
        #For every factor in net, only remain the evidence variable with its instructed value
        for factor in bayesNet_left:
            if evidenceVars[i] in factor.columns:
                for j in range(len(bayesNet_update)):
                    if list(bayesNet_update[j].columns) == list(factor.columns):
                        del bayesNet_update[j]
                        break
                #Figure the new factor, and add it to the net
                factor_update = factor[factor[evidenceVars[i]]==evidenceVals[i]]
                bayesNet_update.append(factor_update)
    return bayesNet_update


## Run inference on a Bayesian network
## bayesNet: a list of factor tables and each table iin dataframe type
## hiddenVar: a string of the variable name to be marginalized
## evidenceVars: a vector of variable names in the evidence list
## evidenceVals: a vector of values for corresponding variables (in the same order)
##
## This function should run variable elimination algorithm by using 
## join and marginalization of the sets of variables. 
## The order of the elimiation can follow hiddenVar ordering
## It should return a single joint probability table. The
## variables that are hidden should not appear in the table. The variables
## that are evidence variable should appear in the table, but only with the single
## evidence value. The variables that are not marginalized or evidence should
## appear in the table with all of their possible values. The probabilities
## should be normalized to sum to one.
def inference(bayesNet, hiddenVar, evidenceVars, evidenceVals):
    # your code 
    bayesNet_update = bayesNet.copy()
    #Firstly, filter the evidence value which are not satisfied with the instruction
    bayesNet_update = evidenceUpdateNet(bayesNet_update,evidenceVars,evidenceVals)
    #Secondly, marginalize the hidden variable
    bayesNet_update = marginalizeNetworkVariables(bayesNet_update,hiddenVar)
    
    #Join the remained factors until there is only one factor, which is the factor we query
    while len(bayesNet_update) != 1:
        factor1 , factor2 = np.random.choice(bayesNet_update,2)
        if len(set(factor1.columns).intersection(set(factor2.columns))) > 1 and list(factor1.columns) != list(factor2.columns):
            for j in range(len(bayesNet_update)):
                if list(bayesNet_update[j].columns) == list(factor1.columns):
                    del bayesNet_update[j]
                    break
            for j in range(len(bayesNet_update)):
                if list(bayesNet_update[j].columns) == list(factor2.columns):
                    del bayesNet_update[j]
                    break
            factor_update = joinFactors(factor1,factor2)
            bayesNet_update.append(factor_update)
    factor_final = bayesNet_update[0]

    #Normalize
    total = sum(list(factor_final['probs']))
    factor_final['probs'] /= total
    
    return factor_final





