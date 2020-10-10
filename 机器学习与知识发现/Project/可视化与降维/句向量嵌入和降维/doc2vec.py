#coding:utf-8
import jieba
import sys
import gensim
import sklearn
import numpy as np
import json
from gensim.models.doc2vec import Doc2Vec, LabeledSentence
TaggededDocument = gensim.models.doc2vec.TaggedDocument
import sys,os
path = os.path.abspath(os.path.dirname(sys.argv[0]))

#进行中文分词
def cut_files():
    filePath = path + '/hupu.txt'
    fr = open(filePath, 'r')
    fvideo = open(path + '/hupu_cut.txt', "w")
    for line in fr.readlines():
        line = line.rstrip('\n')
        line = line.rstrip('\t')
        line = line + '\n'
        curLine =' '.join(list(jieba.cut(line)))
        fvideo.writelines(str(curLine))

def cut_files_tieba():
    filePath = path + '/tieba.txt'
    fr = open(filePath, 'r')
    fvideo = open(path + '/tieba_cut.txt', "w")
    for line in fr.readlines():
        line = line.rstrip('\n')
        line = line.rstrip('\t')
        line = line + '\n'
        curLine =' '.join(list(jieba.cut(line)))
        fvideo.writelines(str(curLine))

def cut_files_zhihu():
    doc = json.load(open(path + '/zhihu.json','r'))
    filePath = path + '/zhihu.txt'
    fi = open(filePath,'w')
    for article in doc:
        sentence_list = article.split('。')
        for sentence in sentence_list:
            if(sentence!='\n'):
                fi.writelines(sentence)
    fi.close()
    filePath = path + '/zhihu.txt'
    fr = open(filePath, 'r')
    fvideo = open(path + '/zhihu_cut.txt', "w")
    for line in fr.readlines():
        if line!='\n':
            line = line.rstrip('\n')
            line = line.rstrip('\t')
            line = line + '\n'
            curLine =' '.join(list(jieba.cut(line)))
            fvideo.writelines(str(curLine))


def get_datasest(topic = None):
    if topic == 'hupu':
        with open(path + "/hupu_cut.txt", 'r') as cf:
            docs = cf.readlines()
            print (len(docs))
    if topic == 'zhihu':
        with open(path + "/zhihu_cut.txt", 'r') as cf:
            docs = cf.readlines()
            print (len(docs))
    if topic == 'tieba':
        with open(path + "/tieba_cut.txt", 'r') as cf:
            docs = cf.readlines()
            print (len(docs))
    if topic == None:
        with open(path + "/hupu_cut.txt", 'r') as cf:
            docs1 = cf.readlines()
        with open(path + "/zhihu_cut.txt", 'r') as cf:
            docs2 = cf.readlines()
        with open(path + "/tieba_cut.txt", 'r') as cf:
            docs3 = cf.readlines()
    
    if topic != None:
        x_train = []
        for i, text in enumerate(docs):
            word_list = text.split(' ')
            l = len(word_list)
            word_list[l - 1] = word_list[l - 1].strip()
            document = TaggededDocument(word_list, tags=[i])
            x_train.append(document)
    
    if topic == None:
        x_train = []
        for i, text in enumerate(docs1):
            word_list = text.split(' ')
            l = len(word_list)
            word_list[l - 1] = word_list[l - 1].strip()
            document = TaggededDocument(word_list, tags=[i])
            x_train.append(document)
            if i > 20000:
                break
        for i, text in enumerate(docs2):
            word_list = text.split(' ')
            l = len(word_list)
            word_list[l - 1] = word_list[l - 1].strip()
            document = TaggededDocument(word_list, tags=[i+20000])
            x_train.append(document)
            if i > 20000:
                break
        for i, text in enumerate(docs3):
            word_list = text.split(' ')
            l = len(word_list)
            word_list[l - 1] = word_list[l - 1].strip()
            document = TaggededDocument(word_list, tags=[i+40000])
            x_train.append(document)
            if i > 20000:
                break

    return x_train

#模型训练
# 原参数：size = 150 ，window = 5
def train(x_train, topic, size=1500, epoch_num=10):
    model_dm = Doc2Vec(x_train, min_count=1, window=10, size=size, sample=1e-3, negative=5, workers=4)
    model_dm.train(x_train, total_examples=model_dm.corpus_count, epochs=epoch_num)
    model_dm.save(path + '/model_doc2vec_' + str(topic))

    return model_dm

