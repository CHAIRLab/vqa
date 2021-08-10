# -*- coding: utf-8 -*-#
# email:
# Description:
# Author:       adzhua
# Date:         2019/8/12

import nltk
import copy
import re
from parse_util import triple_first, re_sort_wh, be_words, what_nn_is_prep, rel_chunk, find, re_construct_VB_end, handle_first_direction
from parse_util import key_words, cut_redundance, judge, clean, clean_scene, nlp, filters, wh_list, handle_preposition_last


def pares_sentence(s):
    """
    解析所有问句
    :return:
    """
    pairs = []
    pos_dict = {}
    if s[-1] in filters:
        s = s[:-1]
    s = s.strip().replace('\n', '')
    doc = nlp(s)
    for dep_edge in doc.sentences[0].dependencies:



        s =  clean(dep_edge[0].text)
        s_pos = dep_edge[0].pos
        o =  clean(dep_edge[2].text)
        # if s not in sg_words and o not in sg_words:
        #     continue
        o_pos = dep_edge[2].pos
        rel = dep_edge[1]
        print(s, rel, o)
        if dep_edge[0].text == 'ROOT':
            continue
        if s in ['the', 'a', 'an'] or o in ['the', 'a', 'an']:
            continue

        if judge(s) or judge(o):
            continue
        if s in filters or o in filters or dep_edge[0].text in filters or dep_edge[2].text in filters:
            continue

        if s not in pos_dict or s_pos[:2] == 'NN':
            pos_dict[dep_edge[0].text] = s_pos[:2]
        if o not in pos_dict or o_pos[:2] == 'NN':
            pos_dict[dep_edge[2].text] = o_pos[:2]

        if s in key_words or o in key_words:

            if dep_edge[1][:4]  in ['nsub', 'nmod']:  # nsubjpass
                pairs.append([dep_edge[2].text, dep_edge[0].text, rel])
            else:
                pairs.append([dep_edge[0].text, dep_edge[2].text, rel])
            if pairs[-1][1] == 'not':
                pairs[-1] = [pairs[-1][1], pairs[-1][0], pairs[-1][2]]

    pairs = re_sort_wh(pairs)
    return pairs, pos_dict


def re_consturct_q(q):
    idx = q.find('that')
    is_that_idx = q.find('is that') # what is that man wearing
    if idx != -1 and is_that_idx==-1:
        q1, q2 = q[: idx], q[idx:]
        q1 = ' '.join([w for w in q1.split() if len(w) > 0])
        q2 = ' '.join([w for w in q2.split() if len(w) > 0])
        q2_words = q2.split()
        q1_words = q1.split()
        if len(q2_words) < 2:
            return [q]

        if q2_words[-2] not in be_words and (q2_words[-1][-3:] == 'ing' or  q2_words[-1] == 'called'):
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



def re_construct_item_kind(q_list):
    """
    what kind of| what item of
    What item of furniture does the computer sit on? --[what item of furniture is, furniture does the computer sit on]
    :param q_list:
    :return:
    """

    re_q = []
    for q in q_list:
        if 'what kind of' in q or 'what item of' in q or 'what type of' in q or 'what piece of' in q:
            of_idx = find(q, 'of')
            q2 = q[of_idx + 3:].strip()
            flag = True
            for k in ['is', 'are']:
                idx = q.find(k)
                if idx != -1:
                    q1 = q[:idx - 1].strip()
                    re_q.append(q1)
                    re_q.append(q2)
                    flag = False
                    break
            for k in ['do', 'does']:
                idx = find(q, k)
                shift = 5 if k == 'does' else 3
                q2 = q[idx + shift:] + ' ' + q[of_idx + 3: idx - 1]
                if idx != -1:
                    q1 = q[:idx - 1].strip()
                    re_q.append(q1)
                    re_q.append(q2)
                    flag = False
                    break
            if flag:
                re_q.append(q)
        else:
            re_q.append(q)
    return re_q



def fine_tune_not(pairs):
    """
    [['what', 'color', 'helmet'], ['helmet', 'in the middle of', 'image']] to
    [['helmet', 'color', 'what'], ['helmet', 'in the middle of', 'image']]
    :param pairs:
    :return:
    """
    for i, pair in enumerate(pairs):
        if pair[0] == 'not' and len(pair) == 3:
            pairs[i] = [pair[1], pair[0], pair[-1]]
        elif pair[-1] == 'not' and len(pair) == 3:
            pairs[i] = [pair[0], pair[-1], pair[1]]


    return pairs


