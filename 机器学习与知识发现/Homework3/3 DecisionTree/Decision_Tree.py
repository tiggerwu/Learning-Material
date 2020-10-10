import math
import numpy as np
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

    
def preprocessing(feature,label):
    
    new_feature = feature.iloc[:,:6]

    for i in range(len(label)):
        if label[i] == '否':
            label[i] = 0
        else:
            label[i] = 1
            
    return new_feature , label

def MajorityCount(label):
    label_list = list(label)
    dic = {}
    for l in set(label_list):
        ct = label_list.count(l)
        dic[l] = ct
    max_label = max(dic,key=dic.get)
    return max_label

def Ent(feature,label):
    label_list = list(label)
    ent = 0.0
    dic = {}
    for l in set(label_list):
        ct = label_list.count(l)
        dic[l] = ct
    for l in set(label_list):
        pk = float(dic[l])/float(len(label_list)) 
        ent -= pk * np.log2(pk)
    return ent

def CalcGainRatio(feature,label,a):
    Gain = 0.0
    IV = 0.0
    Gain += Ent(feature,label)

    values = feature.loc[:,a]
    values = set(values)
    for value in values:
        subfeature, sublabel = GetSubData(feature,label,a,value)
        pro = float(len(subfeature))/float(len(feature))
        Gain -= pro * Ent(subfeature,sublabel)
        IV -= pro * np.log2(pro)
    if IV == 0 and Gain == 0:
        Gain_ratio = 0.0
    else:
        Gain_ratio = Gain / IV
    return Gain_ratio

def ChooseFeature(feature,label,attr):
    max_Gain_ratio = -1
    best_attr = None
    for a in attr:
        Gain_ratio = CalcGainRatio(feature,label,a)
        if Gain_ratio > max_Gain_ratio:
            max_Gain_ratio = Gain_ratio
            best_attr = a
    return  best_attr

def GetSubData(feature,label,a,value):
    idx = feature[a].isin([value])
    new_feature = feature[idx]
    new_label = label[idx]
    return new_feature, new_label

def CreateTree(feature,label,attr):
    label_tmp = list(label)
    feature_copy = feature.copy()
    if len(set(label_tmp)) == 1:
        return label_tmp[0]
    if len(attr) == 0 or len(feature_copy.drop_duplicates(subset=list(attr))) == 1:
        return MajorityCount(label)
    
    a_ = ChooseFeature(feature,label,attr)
    Tree = {a_:{}}
    attr.remove(a_)
    attr_dic = {'色泽':['青绿', '乌黑', '浅白'], '根蒂':['蜷缩', '稍蜷', '硬挺'], '敲声':['浊响', '沉闷', '清脆'], \
        '纹理':['清晰', '稍糊', '模糊'], '脐部':['凹陷', '稍凹', '平坦'], '触感':['硬滑', '软粘']}
    values = attr_dic[a_]

    for value in values:
        sub_feature, sub_label = GetSubData(feature,label,a_,value) 
        if sub_feature.empty:
            Tree[a_][value] = MajorityCount(label)
            continue
        Tree[a_][value] = CreateTree(sub_feature,sub_label,attr)

    return Tree

def SingleJudge(single_feature,DecisionTree):
    a = list(DecisionTree.keys())[0]
    dic = DecisionTree[a]
    value = single_feature.loc[a]
    SubTree = dic[value]
    if type(SubTree).__name__ == 'dict':
        label = SingleJudge(single_feature,SubTree)
    else:
        label = SubTree
    return label

def Judge(test_feature,DecisionTree):
    predict_label = np.zeros(len(test_feature))
    for i in range(len(test_feature)):
        single_feature = test_feature.iloc[i]
        single_label = SingleJudge(single_feature,DecisionTree)
        predict_label[i] = single_label
    return predict_label
    

def get_data():
    data = pd.read_csv(path+'/watermelon3.csv')
    n, m = data.shape
    idx = list(range(n))
    np.random.shuffle(idx)

    train_feature = data.iloc[idx[:int(n*0.7)],0:6]
    train_feature = train_feature.reset_index(drop=True)
    train_label = data.iloc[idx[:int(n*0.7)],8]
    train_label = train_label.reset_index(drop=True)
    train_label = np.array(train_label)

    test_feature = data.iloc[idx[int(n*0.7):],0:6]
    test_feature = test_feature.reset_index(drop=True)
    test_label = data.iloc[idx[int(n*0.7):],8]
    test_label = test_label.reset_index(drop=True)
    test_label = np.array(test_label)
    train_feature, train_label = \
        preprocessing(train_feature, train_label)
    test_feature, test_label = \
        preprocessing(test_feature, test_label)

    return train_feature, train_label, test_feature, test_label

if __name__ == '__main__':
    accuracy_list = []
    for i in range(10):
        train_feature, train_label, test_feature, test_label = \
            get_data()
        # print(train_feature)
        # print(train_label)
        # print(test_feature)
        # print(test_label)
        attribution = set(['色泽', '根蒂', '敲声', '纹理', '脐部', '触感'])
        DecisionTree = CreateTree(train_feature,train_label,attribution)
        print('The Decision Tree is : ',DecisionTree)
        predicted_label = Judge(test_feature,DecisionTree)
        accuracy = 0
        for i in range(len(test_label)):
            if (test_label[i] == predicted_label[i]):
                accuracy += 1
        accuracy /= len(test_label)
        accuracy_list.append(accuracy)
        print('The accuracy is : ',accuracy, '\n')

    print('The average accuracy is : ',np.mean(accuracy_list))



    

