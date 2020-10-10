import math
import numpy as np
import pandas as pd
from sklearn import svm
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class Iris_SVM(object):
    
    def preprocessing(self,label,positive):
        
        if positive != 'all':
            for i in range(len(label)):
                if label.iloc[i,0] == positive:
                    label.iloc[i,0] = 1
                else:
                    label.iloc[i,0] = 0

        if positive == 'all':
            for i in range(len(label)):
                if label.iloc[i,0] == 'setosa':
                    label.iloc[i,0] = 0
                elif label.iloc[i,0] == 'versicolor':
                    label.iloc[i,0] = 1
                else:
                    label.iloc[i,0] = 2

        return label
        
    def LinearSVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=100, kernel='linear')
        svc.fit(train_feature,train_label.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def PolySVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=1, kernel='poly',degree=3)
        svc.fit(train_feature,train_label.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def RbfSVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=10000, kernel='rbf',gamma=0.01)
        svc.fit(train_feature,train_label.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def SigmoidSVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=5, kernel='sigmoid',gamma=2)
        svc.fit(train_feature,train_label.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def assess(self,train_feature,train_label,test_feature,test_label):
        
        test_label = self.preprocessing(test_label,'all')

        train_label1 = train_label.copy()
        train_label2 = train_label.copy()
        train_label3 = train_label.copy()

        train_label1 = self.preprocessing(train_label1,'setosa')
        predicted_label11 = self.LinearSVM(train_feature.values,train_label1.values,test_feature.values)
        predicted_label21 = self.PolySVM(train_feature.values,train_label1.values,test_feature.values)
        predicted_label31 = self.RbfSVM(train_feature.values,train_label1.values,test_feature.values)
        predicted_label41 = self.SigmoidSVM(train_feature.values,train_label1.values,test_feature.values)

        train_label2 = self.preprocessing(train_label2,'versicolor')
        predicted_label12 = self.LinearSVM(train_feature.values,train_label2.values,test_feature.values)
        predicted_label22 = self.PolySVM(train_feature.values,train_label2.values,test_feature.values)
        predicted_label32 = self.RbfSVM(train_feature.values,train_label2.values,test_feature.values)
        predicted_label42 = self.SigmoidSVM(train_feature.values,train_label2.values,test_feature.values)

        train_label3 = self.preprocessing(train_label3,'virginica')
        predicted_label13 = self.LinearSVM(train_feature.values,train_label3.values,test_feature.values)
        predicted_label23 = self.PolySVM(train_feature.values,train_label3.values,test_feature.values)
        predicted_label33 = self.RbfSVM(train_feature.values,train_label3.values,test_feature.values)
        predicted_label43 = self.SigmoidSVM(train_feature.values,train_label3.values,test_feature.values)

        predicted_label1 = np.column_stack((predicted_label11,predicted_label12,predicted_label13))
        predicted_label2 = np.column_stack((predicted_label21,predicted_label22,predicted_label23))
        predicted_label3 = np.column_stack((predicted_label31,predicted_label32,predicted_label33))
        predicted_label4 = np.column_stack((predicted_label41,predicted_label42,predicted_label43))
        
        index1 = np.argmax(predicted_label1,axis=1)
        index2 = np.argmax(predicted_label2,axis=1)
        index3 = np.argmax(predicted_label3,axis=1)
        index4 = np.argmax(predicted_label4,axis=1)

        accuracy1 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == index1[i]):
                accuracy1 += 1
        accuracy1 /= len(test_label)
        
        accuracy2 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == index2[i]):
                accuracy2 += 1
        accuracy2 /= len(test_label)
        
        accuracy3 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == index3[i]):
                accuracy3 += 1
        accuracy3 /= len(test_label)
        
        accuracy4 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == index4[i]):
                accuracy4 += 1
        accuracy4 /= len(test_label)

        return accuracy1 , accuracy2 , accuracy3 , accuracy4

    def cross_validation(self):
        data = pd.read_csv(path + '\\iris.csv')

        accuracy1_sum = accuracy2_sum = accuracy3_sum = accuracy4_sum = 0
        idx = list(range(149))
        np.random.shuffle(idx)
        for k in[0,29,58,87,116]:
            train1 = data.iloc[idx[:k],:]
            train2 = data.iloc[idx[k+29:],:]
            train = np.row_stack((train1,train2))
            
            train_feature = train[:,:4]
            train_feature = pd.DataFrame(train_feature)
            train_feature = train_feature.reset_index(drop=True)
            
            train_label = train[:,4]
            train_label = pd.DataFrame(train_label)
            train_label = train_label.reset_index(drop=True)
            
            test_feature = data.iloc[idx[k:k+29],:4]
            test_feature = pd.DataFrame(test_feature)
            test_feature = test_feature.reset_index(drop=True)
            test_label = data.iloc[idx[k:k+29],4]
            test_label = pd.DataFrame(test_label)
            test_label = test_label.reset_index(drop=True)

            accuracy1 , accuracy2 , accuracy3 , accuracy4 = \
            self.assess(train_feature,train_label,test_feature,test_label)

            accuracy1_sum += accuracy1
            accuracy2_sum += accuracy2
            accuracy3_sum += accuracy3
            accuracy4_sum += accuracy4
        accuracy1_sum /= 5
        accuracy2_sum /= 5
        accuracy3_sum /= 5
        accuracy4_sum /= 5

        print('The accuracy of LinearMethod(cross validation):',accuracy1_sum)
        print('The accuracy of PolynomialMethod(cross validation):',accuracy2_sum)
        print('The accuracy of GaussianradialbasisMethod(cross validation):',accuracy3_sum)
        print('The accuracy of SigmoidMethod(cross validation):',accuracy4_sum)

if __name__ == '__main__':
    SVM1 = Iris_SVM()
    SVM1.cross_validation()



    

    
    