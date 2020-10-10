import jieba
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
from collections import Counter 
import os, sys
import sys,os
path = os.path.abspath(os.path.dirname(sys.argv[0]))

def word_split(text,topic):
    split_words = jieba.cut(text,cut_all=False)
    data = []
    for word in split_words:
        data.append(word)
    dataDict = Counter(data)
    with open((path + '/WordFre_' + topic + '.txt'),'w') as fil:
        for k,v in dataDict.items():
            fil.write(str(k) + '\t' + str(v) + '\n')
    
    split_words = jieba.cut(text,cut_all=False)
    split_words_list = ''.join(split_words)

    return split_words_list

def generate_wordcloud(text,topic):
    mask = np.array(Image.open(path + '/mask.png'))
    font_path = path + '/msyh.ttf'
    if topic == 'Hupu':
        stopwords = set(STOPWORDS) | {'哈哈','哈哈哈','可以','是的','加油','视频无法播放','浏览器版本过低'}
    elif topic == 'Zhihu':
        stopwords = set(STOPWORDS) | {'关注微信公众号','微信号','jingyimo456','静易墨','扫描二维码关注','扫描二维码关注静易墨'}
    elif topic == 'Tieba':
        stopwords = set(STOPWORDS) | {'哈哈','微信号','是的','哈哈哈','确实','最理智詹密留'}

    wordcloud = WordCloud(
        background_color = 'white',
        stopwords = stopwords,
        max_words = 3000,
        font_path = font_path,
        width = 2000,
        height = 1200,
        mask = None #mask
    )

    wordcloud.generate(text)

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    text_hupu = open(path + '/hupu.txt').read()
    text_hupu = word_split(text_hupu,'Hupu')
    generate_wordcloud(text_hupu,'Hupu')

    text_zhihu = open(path + '/zhihu.txt').read()
    text_zhihu = word_split(text_zhihu,'Zhihu')
    generate_wordcloud(text_zhihu,'Zhihu')

    text_tieba = open(path + '/tieba.txt').read()
    text_tieba = word_split(text_tieba,'Tieba')
    generate_wordcloud(text_tieba,'Tieba')