import math
import numpy as np
import pandas as pd
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class Iris_NBC(object):
    def _init_(self):
        self.prior = [0,0,0]
        self.mean = np.zero(4,3)
        self.std = np.zeros(4,3)

        
    def train(self,train_feature,train_label):
        
        train_set = np.column_stack((train_feature,train_label))
        
        #得到先验概率
        prior = [0,0,0]
        for i in train_label:
            if i == 'setosa':
                prior[0] += 1
            elif i == 'versicolor':
                prior[1] += 1
            else:
                prior[2] += 1
        prior[0] /= len(train_label)
        prior[1] /= len(train_label)
        prior[2] /= len(train_label)
        self.prior = prior
            
        #计算连续特征的类分布概率
        mean = np.zeros((4,3))
        std = np.zeros((4,3))
        mean[0,0] = np.mean(train_set[train_label == "setosa",0])
        mean[0,1] = np.mean(train_set[train_label == "versicolor",0])
        mean[0,2] = np.mean(train_set[train_label == "virginica",0])
        mean[1,0] = np.mean(train_set[train_label == "setosa",1])
        mean[1,1] = np.mean(train_set[train_label == "versicolor",1])
        mean[1,2] = np.mean(train_set[train_label == "virginica",1])
        mean[2,0] = np.mean(train_set[train_label == "setosa",2])
        mean[2,1] = np.mean(train_set[train_label == "versicolor",2])
        mean[2,2] = np.mean(train_set[train_label == "virginica",2])
        mean[3,0] = np.mean(train_set[train_label == "setosa",3])
        mean[3,1] = np.mean(train_set[train_label == "versicolor",3])
        mean[3,2] = np.mean(train_set[train_label == "virginica",3])
        std[0,0] = np.std(train_set[train_label == "setosa",0])
        std[0,1] = np.std(train_set[train_label == "versicolor",0])
        std[0,2] = np.std(train_set[train_label == "virginica",0])
        std[1,0] = np.std(train_set[train_label == "setosa",1])
        std[1,1] = np.std(train_set[train_label == "versicolor",1])
        std[1,2] = np.std(train_set[train_label == "virginica",1])
        std[2,0] = np.std(train_set[train_label == "setosa",2])
        std[2,1] = np.std(train_set[train_label == "versicolor",2])
        std[2,2] = np.std(train_set[train_label == "virginica",2])
        std[3,0] = np.std(train_set[train_label == "setosa",3])
        std[3,1] = np.std(train_set[train_label == "versicolor",3])
        std[3,2] = np.std(train_set[train_label == "virginica",3])
        
        self.mean = mean
        self.std = std
        
        return None
    
    def test(self,test_feature):
        
        test_num = test_feature.shape[0]
        predicted_label = np.zeros(test_num)
        
        prior = self.prior
        mean = self.mean
        std = self.std
        
        for i in range(test_num):
            sample = test_feature.iloc[i,:]
            pro = [prior[0],prior[1],prior[2]]
            
            for m in range(4):
                pro[0] *= 1/(math.sqrt(2*math.pi)*std[m,0])*math.exp(-((sample[m]-mean[m,0])**2)/(2*(std[m,0]**2)))
                pro[1] *= 1/(math.sqrt(2*math.pi)*std[m,1])*math.exp(-((sample[m]-mean[m,1])**2)/(2*(std[m,1]**2)))
                pro[2] *= 1/(math.sqrt(2*math.pi)*std[m,2])*math.exp(-((sample[m]-mean[m,2])**2)/(2*(std[m,2]**2)))
            
            if pro[0] >= pro[1] and pro[0] >= pro[2]:
                predicted_label[i] = 0
            elif pro[1] >= pro[0] and pro[1] >= pro[2]:
                predicted_label[i] = 1
            else:
                predicted_label[i] = 2
            
        return predicted_label
    
    def assess(self,train_feature,train_label,test_feature,test_label):
        
        self.train(train_feature,train_label)
        predicted_label = self.test(test_feature)
        
        accuracy = 0
        
        for i in range(len(test_label)):
            if (test_label[i] == "setosa" and predicted_label[i] == 0) or \
                (test_label[i] == "versicolor" and predicted_label[i] == 1) or \
                (test_label[i] == "virginica" and predicted_label[i] == 2):
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
            train_label = train[:,4]
            test_feature = data.iloc[idx[k:k+29],:4]
            test_label = data.iloc[idx[k:k+29],4]
            test_label = test_label.reset_index(drop=True)
            
            accuracy_tmp = self.assess(train_feature,train_label,test_feature,test_label)
            accuracy += accuracy_tmp
        accuracy /= 5

        print("The accuracy for NBC(cross validation):",accuracy)
        
if __name__ == '__main__':
    NBC1 = Iris_NBC()
    NBC1.cross_validation()

        