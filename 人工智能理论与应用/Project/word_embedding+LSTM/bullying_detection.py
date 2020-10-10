import numpy as np
import pandas as pd
import jieba
import keras
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense,Activation,Embedding,Bidirectional,\
    GRU,Flatten,Dropout,LSTM
from keras import regularizers
import sys,os
import random
path = os.path.abspath(os.path.dirname(sys.argv[0]))
from keras.utils import plot_model

def preprocess(data):
    
    #创建词频字典，并将数据集中的句子分词统计到其中
    WordFre = {}
    for i in range(data.shape[0]):
        content = data.ix[i,0]
        word_list = jieba.lcut(content)
        for word in word_list:
            if word not in WordFre.keys():
                WordFre[word] = 1
            else:
                WordFre[word] += 1
    
    #给词频字典中的每个键赋索引值
    WordIdx = {}
    index = 0
    threshold = 5
    for word in WordFre.keys():
        if WordFre[word] > threshold:
            WordIdx[word] = index
            index += 1
    WordIdx['lowfre'] = index
    WordIdx['empty'] = index + 1

    return WordIdx

def Model(input_dim):
    model = keras.models.Sequential()
    model.add(Embedding(input_dim = input_dim,output_dim = 50,\
        mask_zero=True)) 
    model.add(Bidirectional(LSTM(64,return_sequences=False,dropout=0.4)))
    model.add(Dense(units=32,activation='relu',kernel_regularizer=\
        regularizers.l2(0.01)))
    model.add(Dropout(0.2,noise_shape=None,seed=None))
    model.add(Dense(units=16,activation='relu',kernel_regularizer=\
        regularizers.l2(0.01)))
    model.add(Dense(units=1,activation='sigmoid'))

    model.compile(optimizer='adam',loss='binary_crossentropy',\
        metrics=['binary_accuracy'],)

    return model

def train(data,model,WordIdx):
    
    #计算字符串的最大长度
    max_len = 0
    for i in range(data.shape[0]):
        content = data.ix[i,0]
        word_list = jieba.lcut(content)
        if len(word_list) > max_len:
            max_len = len(word_list)
    
    #将字符串转换为向量
    Train_Data = []
    Train_Label = []
    for i in range(data.shape[0]):
        content = data.ix[i,0]
        word_list = jieba.lcut(content)
        word_mat = []
        for word in word_list:
            if word in WordIdx.keys():
                word_mat.append(WordIdx[word])
            else:
                word_mat.append(WordIdx['lowfre'])
        while len(word_mat) < max_len:
            word_mat.append(WordIdx['empty'])
        
        Train_Data.append(np.array(word_mat))
        Train_Label.append(data.ix[i,1])
    
    #分割数据集
    split = 0.8
    train_num = int(len(Train_Data)*split)
    Train_x = Train_Data[0:train_num]
    Train_y = Train_Label[0:train_num]
    Test_x = Train_Data[train_num:]
    Test_y = Train_Label[train_num:]

    #训练的过程
    model.fit(np.asarray(Train_x),np.asarray(Train_y),\
        batch_size=200,epochs=5,validation_split=0.05)
    model.save(path+'/model.h5')

    loss, acc = model.evaluate(np.asarray(Test_x),np.asarray(Test_y))
    print("model's loss:",loss,"    model's accuracy:",acc)


def predict(model,text,WordIdx):
    word_list = jieba.lcut(text)
    word_mat = []
    for word in word_list:
        if word in WordIdx.keys():
            word_mat.append(WordIdx[word])
        else:
            word_mat.append(WordIdx['lowfre'])
    word_mat = np.array(word_mat)
    
    res = model.predict(np.asarray(word_mat))
    if(res[0][0]) > 0.5:
        print(text,":bullying",res[0][0])
    else:
        print(text,":not bullying",res[0][0])



if __name__ == '__main__':

    data = pd.read_csv(path+"/total_dataset_shuffle.csv")
    WordIdx = preprocess(data) 
    model = Model(len(WordIdx)+1)
    train(data,model,WordIdx)

    #plot_model(model, to_file=path + 'model.png')





