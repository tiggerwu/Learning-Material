import math
import numpy as np
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class Iris_LDA(object):
    def _init_(self):
        self.w = None
        self.mean1 = 0
        self.mean0 = 0
    
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
        
    def train(self,train_feature,train_label):
        
        sample_num = len(train_label)
        idx_posi = []
        idx_nega = []

        for i in range(sample_num):
            if train_label.iloc[i,0] == 1:
                idx_posi.append(i)
            else:
                idx_nega.append(i)

        positive = train_feature.iloc[idx_posi,:]
        negative = train_feature.iloc[idx_nega,:]
        
        positive = np.array(positive)
        negative = np.array(negative)
        
        mean_posi = []
        mean_nega = []
        for dim in range(4):
            mean_posi.append(np.mean(positive[:,dim]))
            mean_nega.append(np.mean(negative[:,dim]))
        
        sw = sw1 = sw2 = np.zeros((4,4))
        for i in range(np.shape(positive)[0]):
            D_value = positive[i,:] - mean_posi
            D_value = np.mat(D_value)
            sw1 = sw1 + D_value.transpose()*D_value
        sw1 /= np.shape(positive)[0]
        
        for i in range(np.shape(negative)[0]):
            D_value = negative[i,:] - mean_nega
            D_value = np.mat(D_value)
            sw2 = sw2 + D_value.transpose()*D_value
        sw2 /= np.shape(negative)[0]
        
        sw = sw1 + sw2
        sw = np.array(sw,dtype = 'float')
        w = np.linalg.inv(sw)*((np.mat(mean_posi)-np.mat(mean_nega)).transpose())
        self.w = w
        
        mean1 = w.transpose() * np.mat(mean_posi).transpose()
        mean0 = w.transpose() * np.mat(mean_nega).transpose()
        self.mean1 = mean1
        self.mean0 = mean0
        
        return None
    
    def test(self,test_feature):
        
        test_num = test_feature.shape[0]
        predicted_label = np.zeros(test_num)
        
        
        w = self.w
        mean1 = self.mean1
        mean0 = self.mean0
        
        for i in range(test_num):
            sample = test_feature.iloc[i,:]
            sample_mat = np.mat(sample,dtype=np.float32).transpose()
            target = w.transpose() * sample_mat
            possbility = abs(target-mean0)/(abs(target-mean1) + abs(target-mean0))
            predicted_label[i] = possbility 
            
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

        print('The accuracy for LDA(cross validation):', accuracy)
    
if __name__ == '__main__':
    LDA1 = Iris_LDA()
    LDA1.cross_validation()
