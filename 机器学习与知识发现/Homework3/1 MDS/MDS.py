import numpy as np
import pandas as pd
import sklearn.manifold as manifold
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys,os
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# 加载入数据
def load():
    data = pd.read_csv(path+'/mnist_train.csv',names=range(785))
    data1 = data[data[0] == 1]
    data2 = data[data[0] == 2]
    data12 = pd.concat([data1,data2],axis=0)
    data12 = data12.sample(frac=1).reset_index(drop=True)
    sample = data12.iloc[:,1:]/255.0
    label = data12.iloc[:,0]
    sample = np.array(sample)
    label = np.array(label)

    return sample,label

def calculate_dis(sample):
    n, m = sample.shape
    Dij = np.zeros((n,n)) 
    for i in range(n):
        for j in range(n):
            Dij[i][j] = np.sum(np.square(sample[i,:] - sample[j,:]))
    return Dij

def MDS(sample,dim):
    n, m = sample.shape
    Dij = calculate_dis(sample)
    
    Di = np.sum(Dij,axis=1,keepdims=True)
    Dj = np.sum(Dij,axis=0,keepdims=True)
    D = np.ones((n,n)) * np.sum(Dij)

    Bij = 1/2 * (Di/n + Dj/n - Dij - D/n**2)

    eval , evec = np.linalg.eig(Bij)
    ind = np.argsort(eval)
    ind = ind.astype(np.int32)
    ind_select = ind[-dim:]
    V = evec[:,ind_select]
    A_ = eval[ind_select].real
    A = np.diag(A_)
    Output = np.dot(V,A**(0.5))
    return Output


if __name__ == '__main__':
    # 载入样本和标签
    sample , label = load() 
    # 使用MDS降成二维并画图
    output1 = MDS(sample[:3000,:],2)
    plt.scatter(output1[:,0],output1[:,1],c=label[:3000])
    plt.show()
    # 使用MDS降成三维并画图
    output2 = MDS(sample[:3000,:],3)
    sample1 = np.array(output2[label[:3000]==1,:].real)
    sample2 = np.array(output2[label[:3000]==2,:].real)
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(sample1[:,0],sample1[:,1],sample1[:,2],label='1')
    ax.scatter(sample2[:,0],sample2[:,1],sample2[:,2],label='2')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.legend()
    plt.show()

    # 调用sklearn包验证降维结果
    # output3 = manifold.MDS(n_components=2).fit_transform(sample[:300,:])
    # plt.scatter(output3[:,0],output3[:,1],c=label[:300])
    # plt.show()
    # output4 = manifold.MDS(n_components=3).fit_transform(sample[:300,:])
    # plt.scatter(output4[:,0],output4[:,1],output4[:,2],c=label[:300])
    # plt.show()