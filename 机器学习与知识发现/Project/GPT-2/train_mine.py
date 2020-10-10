import transformers
import torch
import os
import json
import random
import numpy as np
import argparse
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
from tqdm import tqdm
from torch.nn import DataParallel
from tokenizations.bpe_tokenizer import get_encoder
from pytorch_pretrained_bert import BertAdam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torch.utils.data import Dataset

def collate_fn(batch):
    return batch
    
class ArticleDataset(Dataset):
    def __init__(self, tokens):
        super(ArticleDataset, self).__init__()
        self.tokens = tokens
    
    def __len__(self):
        return len(self.tokens)
    
    def __getitem__(self, idx):
        return self.tokens[idx]



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_config', default='config/model_config_small.json', type=str, required=False,
                        help='choose the model size')
    parser.add_argument('--tokenizer_path', default='cache/vocab_small.txt', type=str, required=False, help='choose a vocabulary')
    parser.add_argument('--tokenized_data_path', default='data/tokenized/', type=str, required=False,
                        help='training data(already tokenized)')
    parser.add_argument('--epochs', default=30, type=int, required=False)
    parser.add_argument('--batch_size', default=4, type=int, required=False, help='batch size(will run out of the memory if too big)')
    parser.add_argument('--lr', default=1.5e-4, type=float, required=False)
    parser.add_argument('--warmup_steps', default=100000, type=int, required=False, help='warm up steps to train the pretrained model')
    parser.add_argument('--log_step', default=2, type=int, required=False, help='steps to print loss，should be times of accumulation gradient**')
    parser.add_argument('--stride', default=768, type=int, required=False, help='the step to move')
    parser.add_argument('--gradient_accumulation', default=1, type=int, required=False, help='equivalent to enlarge the batch size to solve the memory issue(I am so poor)')
    parser.add_argument('--fp16', action='store_true', help='whether or not to use amp to speed up training')
    parser.add_argument('--max_grad_norm', default=1.0, type=float, required=False, help='clip the gradient norm to avoid gradient explosion')
    parser.add_argument('--num_pieces', default=1, type=int, required=False, help='how much pieces to split the training data into, should be consistent with build_tokenized.py')
    # parser.add_argument('--min_length', default=128, type=int, required=False, help='minimal length of the training corpus')
    parser.add_argument('--output_dir', default='char model/', type=str, required=False, help='path to save the model')
    parser.add_argument('--pretrained_model', default='', type=str, required=False, help='use pretrained model(combined with warm up)')
    parser.add_argument('platform', choices=['zhihu', 'hupu', 'tieba'])
    
    args = parser.parse_args()

    


    
    

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    model_config = transformers.modeling_gpt2.GPT2Config.from_json_file(args.model_config)
    tokenized_data_path = args.tokenized_data_path + args.platform + '/'
    epochs = args.epochs
    batch_size = args.batch_size
    lr = args.lr
    warmup_steps = args.warmup_steps
    log_step = args.log_step
    stride = args.stride
    gradient_accumulation = args.gradient_accumulation
    fp16 = args.fp16  
    max_grad_norm = args.max_grad_norm
    num_pieces = args.num_pieces
    # min_length = args.min_length
    output_dir = args.output_dir + args.platform + '/'
    n_ctx = model_config.n_ctx
    if args.platform == 'zhihu':
        min_length = 128
    else:
        #because tieba and hupu reviews tend to be shorter.
        min_length = 5
    assert log_step % gradient_accumulation == 0

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    if not args.pretrained_model:
        # if train the original model
        model = transformers.modeling_gpt2.GPT2LMHeadModel(config=model_config)
    else:
        # if there is a pretrained model
        model = transformers.modeling_gpt2.GPT2LMHeadModel.from_pretrained(args.pretrained_model)
        
    model.to(device)
    # validate the normalization layer and dropout
    model.train()

    overall_length = 0
    for i in tqdm(range(num_pieces)):
        with open(tokenized_data_path + 'tokenized_{}.txt'.format(i), 'r') as f:
            overall_length += len([int(item) for item in f.read().strip().split()])
    total_steps = int(overall_length / stride * epochs / batch_size / gradient_accumulation)

    optimizer = transformers.AdamW(model.parameters(), lr=lr, correct_bias=True)
    
    scheduler = transformers.get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps,
                                                          num_training_steps=total_steps)

    # optimizer = BertAdam(model.parameters(), lr=lr, warmup=0.05,
    #                          t_total=total_steps)
    # scheduler = ReduceLROnPlateau(optimizer, patience=0, factor=0.1, verbose=True, mode='min', min_lr=1e-7)
    
    if fp16:
        try:
            from apex import amp
        except ImportError:
            raise ImportError("Poors guys with poor GPUs cannot use amp library!")
        model, optimizer = amp.initialize(model, optimizer, opt_level='O2', verbosity=0)

    with open((tokenized_data_path + 'tokenized_0.txt'), 'r') as f:
    #strip: clear the blank space in the end
        line = f.read().strip()
    #tokens: all of the tokens within a piece
    tokens = line.split()
    tokens = [int(token) for token in tokens]
    start = 0
    samples = []
    # a single sample has a length of n_ctx in a batch(1024 token as a unit)
    while start < len(tokens) - n_ctx:
        samples.append(tokens[start: start + n_ctx])
        start += stride
    if start < len(tokens):
        samples.append(tokens[len(tokens)-n_ctx:])
    random.shuffle(samples)
    training_set = ArticleDataset(samples)
    training_loader = DataLoader(training_set, batch_sampler=None, batch_size=batch_size, collate_fn=collate_fn, shuffle=True, drop_last=True)
    


    iteration = 0
    running_loss = 0
    for epoch in range(epochs):
        print('epoch {}'.format(epoch + 1))
        start_time = datetime.now()
        for step, batch_inputs in enumerate(training_loader):
            batch_inputs = torch.tensor(batch_inputs).long().to(device)
            outputs = model.forward(input_ids=batch_inputs, labels=batch_inputs)
            loss, logits = outputs[:2]
            if gradient_accumulation > 1:
                loss = loss / gradient_accumulation
            if fp16:
                with amp.scale_loss(loss, optimizer) as scaled_loss:
                    scaled_loss.backward()
                    torch.nn.utils.clip_grad_norm_(amp.master_params(optimizer), max_grad_norm)
            else:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)

            if (step + 1) % gradient_accumulation == 0:
                running_loss += loss.item()
                optimizer.step()
                optimizer.zero_grad()
                scheduler.step()


            print('Step {} of epoch {}, loss {}'.format(
                step + 1,
                epoch + 1,
                running_loss * gradient_accumulation / (log_step / gradient_accumulation)))
            running_loss = 0

       
        if not os.path.exists(output_dir + 'model_epoch{}'.format(epoch + 1)):
            os.mkdir(output_dir + 'model_epoch{}'.format(epoch + 1))
        model_to_save = model.module if hasattr(model, 'module') else model
        model_to_save.save_pretrained(output_dir + 'model_epoch{}'.format(epoch + 1))
        
        end_time = datetime.now()
        print('running time of this epoch: {}'.format(end_time - start_time))
    
    if not os.path.exists(output_dir + 'final_model'):
        os.mkdir(output_dir + 'final_model')
    model_to_save = model.module if hasattr(model, 'module') else model
    model_to_save.save_pretrained(output_dir + 'final_model')

if __name__ == '__main__':
    main()



