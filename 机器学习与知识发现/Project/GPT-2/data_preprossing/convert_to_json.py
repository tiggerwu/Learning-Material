import pandas as pd
import numpy as np
from pathlib import Path
import json

hp_path = Path('..\data\hupu.csv')
hp = pd.read_csv(hp_path)
hp = list(hp['text'])
hp_file = '..\data\hupu.json'
with open(hp_file, 'a', encoding='utf-8') as f:
    json.dump(hp, f, ensure_ascii=False)

tb_file = '..\data\\tieba_data.txt'
with open(tb_file, 'r', encoding='utf-8') as f:
    line = f.read().split('\n')

tb_file = '..\data\\tieba_data.json'
with open(tb_file, 'a', encoding='utf-8') as f:
    json.dump(line, f, ensure_ascii=False)