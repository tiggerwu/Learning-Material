import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import sys,os
import torch
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# 加载入数据
def load():
    data = sio.loadmat(path+'/iris.mat')
    sample = data['samples']
    label = data['labels']

    return sample,label

# 预处理，打乱顺序，归一化，分割训练集和测试集
def preprocess(sample,label):
    
    #计算均值、标准差，将数据归一化（Normalize）
    std = np.std(sample)
    std = np.std(sample)
    mean = np.mean(sample)
    sample = (sample - mean)/std 

    #打乱数据的顺序（shuffle）
    idx = list(range(sample.shape[0]))
    np.random.shuffle(idx)
    sample = sample[idx]
    label = label[idx]
    
    #分割数据集（80%为训练集，20%为测试集）（split the datum）
    split = int(sample.shape[0] * 0.8)
    train_sample = sample[:split]
    train_label = label[:split]
    test_sample = sample[split:]
    test_label = label[split:]

    return train_sample,train_label,test_sample,test_label

#Sigmoid非线性激活函数
def Sigmoid(x):
    return 1/(1+np.exp(-x))

#定义三层神经网络
class BP_network(object):
    def __init__(self,input_dim,hidden_num,output_dim,sample_num):
        #三层神经网络共两组参数
        self.w1 = np.random.rand(hidden_num,input_dim)
        self.b1 = np.random.rand(hidden_num,sample_num)
        self.w2 = np.random.rand(output_dim,hidden_num)
        self.b2 = np.random.rand(output_dim,sample_num)
    
    def activation(self,x):
        return Sigmoid(x)

#BP训练算法的实现
def train(train_sample,train_label):
    #通过训练样本和标记，获得样本向量维数d，隐含神经元个数h，输出单热向量编码c类
    train_sample_num , sample_dim = train_sample.shape
    _ , label_dim = train_label.shape
    hidden_num = 10
    d = sample_dim
    h = hidden_num
    c = label_dim
    #设置迭代次数、一个batch的样本数和梯度下降的学习率
    epoches = 3000
    batch_size = 1
    alpha = 0.001
    iteration = int(train_sample_num/batch_size)
    #实例化模型
    model = BP_network(d,h,c,batch_size)
    #创建保存精度和损失的列表
    loss_list_train = []
    acc_list_train = []
    #创建保存精度和损失的列表
    loss_list_test = []
    acc_list_test = []
    #开始训练
    for epoch in range(epoches):
        loss_epoch = 0
        true_num = 0
        for iter in range(iteration):
            sample_iter = train_sample[iter*batch_size:(iter+1)*batch_size]
            label_iter = train_label[iter*batch_size:(iter+1)*batch_size]
            #前向传播的过程，其中隐含层采用Sigmoid激活函数，输入和输出层都是线性激活函数
            x = np.mat(sample_iter).T
            y = np.mat(label_iter).T
            z1 = np.dot(model.w1,x) + model.b1
            a1 = model.activation(z1)
            z2 = np.dot(model.w2,a1) + model.b2
            y_ = z2
            #计算预测正确的样本数
            for i in range(batch_size):
                index = int(y_[:,i].argmax())
                if y[index,i] == 1.0:
                    true_num += 1
            #计算一次迭代的总损失，采用均方误差函数
            for i in range(batch_size):
                loss_per_sample = 0
                for j in range(label_dim):
                    loss_per_sample += 1/2*(y_[j,i]-y[j,i])**2
                loss_epoch += loss_per_sample

            #Back-propagation反向传播
            delta_y_ = y_ - y
            delta_w2 = np.dot(delta_y_,a1.T)
            delta_b2 = delta_y_
            delta_a1 = np.dot(model.w2.T, delta_y_)
            delta_z1 = delta_a1 * (a1.T * (1 -a1))
            delta_w1 = np.dot(delta_z1 , x.T)
            delta_b1 = delta_z1
            #梯度下降
            model.w1 = model.w1 - alpha * delta_w1
            model.b1 = model.b1 - alpha * delta_b1
            model.w2 = model.w2 - alpha * delta_w2
            model.b2 = model.b2 - alpha * delta_b2
        #一次迭代结束后，计算精度和损失，并添加到列表中
        acc_list_train.append(true_num/train_sample_num)
        print("The accuracy for epoch(training)",epoch," is : ",true_num/train_sample_num)
        loss_list_train.append(loss_epoch/train_sample_num)
        print("The loss for epoch(training)",epoch," is : ",loss_epoch/train_sample_num)

        ave_acc , ave_loss = test(model,test_sample,test_label,batch_size)
        acc_list_test.append(ave_acc)
        print("The accuracy for epoch(testing) ",epoch,"is : ",ave_acc)
        loss_list_test.append(ave_loss)
        print("The loss for epoch(testing) ",epoch,"is : ",ave_loss)
        
        #当精度达到要求了之后，停止训练
        # if true_num/train_sample_num > 0.97 and ave_acc > 0.97:
        #     break
    #保存模型
    torch.save(model,path+'/model_3.pkl')

    return model , acc_list_train ,loss_list_train ,acc_list_test , loss_list_test

