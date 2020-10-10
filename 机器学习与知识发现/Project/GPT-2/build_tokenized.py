import argparse
import json
import os
from tqdm import tqdm
from tokenizations import tokenization_bert


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_data_path', default='data/tieba.json', type=str, required=False, help='raw training data in json format')
    parser.add_argument('--output_path', default='data/tokenized/tieba', type=str, required=False, help='the path to save the tokenized data')
    parser.add_argument('--num_pieces', default=1, type=int, required=False, help='how much pieces to split the training data into')
    parser.add_argument('--tokenizer_path', default='cache/vocab_small.txt', type=str, required=False, help='choose the tokenizer')
    args = parser.parse_args()

    data_path = args.raw_data_path
    output_path = args.output_path
    num_pieces = args.num_pieces



    
    tokenizer = tokenization_bert.BertTokenizer(vocab_file=args.tokenizer_path)

    tokenizer.max_len = 100000 

    with open(data_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
        # both a single \n and a double \n will be replaced with [SEP] to make it more clear
        articles = [article.replace('\n\n', ' [SEP] ') for article in articles]
        articles = [article.replace('\n', ' [SEP] ') for article in articles]
        num_articles = len(articles)
    # a piece should include several articles
    assert num_articles > num_pieces
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    for i in tqdm(range(num_pieces)):
        #sub_articles: articles of one piece
        sub_articles = articles[num_articles // num_pieces * i: num_articles // num_pieces * (i + 1)]
        if i == num_pieces - 1 and num_pieces != 1:
            sub_articles.extend(articles[num_articles // num_pieces * (i + 1):])
        sub_articles = [tokenizer.tokenize(article) for article in sub_articles]
        sub_articles = [tokenizer.convert_tokens_to_ids(article) for article in sub_articles]

        full_sub_articles = []
        for article in sub_articles:
            # [MASK] to denote the start of an article, [CLS] to denote the end of an article
            # full_sub_articles.append(tokenizer.convert_tokens_to_ids(["[MASK]"] + article + ["[CLS]"]))
            full_sub_articles.append(tokenizer.convert_tokens_to_ids('[MASK]'))
            full_sub_articles.extend(article)
            full_sub_articles.append(tokenizer.convert_tokens_to_ids('[CLS]'))
        with open(os.path.join(output_path, 'tokenized_{}.txt'.format(i)), 'w') as f:
            for item in full_sub_articles:
                f.write(str(item) + ' ')

if __name__ == '__main__':
    main()





