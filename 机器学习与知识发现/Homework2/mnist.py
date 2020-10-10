import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import sys,os
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# 加载入数据
def load():
    data = sio.loadmat(path+'/mnist.mat')
    sample = data['fea']
    label = data['gnd']

    return sample,label

# 预处理，打乱顺序，归一化，分割训练集和测试集
def preprocess(sample,label):
    
    #计算均值、标准差，将数据归一化（Normalize）
    sample = sample/255.0
    std = np.std(sample)
    mean = np.mean(sample)
    sample = (sample - mean)/std 

    #打乱数据的顺序（shuffle）
    idx = list(range(sample.shape[0]))
    np.random.shuffle(idx)
    sample = sample[idx]
    label = label[idx]
    
    #分割数据集（前60000个为训练集，后10000个为测试集）（split the datum）
    train_sample = sample[:60000]
    train_label = label[:60000]
    test_sample = sample[60000:]
    test_label = label[60000:]

    return train_sample,train_label,test_sample,test_label

class my_net(nn.Module):
    def  __init__(self):
        super(my_net,self).__init__()
        #全连接层中隐藏层的神经元个数为hidden_num
        hidden_num = 1024
        #构建的神经网络为卷积层、池化层、卷积层、池化层、卷积层、池化层、全连接层、全连接层
        self.layer1 = nn.Sequential(nn.Conv2d(1,32,3),nn.BatchNorm2d(32),nn.ReLU(),nn.MaxPool2d(2,2))
        self.layer2 = nn.Sequential(nn.Conv2d(32,48,3),nn.BatchNorm2d(48),nn.ReLU(),nn.MaxPool2d(2,2),\
            nn.Conv2d(48,64,2),nn.BatchNorm2d(64),nn.ReLU(),nn.MaxPool2d(2,2))
        self.layer3 = nn.Sequential(nn.Linear(64*2*2,hidden_num),nn.BatchNorm1d(hidden_num),nn.ReLU())
        self.layer4 = nn.Sequential(nn.Linear(hidden_num,10),nn.Softmax())
        #指定损失函数和优化器
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.parameters(),lr=0.001)

    def forward(self,input_sample):
        tmp = self.layer1(input_sample)
        tmp = self.layer2(tmp)
        tmp = tmp.view(tmp.size(0),-1)
        tmp = self.layer3(tmp)
        output = self.layer4(tmp)

        return output

# 调用pytorch进行训练
def train_model(train_sample,train_label,test_sample,test_label):
    #得到训练集的样本数
    train_sample_num = train_sample.shape[0]
    #将样本和标记转化为合理的神经网络输入
    train_sample = train_sample.reshape(-1,1,28,28)
    test_sample = test_sample.reshape(-1,1,28,28)
    train_label = train_label.reshape(-1)
    test_label = test_label.reshape(-1)
    test_sample = torch.Tensor(test_sample)
    test_label = torch.Tensor(test_label)
    #实例化模型
    model = my_net()
    #指定迭代次数和batch size
    epoches = 100
    batch_size = 100
    iteration_train = int(train_sample_num/batch_size)
    #创建保存精度和损失的列表
    loss_list_train = []
    acc_list_train = []
    loss_list_test = []
    acc_list_test = []
    #开始训练，并每训练一代测试一次便于绘制精度和损失函数图像
    for epoch in range(epoches):
        loss_epoch = 0
        true_num = 0
        for iter in range(iteration_train):
            sample_iter = torch.Tensor(train_sample[iter*batch_size:(iter+1)*batch_size])
            label_iter = torch.Tensor(train_label[iter*batch_size:(iter+1)*batch_size])
            #label_iter = label_iter.reshape(-1)
            label_pre = model(sample_iter)
            #计算预测准确的样本数
            for i in range(batch_size):
                index = int(label_pre[i].argmax())
                if label_iter[i] == index:
                    true_num += 1
            #计算损失，模型优化
            loss = model.criterion(label_pre,label_iter.long())
            model.optimizer.zero_grad()
            loss.backward()
            model.optimizer.step()
            loss_epoch += loss.item()
        #一次迭代完成后，计算平均精度和平均损失，添加到列表中
        acc_list_train.append(true_num/train_sample_num)
        print("The accuracy for epoch(training)",epoch," is : ",true_num/train_sample_num)
        loss_list_train.append(loss_epoch/train_sample_num)
        print("The average loss for epoch(training)",epoch," is : ",loss_epoch/train_sample_num)

        #一次迭代完成后，测试模型，返回测试集的平均精度和平均损失，并添加到列表中

        ave_acc , ave_loss = test_model(model,test_sample,test_label)
        acc_list_test.append(ave_acc)
        loss_list_test.append(ave_loss)
        print("The accuracy for epoch(testing)",epoch," is : ",ave_acc)
        print("The average loss for epoch(testing)",epoch," is : ",ave_loss)

    torch.save(model,path+'/model_2.pkl')
        
    return loss_list_train,acc_list_train,loss_list_test,acc_list_test

def test_model(model,test_sample,test_label):
    batch_size = 100
    iteration_test = int(test_sample.shape[0]/batch_size)
    loss_epoch = 0
    true_num = 0
    for iter in range(iteration_test):
        sample_iter = torch.Tensor(test_sample[iter*batch_size:(iter+1)*batch_size])
        label_iter = torch.Tensor(test_label[iter*batch_size:(iter+1)*batch_size])
        label_pre = model(sample_iter)
        loss = model.criterion(label_pre,label_iter.long())
        loss_epoch += loss.item()
        #计算预测准确的样本数
        for i in range(batch_size):
            index = int(label_pre[i].argmax())
            if label_iter[i] == index:
                true_num += 1
    #计算平均精度和平均损失，并返回
    ave_acc = true_num/test_sample.shape[0]
    ave_loss = loss_epoch/test_sample.shape[0]

    return ave_acc,ave_loss

def plot_figure(loss_list_train,acc_list_train,loss_list_test,acc_list_test):
    _ , axis = plt.subplots(1,1)
    axis.plot(loss_list_train,label='train_loss',color='red')
    axis.plot(loss_list_test,label='test_loss',color='blue')
    axis.set_xlabel('epoches')
    axis.set_ylabel('loss')
    plt.show()

    _ , axis = plt.subplots(1,1)
    axis.plot(acc_list_train,label='train_accuracy',color='red')
    axis.plot(acc_list_test,label='test_accuracy',color='blue')
    axis.set_xlabel('epoches')
    axis.set_ylabel('accuracy')
    plt.show()


if __name__ == '__main__':
    #载入样本和标签
    sample , label = load() 
    #预处理数据
    train_sample,train_label,test_sample,test_label\
        = preprocess(sample,label)
    #训练并测试
    loss_list_train,acc_list_train,loss_list_test,acc_list_test = \
        train_model(train_sample,train_label,test_sample,test_label)
    #绘制损失和精度曲线
    plot_figure(loss_list_train,acc_list_train,loss_list_test,acc_list_test)

    # #导入模型测试
    # model2 = torch.load(path+'/problem_2.pkl')
    # ave_acc , ave_loss = test_model(model2,torch.Tensor(test_sample.reshape(-1,1,28,28)),torch.Tensor(test_label.reshape(-1)))
    # print("The accuracy is : ",ave_acc)
    # print("The loss for is : ",ave_loss)