#训练结束后进行测试的过程
def test(model,test_sample,test_label,batch_size):
    #得到测试集样本数和标记的维数
    test_sample_num , _ = test_sample.shape
    _ , label_dim = test_label.shape
    iteration = int(test_sample_num/batch_size)
    #开始测试
    total_loss = 0
    true_num = 0
    for iter in range(iteration):
        sample_iter = test_sample[iter*batch_size:(iter+1)*batch_size]
        label_iter = test_label[iter*batch_size:(iter+1)*batch_size]
        #计算预测值
        x = np.mat(sample_iter).T
        y = np.mat(label_iter).T
        z1 = np.dot(model.w1,x) + model.b1
        a1 = model.activation(z1)
        z2 = np.dot(model.w2,a1) + model.b2
        y_ = z2
        #计算预测正确的样本数
        for i in range(batch_size):
            index = int(y_[:,i].argmax())
            if y[index,i] == 1.0:
                true_num += 1
        #计算迭代的总损失，采用均方误差函数
        for i in range(batch_size):
            loss_per_sample = 0
            for j in range(label_dim):
                loss_per_sample += 1/2*(y_[j,i]-y[j,i])**2
            total_loss += loss_per_sample
    #计算精度和损失，并返回
    ave_acc = true_num/test_sample_num
    ave_loss = total_loss/test_sample_num
    
    return ave_acc,ave_loss

#绘制精度和损失函数的图像
def plot_figure(loss_list_train,acc_list_train,loss_list_test,acc_list_test):
    _ , axis = plt.subplots(1,1)
    axis.plot(loss_list_train,label='train_loss',color='red')
    axis.plot(loss_list_test,label='test_loss',color='blue')
    axis.set_xlabel('epoches')
    axis.set_ylabel('loss')
    plt.legend()
    plt.show()

    _ , axis = plt.subplots(1,1)
    axis.plot(acc_list_train,label='train_accuracy',color='red')
    axis.plot(acc_list_test,label='test_accuracy',color='blue')
    axis.set_xlabel('epoches')
    axis.set_ylabel('accuracy')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    #载入样本和标签
    sample , label = load() 
    #预处理数据
    train_sample,train_label,test_sample,test_label\
        = preprocess(sample,label)
    #训练并测试
    model , acc_list_train , loss_list_train , acc_list_test , loss_list_test = train(train_sample,train_label)
    #绘制损失和精度曲线
    plot_figure(loss_list_train,acc_list_train,loss_list_test,acc_list_test)

    # #导入模型测试
    # model = torch.load(path+'/problem_3.pkl')
    # ave_acc , ave_loss = test(model,torch.Tensor(test_sample),torch.Tensor(test_label),batch_size=1)
    # print("The accuracy is : ",ave_acc)
    # print("The loss for is : ",ave_loss)