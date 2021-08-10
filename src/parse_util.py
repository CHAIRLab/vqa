import re
import joblib
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
import json
import stanfordnlp
wnl = WordNetLemmatizer()
st = LancasterStemmer()
nlp = stanfordnlp.Pipeline()

def judge(w):
    pattern = re.compile('[0-9]+')
    match = pattern.findall(w)
    if match:
        return True
    point = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']

    for i in w:
        if i in point:
            return True
    return False

def clean(w):
    w = w.lower()
    w = wnl.lemmatize(w)
    return w

base = './Data/base/'
rel_dict = json.load(open(base + 'word2rel_dict.json'))
key_words = json.load(open(base + 'keywords_test_data.json'))
key_words = [w for w in key_words if judge(w) is False]
wh_list, person_list, direction_list, be_words, filters, not_filter_words = joblib.load('./Data/base/compound.words')

def re_consturct_q(q):
    idx = q.find('that')
    is_that_idx = q.find('is that') # what is that man wearing
    if idx != -1 and is_that_idx==-1:
        q1, q2 = q[: idx], q[idx:]
        q1 = ' '.join([w for w in q1.split() if len(w) > 0])
        q2 = ' '.join([w for w in q2.split() if len(w) > 0])
        q2_words = q2.split()
        q1_words = q1.split()
        if len(q1_words) < 3:
            return [q.replace('that ', '')]
        if len(q2_words) < 2:
            return [q]

        if q2_words[-2] not in ['is', 'are', 'was', 'were'] and (q2_words[-1][-3:] == 'ing' or  q2_words[-1] == 'called'):
            q1 = q1 + ' ' + q2_words[-1]
            q2 = ' '.join(q2_words[:-1])
            q2_words = q2.split()

        if q2_words[1].lower() in ['is', 'are', 'looks', 'look']:
            # that is in the room
            q2 = q1_words[-1] + ' ' + ' '.join(q2_words[1:])
        else:
            q2 = ' '.join(q2_words[1:]) + ' ' + q1_words[-1]

        return [q1, q2]
    else:
        return [q]

def re_construct_VB_end(q_list):
    """
    :param q_list:
    :return:
    """
    re_list = []
    for q in q_list:
        if re.search(r"what (is|are) (the|this|that|those) ", q, flags=re.I) and (q[-6:] == 'called' or q[-3:]=='ing'):
            words = q.split()
            re_list.append(' '.join(words[: 4]) + ' ' + words[-1])
            re_list.append(' '.join(words[3: -1]))
        else:
            re_list.append(q)
    return re_list


def rel_chunk(pairs, text, pos_dict):
    def find_best_rel(t):
        best_rel = ''
        if t in rel_dict:
            for rel in rel_dict[t]:
                if text.find(rel) != -1 and len(rel.split()) > len(best_rel.split()):
                    best_rel = rel
        return best_rel
    pairs_ = []
    for so in pairs:
        best_s_rel = find_best_rel(so[0])
        best_o_rel = find_best_rel(so[1])
        s = so[0]
        o = so[1]
        if best_o_rel != best_s_rel and (best_o_rel != '' or best_s_rel != '') :
            if len(best_s_rel) > 0:
                s = best_s_rel
                pos_dict[s] = pos_dict.get(s.split()[-1], 'O')
            if len(best_o_rel) > 0:
                o = best_o_rel
                pos_dict[o] = pos_dict.get(o.split()[-1], 'O')
        elif best_o_rel == best_s_rel and best_s_rel != '':
            continue
        pairs_.append([s, o, so[2]])
    flags = [1] * len(pairs_)
    re_pairs = []
    for i in range(len(pairs_) - 1):
        for j in range(i+1, len(pairs_)):
            if pairs_[i][:2] == pairs_[j][:2] or pairs_[i][:2] == [pairs_[j][1], pairs_[j][0]]:
                flags[j] = 0
    for i in range(len(flags)):
        if flags[i] == 1:
            re_pairs.append(pairs_[i])

    return re_pairs, pos_dict

def is_first(pairs, text):
    if len(pairs) > 0 and  pairs[0][0][0] in be_words:
        flag = False

        for w in wh_list:
            if w in text:
                flag = True
                wh_word = w
                break
        if flag:
            re_pairs = []
            cand_pair = []
            for pair in pairs[1:]:
                s, p, o = pair
                s_t, s_pos = s
                o_t, o_pos = o
                if s_t in be_words and flag:
                    if o_pos[:2] in ['NN', 'VB']:
                        cand_pair.append(((wh_word, 'WP'), pair[1], (o_t, o_pos)))
                        flag = False

                elif o_t in be_words and flag:
                    if s_pos[:2] in ['NN', 'VB']:
                        cand_pair.append([wh_word, s_t])
                        flag = False
                else:
                    re_pairs.append(pair)
            return cand_pair + re_pairs
    return pairs

def re_sort_wh(pairs):
    """
    :param pairs:
    :return:
    """
    wh_pairs = []
    re_pairs = []
    for pair in pairs:
        if pair[0] in wh_list or pair[1] in wh_list:
            wh_pairs.append(pair)
        else:
            re_pairs.append(pair)
    re_pairs_ = []
    if len(wh_pairs) > 1:

        for p in wh_pairs:
            if p[0] in be_words or p[1] in be_words:
                continue
            re_pairs_.append(p)
    else:
        re_pairs_.extend(wh_pairs)

    re_pairs_.extend(re_pairs)
    return re_pairs_


