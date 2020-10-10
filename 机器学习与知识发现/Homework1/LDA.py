import math
import numpy as np
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class LDA(object):
    def _init_(self):
        self.w = None
        self.mean1 = 0
        self.mean0 = 0
    
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
        for dim in range(19):
            mean_posi.append(np.mean(positive[:,dim]))
            mean_nega.append(np.mean(negative[:,dim]))
        
        sw = sw1 = sw2 = np.zeros((19,19))
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
        w = np.linalg.pinv(sw)*((np.mat(mean_posi)-np.mat(mean_nega)).transpose())
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
            sample_mat = np.mat(sample).transpose()
            target = w.transpose() * sample_mat
            if abs(target-mean1) < abs(target-mean0):
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
        
#if __name__ == '__main__':
    def validation_80to20(self):
        data = pd.read_csv(path+'\\watermelon3.csv')
        
        accuracy_average = []
        for i in range(10):
            idx = list(range(17))
            np.random.shuffle(idx)

            train_feature = data.iloc[idx[:14],0:8]
            train_feature = train_feature.reset_index(drop=True)
            train_feature = pd.DataFrame(train_feature)
            train_label = data.iloc[idx[:14],8]
            train_label = train_label.reset_index(drop=True)
            train_label = pd.DataFrame(train_label)

            test_feature = data.iloc[idx[14:],0:8]
            test_feature = test_feature.reset_index(drop=True)
            test_feature = pd.DataFrame(test_feature)
            test_label = data.iloc[idx[14:],8]
            test_label = test_label.reset_index(drop=True)
            test_label = pd.DataFrame(test_label)

            accuracy = self.assess(train_feature,train_label,test_feature,test_label)
            accuracy_average.append(accuracy)

        print('The accuracy for LDA(80% to 20% validation):' , np.mean(accuracy_average))

    def cross_validation(self):
        data = pd.read_csv(path+'\\watermelon3.csv')
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

        print('The accuracy for LDA(cross validation):', accuracy)
    
if __name__ == '__main__':
    LDA1 = LDA()

    LDA1.cross_validation()
    LDA1.validation_80to20()
