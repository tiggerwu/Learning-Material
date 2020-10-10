import math
import numpy as np
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class LOG(object):
    def _init_(self):
        self.w = None
        self.b = None

    
    def preprocessing(self,feature,label):
        
        feature.rename(columns={'色泽':0, '根蒂':1, '敲声':2 ,'纹理':3 ,'脐部':4 , '触感':5 ,'密度':6 ,'含糖率':7}, inplace = True)
        new_feature = pd.DataFrame(np.zeros((len(label),19)))
        for i in range(len(label)):
            for dim in range(6):
                if feature.iloc[i,dim] == '浅白':
                    new_feature.set_value(i,0,1)
                if feature.iloc[i,dim] == '乌黑':
                    new_feature.set_value(i,1,1)
                if feature.iloc[i,dim] == '青绿':
                    new_feature.set_value(i,2,1)
                if feature.iloc[i,dim] == '硬挺':
                    new_feature.set_value(i,3,1)
                if feature.iloc[i,dim] == '蜷缩':
                    new_feature.set_value(i,4,1)
                if feature.iloc[i,dim] == '稍蜷':
                    new_feature.set_value(i,5,1)
                if feature.iloc[i,dim] == '清脆':
                    new_feature.set_value(i,6,1)
                if feature.iloc[i,dim] == '浊响':
                    new_feature.set_value(i,7,1)
                if feature.iloc[i,dim] == '沉闷':
                    new_feature.set_value(i,8,1)
                if feature.iloc[i,dim] == '模糊':
                    new_feature.set_value(i,9,1)
                if feature.iloc[i,dim] == '清晰':
                    new_feature.set_value(i,10,1)
                if feature.iloc[i,dim] == '稍糊':
                    new_feature.set_value(i,11,1)
                if feature.iloc[i,dim] == '平坦':
                    new_feature.set_value(i,12,1)
                if feature.iloc[i,dim] == '凹陷':
                    new_feature.set_value(i,13,1)
                if feature.iloc[i,dim] == '稍凹':
                    new_feature.set_value(i,14,1)
                if feature.iloc[i,dim] == '硬滑':
                    new_feature.set_value(i,15,1)
                if feature.iloc[i,dim] == '软粘':
                    new_feature.set_value(i,16,1)
            for dim in [6,7]:
                new_feature.set_value(i,dim+11,feature.iloc[i,dim])

        for i in range(len(label)):
            if label.iloc[i,0] == '是':
                label.iloc[i,0] = 1
            else:
                label.iloc[i,0] = 0
                
        return new_feature , label
    
    def sigmoid(self,w,x,b):
        return 1/(1 + math.exp(-(np.dot(w.transpose(),x)+b)))
        
    def train(self,train_feature,train_label):
        
        alpha = 0.002
        w = np.mat(np.zeros(19)).transpose()
        b = 0
        num = train_feature.shape[0]
        x_train = []
        
        for i in range(num):
            x_train.append(np.mat(train_feature.iloc[i,:]).transpose())
        
        
        n = 0
        while n < 300:
            delta_w = np.mat(np.zeros(19)).transpose()
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
            sample_mat = np.mat(sample).transpose()
            target = self.sigmoid(w,sample_mat,b)
            if target > 0.5:
                predicted_label[i] = 1
            else:
                predicted_label[i] = 0

            
        return predicted_label
    
    def assess(self,train_feature,train_label,test_feature,test_label):
        
        train_feature1,train_label1 = self.preprocessing(train_feature,train_label)
        self.train(train_feature1,train_label1)
        test_feature1,test_label1 = self.preprocessing(test_feature,test_label)
        predicted_label = self.test(test_feature1)

        accuracy = 0
        
        for i in range(len(test_label1)):
            if (test_label.iloc[i,0] == predicted_label[i]):
                accuracy += 1
        accuracy /= len(test_label)
        
        return accuracy
        
    def cross_validation(self):
        data = pd.read_csv(path+'/watermelon3.csv')
        accuracy = 0
        
        idx = list(range(17))
        np.random.shuffle(idx)
        for k in[0,3,6,9,12]:
            train1 = data.iloc[idx[:k],:]
            train2 = data.iloc[idx[k+3:],:]
            train = np.row_stack((train1,train2))
            
            train_feature = train[:,:8]
            train_feature = pd.DataFrame(train_feature)
            train_feature = train_feature.reset_index(drop=True)
            
            train_label = train[:,8]
            train_label = pd.DataFrame(train_label)
            train_label = train_label.reset_index(drop=True)
            
            test_feature = data.iloc[idx[k:k+3],:8]
            test_feature = pd.DataFrame(test_feature)
            test_feature = test_feature.reset_index(drop=True)
            test_label = data.iloc[idx[k:k+3],8]
            test_label = pd.DataFrame(test_label)
            test_label = test_label.reset_index(drop=True)
            
            accuracy_tmp = self.assess(train_feature,train_label,test_feature,test_label)
            accuracy += accuracy_tmp
            
        accuracy /= 5

        print('The accuracy for LOG(cross validation):', accuracy)
    
if __name__ == '__main__':
    LOG1 = LOG()
    LOG1.cross_validation()

