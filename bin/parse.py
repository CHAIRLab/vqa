import nltk
import os,json
from parse_util import be_words
from gqa_be_v1_stanfordnlp import parse_be_sentence
from gqa_v1_stanfordnlp import parse_single_sentence
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def parse(s):
    words = [w.lower() for w in nltk.word_tokenize(s)]
    if words[0] in be_words:
        return parse_be_sentence(s)
    else:
        return parse_single_sentence(s)

if __name__ == '__main__':
    result = parse("What color is the bottle on the sink?")
    print(result)
    json.dump(result, open('data/word_graph/131090.json', 'w', encoding='utf8'))