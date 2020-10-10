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
    data = sio.loadmat(path+'/iris.mat')
    sample = data['samples']
    label = data['labels']

    return sample,label

# 预处理，打乱顺序，归一化，分割训练集和测试集
def preprocess(sample,label):
    
    #计算均值、标准差，将数据归一化（Normalize）
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

class three_layers_net(nn.Module):
    def  __init__(self,input_dim,output_dim,activation):
        super(three_layers_net,self).__init__()
        
        #隐藏层的神经元数
        hidden_num = 50

        #四种不同激活函数的影响
        if activation == 'ReLU':
            self.layer1 = nn.Sequential(nn.Linear(input_dim,hidden_num),nn.ReLU())
        elif activation == 'Sigmoid':
            self.layer1 = nn.Sequential(nn.Linear(input_dim,hidden_num),nn.Sigmoid())
        elif activation == 'Tanh':
            self.layer1 = nn.Sequential(nn.Linear(input_dim,hidden_num),nn.Tanh())
        elif activation == 'Softmax':
            self.layer1 = nn.Sequential(nn.Linear(input_dim,hidden_num),nn.Softmax())
        self.layer2 = nn.Sequential(nn.Linear(hidden_num,output_dim),nn.Softmax())

        #设置损失函数和优化器
        self.criterion = nn.MSELoss(size_average=False)
        self.optimizer = optim.SGD(self.parameters(),lr=0.015)

    def forward(self,input_sample):
        tmp = self.layer1(input_sample)
        output = self.layer2(tmp)

        return output

# 调用pytorch进行训练
def train_model(train_sample,train_label,test_sample,test_label,activation):
    #得到样本数、样本的维数、标记的维数
    sample_num,sample_dim = train_sample.shape
    _,label_dim = train_label.shape
    #转化为张量
    test_sample = torch.Tensor(test_sample)
    test_label = torch.Tensor(test_label)
    #实例化模型
    model = three_layers_net(sample_dim,label_dim,activation)
    #设置迭代次数500，batchsize为10,计算每次迭代的batch数
    epoches = 500
    batch_size = 10
    iteration = int(sample_num/batch_size)
    #创建保存精度和损失的列表
    loss_list_train = []
    acc_list_train = []
    loss_list_test = []
    acc_list_test = []
    #开始训练，并每训练一代测试一次便于绘制精度和损失函数图像
    for epoch in range(epoches):
        loss_epoch = 0
        true_num = 0
        for iter in range(iteration):
            sample_iter = torch.Tensor(train_sample[iter*batch_size:(iter+1)*batch_size])
            label_iter = torch.Tensor(train_label[iter*batch_size:(iter+1)*batch_size])
            label_pre = model(sample_iter)
            #计算预测准确的样本数
            for i in range(batch_size):
                index = int(label_pre[i].argmax())
                if label_iter[i,index] == 1.0:
                    true_num += 1
            #计算损失，模型优化
            loss = model.criterion(label_pre,label_iter)
            model.optimizer.zero_grad()
            loss.backward()
            model.optimizer.step()
            loss_epoch += loss.item()
        #一次迭代完成后，计算平均精度和平均损失，添加到列表中
        acc_list_train.append(true_num/sample_num)
        print("The accuracy for epoch(training)",epoch," is : ",true_num/sample_num)
        loss_list_train.append(loss_epoch/sample_num)
        print("The average loss for epoch(training)",epoch," is : ",loss_epoch/sample_num)
        
        #一次迭代完成后，测试模型，返回测试集的平均精度和平均损失，并添加到列表中
        ave_acc , ave_loss = test_model(model,test_sample,test_label)
        acc_list_test.append(ave_acc)
        loss_list_test.append(ave_loss)
        print("The accuracy for epoch(testing)",epoch," is : ",ave_acc)
        print("The total loss for epoch(testing)",epoch," is : ",ave_loss)
    
    #所有迭代完成后，保存模型
    torch.save(model,path+'/model_1_'+str(activation)+'.pkl')
        
    return loss_list_train,acc_list_train,loss_list_test,acc_list_test

def test_model(model,test_sample,test_label):
    label_pre = model(test_sample)
    #计算预测准确的样本数
    true_num = 0
    for i in range(test_sample.shape[0]):
        index = int(label_pre[i].argmax())
        if test_label[i,index] == 1.0:
            true_num += 1
    #计算平均精度和平均损失，并返回
    ave_acc = true_num/test_sample.shape[0]
    loss = model.criterion(label_pre,test_label)
    ave_loss = loss.item()/test_sample.shape[0]

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

#绘制精度和损失函数的图像,对比四种激活函数的影响
def plot_activation(acc_list,loss_list):
    _ , axis = plt.subplots(1,1)
    axis.plot(loss_list['ReLU'],label='ReLU',color='red')
    axis.plot(loss_list['Sigmoid'],label='Sigmoid',color='blue')
    axis.plot(loss_list['Tanh'],label='Tanh',color='yellow')
    axis.plot(loss_list['Softmax'],label='Softmax',color='green')
    axis.set_xlabel('epoches')
    axis.set_ylabel('loss')
    plt.legend()
    plt.show()

    _ , axis = plt.subplots(1,1)
    axis.plot(acc_list['ReLU'],label='ReLU',color='red')
    axis.plot(acc_list['Sigmoid'],label='Sigmoid',color='blue')
    axis.plot(acc_list['Tanh'],label='Tanh',color='yellow')
    axis.plot(acc_list['Softmax'],label='Softmax',color='green')
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

    #对每种不同的激活函数进行训练和测试，并绘制精度、损失函数图像
    acc_list = {}
    loss_list = {}
    for activation in ['ReLU','Sigmoid','Tanh','Softmax']:
        loss_list_train,acc_list_train,loss_list_test,acc_list_test = \
            train_model(train_sample,train_label,test_sample,test_label,activation)
        acc_list[activation] = acc_list_test
        loss_list[activation] = loss_list_test
        plot_figure(loss_list_train,acc_list_train,loss_list_test,acc_list_test)
    #对比绘制不同激活函数的精度曲线和损失曲线
    plot_activation(acc_list,loss_list)

    # #导入模型测试
    # for activation in ['ReLU','Sigmoid','Tanh','Softmax']:
    #     model = torch.load(path+'/problem_1_'+str(activation)+'.pkl')
    #     ave_acc , ave_loss = test_model(model,torch.Tensor(test_sample),torch.Tensor(test_label))
    #     print("The accuracy for ",activation," is : ",ave_acc)
    #     print("The loss for ",activation," is : ",ave_loss)

