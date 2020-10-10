import math
import numpy as np
import pandas as pd
from sklearn import svm
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

class SVM(object):
    
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
        
    def LinearSVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=20, kernel='linear')
        svc.fit(train_feature,train_label.values.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def PolySVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=20, kernel='poly',degree=3)
        svc.fit(train_feature,train_label.values.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def RbfSVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=20, kernel='rbf',gamma=0.01)
        svc.fit(train_feature,train_label.values.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def SigmoidSVM(self,train_feature,train_label,test_feature):
        
        svc = svm.SVC(C=4, kernel='sigmoid')
        svc.fit(train_feature,train_label.values.ravel())
        predicted_label = svc.predict(test_feature)
        
        return predicted_label
    
    def assess(self,train_feature,train_label,test_feature,test_label):
        
        train_feature1,train_label1 = self.preprocessing(train_feature,train_label)
        train_feature1 = np.array(train_feature1)
        #train_label1 = np.array(train_label1)
        test_feature1,test_label1 = self.preprocessing(test_feature,test_label)
        test_feature1 = np.array(test_feature1)
        predicted_label1 = self.LinearSVM(train_feature1,train_label1,test_feature1)
        predicted_label2 = self.PolySVM(train_feature1,train_label1,test_feature1)
        predicted_label3 = self.RbfSVM(train_feature1,train_label1,test_feature1)
        predicted_label4 = self.SigmoidSVM(train_feature1,train_label1,test_feature1)
        
        accuracy1 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == predicted_label1[i]):
                accuracy1 += 1
        accuracy1 /= len(test_label)
        
        accuracy2 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == predicted_label2[i]):
                accuracy2 += 1
        accuracy2 /= len(test_label)
        
        accuracy3 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == predicted_label3[i]):
                accuracy3 += 1
        accuracy3 /= len(test_label)
        
        accuracy4 = 0
        for i in range(len(test_label)):
            if (test_label.iloc[i,0] == predicted_label4[i]):
                accuracy4 += 1
        accuracy4 /= len(test_label)

        return accuracy1 , accuracy2 , accuracy3 , accuracy4
        
    
    def validation_80to20(self):
        data = pd.read_csv(path+'\\watermelon3.csv')
        
        accuracy1_sum = accuracy2_sum = accuracy3_sum = accuracy4_sum = 0
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
            
            accuracy1 , accuracy2 , accuracy3 , accuracy4 = \
            self.assess(train_feature,train_label,test_feature,test_label)

            accuracy1_sum += accuracy1
            accuracy2_sum += accuracy2
            accuracy3_sum += accuracy3
            accuracy4_sum += accuracy4
        accuracy1_sum /= 10
        accuracy2_sum /= 10
        accuracy3_sum /= 10
        accuracy4_sum /= 10

        print('The accuracy of LinearMethod(80% to 20% validation):',accuracy1_sum)
        print('The accuracy of PolynomialMethod(80% to 20% validation):',accuracy2_sum)
        print('The accuracy of GaussianradialbasisMethod(80% to 20% validation):',accuracy3_sum)
        print('The accuracy of SigmoidMethod(80% to 20% validation):',accuracy4_sum)

    def cross_validation(self):
        data = pd.read_csv(path+'\\watermelon3.csv')

        accuracy1_sum = accuracy2_sum = accuracy3_sum = accuracy4_sum = 0
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
    SVM1 = SVM()

    SVM1.cross_validation()
    SVM1.validation_80to20()


    

    
    