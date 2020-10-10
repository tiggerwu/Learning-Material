import torch
import torch.nn.functional as F
import os
import argparse
from tqdm import trange
from transformers import GPT2LMHeadModel
from tokenizations import tokenization_bert



def is_word(word):
    for item in list(word):
        if item not in 'qwertyuiopasdfghjklzxcvbnm':
            return False
    return True



def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
        Args:
            logits: logits distribution shape (vocabulary size)
            top_k > 0: keep only top k tokens with highest probability (top-k filtering).
            top_p > 0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        From: https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317
    """
    assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits


def sample_sequence(model, context, length, n_ctx, tokenizer, temperature=1.0, top_k=30, top_p=0.0, repitition_penalty=1.0,
                    device='cpu'):
    context = torch.tensor(context, dtype=torch.long, device=device)
    context = context.unsqueeze(0)
    generated = context
    with torch.no_grad():
        for _ in trange(length):
            inputs = {'input_ids': generated[0][-(n_ctx - 1):].unsqueeze(0)}
            outputs = model(
                **inputs)  # Note: we could also use 'past' with GPT-2/Transfo-XL/XLNet (cached hidden-states)
            next_token_logits = outputs[0][0, -1, :]
            for id in set(generated):
                next_token_logits[id] /= repitition_penalty
            next_token_logits = next_token_logits / temperature
            #we dont want to output [UNK] token
            next_token_logits[tokenizer.convert_tokens_to_ids('[UNK]')] = -float('Inf')
            filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=top_k, top_p=top_p)
            next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
            generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
    return generated.tolist()[0]



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--length', default=100, type=int, required=False, help='the length of the generated text')
    parser.add_argument('--nsamples', default=3, type=int, required=False, help='generate n samples')
    parser.add_argument('--temperature', default=1.0, type=float, required=False,
                         help='generation temperature, the bigger the temperature is, the more likely to choose those vocab with lower probs. You can refer to the paper in topkp filtering.')
    parser.add_argument('--topk', default=30, type=int, required=False, help='topk for beam search')
    parser.add_argument('--topp', default=0, type=float, required=False, help='max accumulation prob')
    parser.add_argument('--model_config', default='config/model_config_small.json', type=str, required=False,
                        help='model configuration')
    parser.add_argument('--tokenizer_path', default='cache/vocab_small.txt', type=str, required=False, help='vocab path')
    parser.add_argument('--model_path', default='model/', type=str, required=False, help='model path')
    parser.add_argument('--save_samples', action='store_true', help='save samples?')
    parser.add_argument('--save_samples_path', default='.', type=str, required=False, help="the path to save samples")
    parser.add_argument('--repetition_penalty', default=1.0, type=float, required=False)
    parser.add_argument('platform', choices=['zhihu', 'hupu', 'tieba'])

    args = parser.parse_args()




    length = args.length
    nsamples = args.nsamples
    temperature = args.temperature
    topk = args.topk
    topp = args.topp
    repetition_penalty = args.repetition_penalty
    model_path = args.model_path + args.platform

    print(model_path)


    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = tokenization_bert.BertTokenizer(vocab_file=args.tokenizer_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    model.to(device)
    model.eval()

    n_ctx = model.config.n_ctx

    if length == -1:
        length = model.config.n_ctx
    if args.save_samples:
        if not os.path.exists(args.save_samples_path):
            os.makedirs(args.save_samples_path)
        samples_file = open(args.save_samples_path + args.platform + '/samples.txt', 'w', encoding='utf8')

    print("输入球评的开始:")
    prefix = input()
    while True:
        raw_text = prefix
        context_tokens = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(raw_text))
        num_generated = 0
        for _ in range(nsamples):
            out = sample_sequence(
                n_ctx=n_ctx,
                model=model,
                context=context_tokens,
                length=length,
                tokenizer=tokenizer,
                temperature=temperature, top_k=topk, top_p=topp, repitition_penalty=repetition_penalty, device=device
            )
            # for i in range(batch_size):
            num_generated += 1
            break_point = -1

            text = tokenizer.convert_ids_to_tokens(out)
            for i, item in enumerate(text[:-1]):  # drop last
                if is_word(item) and is_word(text[i + 1]):
                    text[i] = item + ' '
            for i, item in enumerate(text):
                if item == '[MASK]':
                    text[i] = ''
                elif item == '[CLS]':
                    text[i] = '\n\n'
                    break_point = i + 1
                elif item == '[SEP]':
                    text[i] = '\n'
            info = "=" * 40 + " SAMPLE " + str(num_generated) + " " + "=" * 40 + "\n"
            print(info)
            if break_point == -1:    
                text = ''.join(text).replace('##', '').strip()
            else:
                text = ''.join(text[:break_point]).replace('##', '').strip()
            print(text)
            if args.save_samples:
                samples_file.write(info)
                samples_file.write(text)
                samples_file.write('\n')
                samples_file.write('=' * 90)
                samples_file.write('\n' * 2)
        print("=" * 80)
        if num_generated == nsamples:
            # close file when finish writing.
            if args.save_samples:
                samples_file.close()
            break


if __name__ == '__main__':
    main()
