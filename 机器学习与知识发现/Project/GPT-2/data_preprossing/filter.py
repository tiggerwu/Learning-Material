import re
import argparse
import pandas as pd

def filter_by_paragraph(data_path):    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = f.read()
    filtered = []
    for item in data.split('\n'):
        if item != '' and item[0] != '!' and item[0] != '#' and item[0]!='-' :
            filtered.append(item)
    return filtered


parser = argparse.ArgumentParser()
arg = parser.add_argument
arg('--data', default=None)
args = parser.parse_args()
DATA_PATH = args.data
filtered = filter_by_paragraph(DATA_PATH)
filtered = [item.replace('*', '') for item in filtered]
http_p = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
filtered = [re.sub(http_p, '', item) for item in filtered]

print("collecting {} items.....".format(len(filtered)))

filt = pd.DataFrame(data=filtered)
filt.to_csv('final.csv', mode='a', encoding='utf-8_sig', header=False)