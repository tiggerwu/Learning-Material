import math
import numpy as np
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)

from LDA import LDA
from NBC import NBC
from SVM import SVM
from LOG import LOG
from Iris_LDA import Iris_LDA
from Iris_NBC import Iris_NBC
from Iris_SVM import Iris_SVM
from Iris_LOG import Iris_LOG

if __name__ == '__main__':

    #Question 1 :
    print('The answer for Question1:')
    LDA1 = LDA()
    LDA1.validation_80to20()
    print(' ')

    #Question 2 :
    print('The answer for Question2:')
    NBC1 = NBC()
    NBC1.cross_validation()
    print(' ')

    #Question 3 :
    print('The answer for Question3:')
    SVM1 = SVM()
    SVM1.validation_80to20()
    print(' ')

    #Supplement Question :
    #The algorithm performance in Watermelon 3.0:
    #NBC:
    print('The performance of NBC in Watermelon 3.0:')
    NBC1 = NBC()
    NBC1.cross_validation()
    print(' ')
    #LDA:
    print('The performance of LDA in Watermelon 3.0:')
    LDA1 = LDA()
    LDA1.cross_validation()
    print(' ')
    #LOG:
    print('The performance of LOG in Watermelon 3.0:')
    LOG1 = LOG()
    LOG1.cross_validation()
    print(' ')
    #SVM:
    print('The performance of SVM in Watermelon 3.0:')
    SVM1 = SVM()
    SVM1.cross_validation()
    print(' ')
    #The algorithm performance in Iris:
    #NBC:
    print('The performance of NBC in Iris:')
    NBC1 = Iris_NBC()
    NBC1.cross_validation()
    print(' ')
    #LDA:
    print('The performance of LDA in Iris:')
    LDA1 = Iris_LDA()
    LDA1.cross_validation()
    print(' ')
    #LOG:
    print('The performance of LOG in Iris:')
    LOG1 = Iris_LOG()
    LOG1.cross_validation()
    print('')
    #SVM:
    print('The performance of SVM in Iris:')
    SVM1 = Iris_SVM()
    SVM1.cross_validation()
    print(' ')