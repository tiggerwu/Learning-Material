import math
import numpy as np
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class Iris_LOG(object):
    def _init_(self):
        self.w = None
        self.b = None

    
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
                    label.iloc[i,0] =2

        return label
    
    def sigmoid(self,w,x,b):
        return 1/(1 + math.exp(-(np.dot(w.transpose(),x)+b)))
        
    def train(self,train_feature,train_label):
        
        alpha = 0.002
        w = np.mat(np.zeros(4)).transpose()
        b = 0
        num = train_feature.shape[0]
        x_train = []
        
        for i in range(num):
            x_train.append(np.mat(train_feature.iloc[i,:],dtype=np.float64).transpose())
        
        
        n = 0
        while n < 300:
            delta_w = np.mat(np.zeros(4)).transpose()
            delta_b = 0
            for i in range(num):
                delta_w = delta_w + x_train[i]*train_label.iloc[i,0] - x_train[i]*self.sigmoid(w,x_train[i],b) 
                delta_b = delta_b + train_label.iloc[i,0] - self.sigmoid(w,x_train[i],b)
            delta_w = -delta_w
            delta_b = -delta_b
            n += 1
            
            if abs(self.sigmoid(w,x_train[0],b)-self.sigmoid(w - alpha*delta_w,x_train[0],b - alpha*delta_b))<math.exp(-16):
                break
            w = w - alpha * delta_w
            b = b - alpha * delta_b
            
        self.w = w
        self.b = b
        
        return None
    
    def test(self,test_feature):
        
        test_num = test_feature.shape[0]
        predicted_label = np.zeros(test_num)
        
        w = self.w
        b = self.b
        
        for i in range(test_num):
            sample = test_feature.iloc[i,:]
            sample_mat = np.mat(sample,dtype=np.float32).transpose()
            target = np.dot(w.transpose(),sample_mat)+b
            predicted_label[i] = target

        return predicted_label
    
    def assess(self,train_feature,train_label,test_feature,test_label):
        
        test_label = self.preprocessing(test_label,'all')

        train_label1 = train_label.copy()
        train_label2 = train_label.copy()
        train_label3 = train_label.copy()
        train_label1 = self.preprocessing(train_label1,'setosa')
        self.train(train_feature,train_label1)
        predicted_label1 = self.test(test_feature)

        train_label2 = self.preprocessing(train_label2,'versicolor')
        self.train(train_feature,train_label2)
        predicted_label2 = self.test(test_feature)

        train_label3 = self.preprocessing(train_label3,'virginica')
        self.train(train_feature,train_label3)
        predicted_label3 = self.test(test_feature)

        predicted_label = np.column_stack((predicted_label1,predicted_label2,predicted_label3))

        accuracy = 0
        
        index = np.argmax(predicted_label,axis=1)
        for i in range(len(test_label)):
            if (index[i] == test_label.iloc[i,0]):
                accuracy += 1
        accuracy /= len(test_label)
        
        return accuracy
        
    def cross_validation(self):
        data = pd.read_csv(path+'\\iris.csv')
        accuracy = 0
        
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
            
            accuracy_tmp = self.assess(train_feature,train_label,test_feature,test_label)
            accuracy += accuracy_tmp
            
        accuracy /= 5

        print('The accuracy for LOG(cross validation):', accuracy)
    
if __name__ == '__main__':
    LOG1 = Iris_LOG()
    LOG1.cross_validation()