def triple_first(t, item, pos_dict):
    """What's the book on?--》[what on book] --> [book, on, what]"""
    if len(item) == 2:
        return item
    if item[1] in wh_list:
        item = [item[1], item[0], item[2]]
    s, p, o = item
    if pos_dict.get(s, "NN") == 'IN' and pos_dict.get(p, 'NN') != 'IN' and pos_dict.get(o,'NN') != 'IN':

        temp = p
        p = s
        s = temp
    elif pos_dict.get(o, 'NN') == 'IN' and pos_dict.get(p, 'NN') != 'IN' and pos_dict.get(s, 'NN') != 'IN':
        temp = p
        p = o
        o = temp
    t_ = ' ' + t + ' '
    p_idx = t_.find(' ' + p + ' ')
    s_idx = t_.find(' ' + s + ' ')
    o_idx = t_.find(' ' + o + ' ')
    if s_idx < p_idx and o_idx < p_idx:
        if s_idx > o_idx:
            return [s, p, o]
        else:
            return [o, p, s]
    elif s_idx > p_idx and o_idx:
        if s_idx < o_idx:
            return [s, p, o]
        else:
            return [o, p, s]
    elif s_idx < p_idx and o_idx > p_idx:
        return [s, p, o]
    else:
        return [o, p, s]


def what_nn_is_prep(words, post_dict):
    """
    what animal is on the dirt:
    :param words:
    :param post_dict:
    :return:
    """
    for i, w in enumerate(words[:-1]):
        if w in be_words and post_dict.get(words[i+1], 'O') == "IN":
            return True
    return False

def cut_redundance(pairs):
    """
    [['yes', 'no'], ['beds', 'next to', 'outlet'], ['outlet', 'small'], ['beds', 'outlet']] cut ['beds', 'outlet']
    :param pairs:
    :return:
    """
    re_pairs = []
    for i in range(len(pairs)):
        e1 = pairs[i]
        if len(e1) == 3:
            re_pairs.append(e1)
        else:
            flag = False
            for j in range(len(pairs)):
                if i == j:
                    break
                e2 = pairs[j]
                if e1[0] in e2 and e1[1] in e2:
                    flag = True
                    break
            if flag == False:
                re_pairs.append(e1)
    return re_pairs


def clean_scene(s):
    s = s.replace('do you think', '')
    s = s.replace('in this picture', '')
    s = s.replace('in the picture', '')

    s = s.replace('in the scene', '')
    s = s.replace('in this scene', '')

    s = s.replace('in the image', '')
    s = s.replace('in this image ', '')

    s = s.replace('in the photograph ', '')
    s = s.replace('in this photograph ', '')

    s = s.replace('in the photo', '')
    s = s.replace('in this photo', '')
    s = s.replace(' located on top of ', ' on top of ')
    s = s.replace("n't", ' not')
    s = s.replace('what is that ', 'what is the ')
    s = s.replace('kind of ', '')
    s = s.replace('type of ', '')
    s = s.replace('piece of ', '')
    s = s.replace('item of ', '')
    s = s.replace('items of ', '')
    s = s.replace('items', '')
    s = s.replace(' appear', '')
    return s

def clean_be(s):
    if s[:7].lower() == 'is that':
        s = 'is' + s[7:]
    elif s[:8].lower() == 'are that':
        s = 'is' + s[8:]
    elif s[:8].lower() == 'was that':
        s = 'is' + s[8:]
    elif s[:9].lower() == 'were that':
        s = 'is' + s[9:]
    return s

def find(q, k):
    words = q.split()
    flag = False
    for w in words:
        if w == k:
            flag = True
            break
    return q.find(k) if flag else -1


def re_construct_VB_end(q_list):
    re_list = []
    for q in q_list:
        if re.search(r"what (is|are) (the|this|that|those) ", q, flags=re.I) and (q[-6:] == 'called' or q[-3:]=='ing'):
            words = q.split()
            re_list.append(' '.join(words[: 4]) + ' ' + words[-1])
            re_list.append(' '.join(words[3: -1]))
        else:
            re_list.append(q)
    return re_list

def handle_first_direction(pairs, words):
    if len(pairs) <= 1 or (pairs[0][1] not in wh_list and pairs[0][0] not in wh_list) or words[1] in ['is', 'are', 'was', 'were', 'do', 'done'] : # pairs对只有一个或者第一个pair对中不包含疑问词
        return []

    s_0, o_0 =  pairs[0][0], pairs[0][1]
    s_0_words, o_0_words = pairs[0][0].split(), pairs[0][1].split()
    wh_word = None
    for w in direction_list:
        if w in s_0_words:
            wh_word = o_0
            break
        elif  w in o_0_words:
            wh_word = s_0
            break
    re_pair = []
    if wh_word and s_0 == pairs[1][0]:
        re_pair = [wh_word, pairs[1][1], pairs[1][2]]
    elif wh_word and s_0 == pairs[1][1]:
        re_pair = [wh_word, pairs[1][0], pairs[1][2]]
    elif wh_word and o_0 == pairs[1][1]:
        re_pair = [wh_word, pairs[1][0], pairs[1][2]]
    elif wh_word and o_0 == pairs[1][0]:
        re_pair = [wh_word, pairs[1][1], pairs[1][2]]
    return re_pair


def handle_preposition_last(pairs):
    """
     [['sink', 'counter', 'on']]--》 [['sink', 'on' , 'counter']]
    [['on', 'sink', 'counter']]--》 [['sink', 'on' , 'counter']]
    :param pairs:
    :return:
    """
    re_pairs = []
    for spo in pairs:
        if len(spo) == 2:
            re_pairs.append(spo)
            continue
        last_words = spo[-1].split()
        p = [spo[0], spo[1], spo[2]]
        for w in last_words:
            if w in direction_list:
                p = [spo[0], spo[2], spo[1]]
        first_words = spo[0].split()
        for w in first_words:
            if w in direction_list:
                p = [spo[1], spo[0], spo[2]]
        re_pairs.append(p)
    return re_pairs