def re_pairs(pairs, words, pos_dict):
    """
    :param pairs:
    :return:
    """
    spo_list = []
    t = ' '.join(words)
    first_pair = handle_first_direction(pairs, words)
    if len(first_pair) > 0:
        spo_list.append(first_pair[:2])

    is_chooses = [0] * len(pairs)
    for i in range(len(pairs)):
        if is_chooses[i] == 1:
            continue
        e1 = pairs[i]
        # # (('food', 'NN'), 'amod', ('fast', 'JJ'))  ['fast food is on the grill']
        if e1[2] == 'amod' or e1[2] == 'compound' and is_chooses[i] == 0:
            spo_list.append(e1[:2][::-1])
            is_chooses[i] = 1
            continue
        if e1[2] == 'nsubj:pass':
            spo_list.append(e1[:2])
            is_chooses[i] = 1
            continue
        if ('what' in e1  or 'which' in e1) and words[1] not in ['is', 'was', 'are', 'were', "'s", "'re"] :#and e1[2] not in ['det']:
            filter_NN = ['kind', 'type', 'item']
            if (e1[0] in pos_dict and pos_dict[e1[0]] == "NN" and e1[0] not in filter_NN) or (e1[1] in pos_dict and pos_dict[e1[1]] == 'NN' and e1[1] not in filter_NN):
                if e1[2] not in ['nsubj'] and what_nn_is_prep(words, pos_dict):
                    e1 = [e1[1], e1[0]] if e1[1] == 'what' else e1
                    spo_list.append(e1[:2])
                    continue

        for j in range(i + 1, len(pairs)):
            e2 = pairs[j]
            if e2[2] == 'amod' and (pos_dict.get(e2[0], 'O') in ['JJ', 'O'] or pos_dict.get(e2[1], 'O') in ['JJ', 'O']):
                continue
            if e1[0] == e2[0]:
                if e1[1] in wh_list:
                    if e1[2][:4] in ['nsub']: # what is this bird called?
                        spo_list.append([e1[0], e2[1], e1[1]])
                    else:
                        spo_list.append([e1[1], e1[0], e2[1]])

                elif t.find(e1[1]) < t.find(e2[1]):
                    spo_list.append([e1[1], e1[0], e2[1]])
                else:
                    spo_list.append([e2[1], e1[0], e1[1]])
                is_chooses[i] = 1
                is_chooses[j] = 1
                break
            elif e1[1] == e2[0]:
                spo_list.append([e1[0], e1[1], e2[1]])
                is_chooses[i] = 1
                is_chooses[j] = 1
                break
            elif e1[0] == e2[1]:
                if t.find(e1[1]) < t.find(e2[0]) and e1[1] not in wh_list:
                    spo_list.append([e1[1], e1[0], e2[0]])
                else:
                    spo_list.append([e1[1], e1[0], e2[0]])
                is_chooses[i] = 1
                is_chooses[j] = 1
                break
            elif e1[1] == e2[1]:
                if e1[0] in wh_list:
                    if e1[2][:4] in ['nsub']:   # What do you think is hanging in the open shower?
                        spo_list.append([e1[0], e1[1], e2[0]])
                    else:
                        spo_list.append([e2[0], e1[1], e1[0]])
                else:
                    spo_list.append([e1[0], e1[1], e2[0]])
                is_chooses[i] = 1
                is_chooses[j] = 1
                break

        if is_chooses[i] == 0:
            spo_list.append(e1[:2])
            is_chooses[i] = 1
    spo_list = handle_preposition_last(spo_list)
    spo_list = [triple_first(t, item, pos_dict) for item in spo_list]
    spo_list = fine_tune_not(spo_list)
    return spo_list


def combine_compound_phrase(pairs):
    """
    :param pairs:
    :return:
    """
    re_data = []
    pairs_ = []
    for pair in pairs:
        if pair[-1] in  ['compound', 'nmod:poss']:
            re_data.append(pair[:-1][::-1])
        else:
            pairs_.append(pair)

    for item in re_data:

        for pair in pairs_:
            if pair[0] in item:
                pair[0] = ' '.join(item)
            elif pair[1] in item:
                pair[1] = ' '.join(item)
    return re_data, pairs_


def cut_two_preposition(pairs, pos_dict):
    """
    :param pairs:
    :param pos_dict:
    :return:
    """
    data = []
    for pair in pairs:
        cnt = 0
        for item in pair:
            for w in item.split():
                if pos_dict.get(w, 'NN') == 'IN':
                    cnt += 1
                    break
        if cnt < 2:
            data.append(pair)
    return data


def handle_conj(pairs):
    """
    ('man', 'woman', 'conj')]
    [('man', 'where', 'nsubj'), ('man', 'woman', 'conj'), ['woman', 'apple', 'nmod']] 保留man,-->[('man', 'where', 'nsubj'), ('man', 'apple', 'nmod')]
    :param pairs:
    :return:
    """
    conj_pairs = []
    for pair in pairs:
        if pair[-1] == 'conj':
            conj_pairs.append(pair)

    replaced_pairs = []
    for conj_pair in conj_pairs:
        for pair in pairs:
            if conj_pair[1] in pair:
                pair[pair.index(conj_pair[1])] = conj_pair[0]
                if pair[0] != pair[1]:
                    replaced_pairs.append(pair)
            else:
                replaced_pairs.append(pair)
    for p in pairs:
        if p not in conj_pair:
            replaced_pairs.append(p)
    return conj_pairs, replaced_pairs


def add_conj(pairs, conj_pairs):
    """
    :param pair:
    :param conj_pair:
    :return:
    """
    re_data = []
    for conj_p in conj_pairs:
        for p in pairs:
            re_data.append(p)
            if conj_p[0] in p:
                p_ = copy.deepcopy(p)
                p_[p_.index(conj_p[0])] = conj_p[1]
                re_data.append(p_)
    return re_data


def parse_single_sentence(s):
    s = clean_scene(s)
    words = nltk.word_tokenize(s)
    if words[-1] == '?':
        words = words[:-1]
    s = ' '.join([w.lower() for w in words])
    pairs = []
    if ',' in s:
        s, a = s.split(',')
        s = s.strip()
        a = [w.strip() for w in a.split('or ')]
        pairs.append(a)
    else:
        pairs.append(())

    q_list =  re_consturct_q(s)

    q_list = re_construct_VB_end(q_list)

    q_list = re_construct_item_kind(q_list)

    for q in q_list:
        pairs_, pos_dict = pares_sentence(q)
        pairs_, pos_dict = rel_chunk(pairs_, s, pos_dict)
        re_data, pairs_ = combine_compound_phrase(pairs_)
        pairs_ = re_pairs(pairs_, words, pos_dict)
        pairs_ = cut_two_preposition(pairs_, pos_dict)
        pairs = pairs + pairs_
    pairs = cut_redundance(pairs)   #
    return pairs


if __name__ == '__main__':
    print(parse_sentence( "What color is the helmet?"))
