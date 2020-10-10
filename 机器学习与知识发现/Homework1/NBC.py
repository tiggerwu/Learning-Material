import math
import numpy as np
import pandas as pd
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class NBC(object):
    def _init_(self):
        self.prior = [0,0]
        self.mean = np.zero(2,2)
        self.std = np.zeros(2,2)
        self.pro_0 = []
        self.pro_1 = []
        
    def train(self,train_feature,train_label):
        
        train_set = np.column_stack((train_feature,train_label))
        
        #得到先验概率
        prior = [0,0]
        for i in train_label:
            if i == '是':
                prior[0] += 1
            else:
                prior[1] += 1
        prior[0] /= len(train_label)
        prior[1] /= len(train_label)
        
        self.prior = prior
        
        #计算离散特征的类分布概率
        positive = []
        negative = []
        for i in range(len(train_label)):
            if train_label[i] == '是':
                positive.append(train_set[i,:])
            else:
                negative.append(train_set[i,:])
        pro_0 = [{'浅白':0,'乌黑':0,'青绿':0},{'硬挺':0,'蜷缩':0,'稍蜷':0},{'清脆':0,'浊响':0,'沉闷':0},\
                 {'模糊':0,'清晰':0,'稍糊':0},{'平坦':0,'凹陷':0,'稍凹':0},{'硬滑':0,'软粘':0}]
        pro_1 = [{'浅白':0,'乌黑':0,'青绿':0},{'硬挺':0,'蜷缩':0,'稍蜷':0},{'清脆':0,'浊响':0,'沉闷':0},\
                 {'模糊':0,'清晰':0,'稍糊':0},{'平坦':0,'凹陷':0,'稍凹':0},{'硬滑':0,'软粘':0}]
        pro = [pro_0,pro_1]
        for dim in range(6):
            for num in range(len(positive)):
                pro_0[dim][positive[num][dim]] += 1
            for key in pro_0[dim].keys():
                pro_0[dim][key] /= len(positive)
        for dim in range(6):
            for num in range(len(negative)):
                pro_1[dim][negative[num][dim]] += 1
            for key in pro_1[dim].keys():
                pro_1[dim][key] /= len(negative)
        
        self.pro_0 = pro_0
        self.pro_1 = pro_1
            
        #计算连续特征的类分布概率
        mean = np.zeros((2,2))
        std = np.zeros((2,2))
        mean[0,0] = np.mean(train_set[train_label == "是",6])
        mean[0,1] = np.mean(train_set[train_label == "否",6])
        mean[1,0] = np.mean(train_set[train_label == "是",7])
        mean[1,1] = np.mean(train_set[train_label == "否",7])
        std[0,0] = np.std(train_set[train_label == "是",6])
        std[0,1] = np.std(train_set[train_label == "否",6])
        std[1,0] = np.std(train_set[train_label == "是",7])
        std[1,1] = np.std(train_set[train_label == "否",7])
        
        self.mean = mean
        self.std = std
        
        return None
    
    def test(self,test_feature):
        
        test_num = test_feature.shape[0]
        predicted_label = np.zeros(test_num)
        
        prior = self.prior
        mean = self.mean
        std = self.std
        pro_0 = self.pro_0
        pro_1 = self.pro_1
        
        for i in range(test_num):
            sample = test_feature.iloc[i,:]
            pro = [prior[0],prior[1]]
            
            for dim in range(6):
                pro[0] *= pro_0[dim][sample[dim]]
                pro[1] *= pro_1[dim][sample[dim]]
            pro[0] *= 1/(math.sqrt(2*math.pi)*std[0,0])*math.exp(-((sample[6]-mean[0,0])**2)/(2*(std[0,0]**2)))
            pro[0] *= 1/(math.sqrt(2*math.pi)*std[1,0])*math.exp(-((sample[7]-mean[1,0])**2)/(2*(std[1,0]**2)))
            pro[1] *= 1/(math.sqrt(2*math.pi)*std[0,1])*math.exp(-((sample[6]-mean[0,1])**2)/(2*(std[0,1]**2)))
            pro[1] *= 1/(math.sqrt(2*math.pi)*std[1,1])*math.exp(-((sample[7]-mean[1,1])**2)/(2*(std[1,1]**2)))
            
            if pro[0] >= pro[1]:
                predicted_label[i] = 0
            else:
                predicted_label[i] = 1
            
        return predicted_label
    
    def assess(self,train_feature,train_label,test_feature,test_label):
        
        self.train(train_feature,train_label)
        predicted_label = self.test(test_feature)
        
        accuracy = 0
        
        for i in range(len(test_label)):
            if (test_label[i] == '是' and predicted_label[i] == 0)or(test_label[i] == '否' and predicted_label[i] == 1):
                accuracy += 1
        accuracy /= len(test_label)
        
        return accuracy
        

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
            train_label = train[:,8]
            test_feature = data.iloc[idx[k:k+3],:8]
            test_label = data.iloc[idx[k:k+3],8]
            test_label = test_label.reset_index(drop=True)
            
            accuracy_tmp = self.assess(train_feature,train_label,test_feature,test_label)
            accuracy += accuracy_tmp
        accuracy /= 5

        print("The accuracy for NBC(cross validation):",accuracy)
        
if __name__ == '__main__':
    NBC1 = NBC()
    NBC1.cross_validation()

        