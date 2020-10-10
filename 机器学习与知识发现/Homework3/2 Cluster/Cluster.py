import math
import numpy as np
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))

    
def preprocessing(feature,label):
    
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
        if label.iloc[i] == '是':
            label.iloc[i] = 1
        else:
            label.iloc[i] = 0
            
    return new_feature , label

def dist_ave(C1,C2,feature):
    dist = 0
    for i in C1:
        for j in C2:
            dist += np.sqrt(np.sum(np.square(feature[i]-feature[j])))
    dist = dist / (len(C1)*len(C2))
    return dist

# 这是一个使用全图来构建W矩阵的Ncut计算方法
# def dist_ncut(C1,C2,feature):
#     dist = 0
#     sigma = 1.0

#     n , m = feature.shape
#     W = np.zeros((n,n))
#     for i in range(n):
#         for j in range(n):
#             W[i][j] = np.exp(-(np.sqrt(np.sum(np.square(feature[i]-feature[j]))))/(2*sigma**2))
    
#     y1 = np.zeros((n,1))
#     y2 = np.zeros((n,1))
#     for i in C1:
#         y1[i] = 1
#     for j in C2:
#         y2[j] = 1
#     D = np.diag(np.sum(W,1))

#     CUT = np.dot(np.dot(y1.T,W),y2)
#     VOL1 = np.dot(np.dot(y1.T,D),y1)
#     VOL2 = np.dot(np.dot(y2.T,D),y2)
#     dist = CUT/VOL1 + CUT/VOL2

#     return dist

# 这是一个仅使用C1、C2来构建W矩阵的Ncut计算方法
def dist_ncut(C1,C2,feature):
    dist = 0
    sigma = 1.0

    n , m = feature.shape
    W = np.zeros((n,n))
    C = []
    C.extend(C1)
    C.extend(C2)
    for i in C:
        for j in C:
            W[i][j] = np.exp(-(np.sum(np.square(feature[i]-feature[j])))/(2*sigma**2))
    y1 = np.zeros((n,1))
    y2 = np.zeros((n,1))
    for i in C1:
        y1[i] = 1
    for j in C2:
        y2[j] = 1
    D = np.diag(np.sum(W,1))

    CUT = np.dot(np.dot(y1.T,W),y2)
    VOL1 = np.dot(np.dot(y1.T,D),y1)
    VOL2 = np.dot(np.dot(y2.T,D),y2)

    if len(C1) == 1:
        VOL1 = 1
    if len(C2) == 1:
        VOL2 = 1
    dist = CUT/VOL1 + CUT/VOL2
    return dist

def find_closest(C,M):
    min_dist = 100000
    i_ = j_ = -1
    m = len(C)
    for i in range(m):
        for j in range(m):
            if M[i,j] < min_dist and i != j:
                min_dist = M[i,j]
                i_ = i
                j_ = j

    return i_ , j_

def Cluster(feature, k, dist_func):
    n, m = feature.shape

    C = []
    for j in range(n):
        Cj = [j]
        C.append(Cj)
    
    M = np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            if dist_func == 'ave_elu':
                M[i,j] = dist_ave(C[i],C[j],feature)
            if dist_func == 'Ncut':
                M[i,j] = dist_ncut(C[i],C[j],feature)
            M[j,i] = M[i,j]
    
    
    q = n
    if dist_func == 'ave_elu':
        print('If using average Euclidean distance, the clustering process is as below:')
    if dist_func == 'Ncut':
        print('If using NCUT distance, the clustering process is as below:')
    while q > k :
        print('For ',q,'\'s cluster, the answer: ',)
        for ci in C:
            print(ci)
        i_, j_ = find_closest(C,M)
        C[i_].extend(C[j_])
        C.remove(C[j_])
        M = np.delete(M,j_,axis=0)
        M = np.delete(M,j_,axis=1)
        for j in range(q-1):
            if dist_func == 'ave_elu':
                M[i_,j] = dist_ave(C[i_],C[j],feature)
            if dist_func == 'Ncut':
                M[i_,j] = dist_ncut(C[i_],C[j],feature)
            M[j,i_] = M[i_,j]
        q -= 1

    print('\n\n\n')
    if dist_func == 'ave_elu':
        print('If using average Euclidean distance, the final clustering result is :')
    if dist_func == 'Ncut':
        print('If using NCUT distance, the final clustering result is :')
    print('For 2\'s cluster, the answer: ',)
    for ci in C:
        print(ci)
    print('\n\n\n')

if __name__ == '__main__':
    data = pd.read_csv(path+'/watermelon3.csv')
    idx = list(range(17))
    feature = data.iloc[:,:8]
    label = data.iloc[:,8]
    feature, label = preprocessing(feature,label)
    feature = np.array(feature)

    # 运行使用平均欧式距离的层级聚类
    Cluster(feature,2,'ave_elu')

    # 用sklearn包验证平均欧式距离的层级聚类结果
    # from sklearn.cluster import AgglomerativeClustering
    # clustering = AgglomerativeClustering(linkage='average')
    # cluster = clustering.fit(feature)
    # print(cluster.labels_)

    # 运行使用NCUT相似性度量的层级聚类
    Cluster(feature,2,'Ncut')




    