#实例
def test():
    model_dm_full = Doc2Vec.load(path + "/model_doc2vec_full")
    
    sentence_embed_hupu = []
    with open(path + "/hupu_cut.txt", 'r') as cf:
        docs = cf.readlines()
    count = 0
    for i, text in enumerate(docs):
        word_list = text.split(' ')
        l = len(word_list)
        word_list[l - 1] = word_list[l - 1].strip()
        inferred_vector_dm = model_dm_full.infer_vector(word_list)
        sentence_embed_hupu.append(inferred_vector_dm)
        count += 1
        if count > 1000:
            break

    sentence_embed_zhihu = []
    with open(path + "/zhihu_cut.txt", 'r') as cf:
        docs = cf.readlines()
    count = 0
    for i, text in enumerate(docs):
        word_list = text.split(' ')
        l = len(word_list)
        word_list[l - 1] = word_list[l - 1].strip()
        inferred_vector_dm = model_dm_full.infer_vector(word_list)
        sentence_embed_zhihu.append(inferred_vector_dm)
        count += 1
        if count > 1000:
            break
    
    sentence_embed_tieba = []
    with open(path + "/tieba_cut.txt", 'r') as cf:
        docs = cf.readlines()
    count = 0
    for i, text in enumerate(docs):
        word_list = text.split(' ')
        l = len(word_list)
        word_list[l - 1] = word_list[l - 1].strip()
        inferred_vector_dm = model_dm_full.infer_vector(word_list)
        sentence_embed_tieba.append(inferred_vector_dm)
        count += 1
        if count > 1000:
            break
    
    return sentence_embed_hupu,sentence_embed_zhihu,sentence_embed_tieba

def plot(sentence_embed1,sentence_embed2,sentence_embed3):
    from sklearn.manifold import TSNE
    import pandas as pd
    import matplotlib.pyplot as plt
    import preprocessing
    
    sentence_embed1 = np.array(sentence_embed1)
    sentence_embed1 = TSNE(n_components=2).fit_transform(sentence_embed1)
    pos1 = pd.DataFrame(sentence_embed1, columns=['X','Y'])
    pos1 = (pos1-pos1.min())/(pos1.max()-pos1.min())
    # pos1 = np.mat(sentence_embed1)
    # mean0 = np.mean(pos1[:,0])
    # std0 = np.std(pos1[:,0])
    # pos1[:,0] = (pos1[:,0]-mean0)/std0
    # mean1 = np.mean(pos1[:,1])
    # std1 = np.std(pos1[:,1])
    # pos1[:,1] = (pos1[:,1]-mean1)/std1
    # pos1 = pd.DataFrame(pos1, columns=['X','Y'])
    pos1['topic'] = 'hupu'

    sentence_embed2 = np.array(sentence_embed2)
    sentence_embed2 = TSNE(n_components=2).fit_transform(sentence_embed2)
    pos2 = pd.DataFrame(sentence_embed2, columns=['X','Y'])
    pos2 = (pos2-pos2.min())/(pos2.max()-pos2.min())
    # pos2 = np.mat(sentence_embed2)
    # mean0 = np.mean(pos2[:,0])
    # std0 = np.std(pos2[:,0])
    # pos2[:,0] = (pos2[:,0]-mean0)/std0
    # mean1 = np.mean(pos2[:,1])
    # std1 = np.std(pos2[:,1])
    # pos2[:,1] = (pos2[:,1]-mean1)/std1
    # pos2 = pd.DataFrame(pos2, columns=['X','Y'])
    pos2['topic'] = 'zhihu'

    sentence_embed3 = np.array(sentence_embed3)
    sentence_embed3 = TSNE(n_components=2).fit_transform(sentence_embed3)
    pos3 = pd.DataFrame(sentence_embed3, columns=['X','Y'])
    pos3 = (pos3-pos3.min())/(pos3.max()-pos3.min())
    # pos3 = np.mat(sentence_embed3)
    # mean0 = np.mean(pos3[:,0])
    # std0 = np.std(pos3[:,0])
    # pos3[:,0] = (pos3[:,0]-mean0)/std0
    # mean1 = np.mean(pos3[:,1])
    # std1 = np.std(pos3[:,1])
    # pos3[:,1] = (pos3[:,1]-mean1)/std1
    # pos3 = pd.DataFrame(pos3, columns=['X','Y'])
    pos3['topic'] = 'tieba'

    pos = pd.concat([pos1,pos2,pos3])
    print(pos)

    ax = pos[pos['topic']=='hupu'].plot(kind='scatter', x='X', y='Y', color='blue',label='hupu')
    pos[pos['topic']=='zhihu'].plot(kind='scatter', x='X', y='Y', color='red',label='zhihu',ax=ax)
    pos[pos['topic']=='tieba'].plot(kind='scatter', x='X', y='Y', color='green',label='tieba',ax=ax)
    plt.show()

if __name__ == '__main__':
    #cut_files()
    #cut_files_zhihu()
    #cut_files_tieba()
    x_train = get_datasest()
    model_dm = train(x_train,'full')
    sentence_embed_hupu , sentence_embed_zhihu , sentence_embed_tieba = test()
    plot(sentence_embed_hupu,sentence_embed_zhihu,sentence_embed_tieba)

