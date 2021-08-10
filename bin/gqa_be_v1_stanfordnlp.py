
import nltk
import re
from parse_util import triple_first, re_sort_wh, be_words, clean_be, cut_redundance, judge, clean, clean_scene, find, handle_preposition_last
from parse_util import key_words, rel_dict, nlp, filters, wh_list, handle_first_direction, not_filter_words, re_construct_VB_end


def pares_sentence(s):

    s = s.strip().replace('\n', '')
    pairs = []
    pos_dict = {}
    conj_dict = {}
    doc = nlp(s)
    for dep_edge in doc.sentences[0].dependencies:
        if dep_edge[0].text == 'ROOT':
            continue

        s = clean(dep_edge[0].text)
        s_pos = dep_edge[0].pos
        o = clean(dep_edge[2].text)
        o_pos = dep_edge[2].pos
        rel = dep_edge[1]
        if s not in pos_dict or s_pos[:2] == 'NN':
            pos_dict[dep_edge[0].text] = s_pos[:2]
        if o not in pos_dict or o_pos[:2] == 'NN':
            pos_dict[dep_edge[2].text] = o_pos[:2]

        rel = dep_edge[1]
        if rel == 'conj':
            if s not in conj_dict:
                conj_dict[dep_edge[0].text] = set()
            conj_dict[dep_edge[0].text].add(dep_edge[2].text)
            if o not in conj_dict:
                conj_dict[dep_edge[2].text] = set()
            conj_dict[dep_edge[2].text].add(dep_edge[0].text)
        if rel == 'cc' and (s=='or' or o=='or'):    # cc: (('green', 'JJ'), 'cc', ('or', 'CC'))
            continue
        if rel == 'conj' and len(pairs) != 0:
            continue
        if rel in ['det', 'case'] and (s not in wh_list and o not in wh_list) and (s not in not_filter_words and o not in not_filter_words) and not (s_pos[:2]=='NN' and o_pos[:2]=='IN') and not(o_pos[:2]=='NN' and s_pos[:2]=='IN'):
            continue

        if judge(s) or judge(o):
            continue
        if s in filters or o in filters or dep_edge[0].text in filters or dep_edge[2].text in filters:
            continue

        if s in key_words or o in key_words:
            if dep_edge[1][:5] == 'nsubj':  # nsubjpass
                pairs.append((dep_edge[2].text, dep_edge[0].text, rel))
            else:
                pairs.append((dep_edge[0].text, dep_edge[2].text, rel))

    re_pairs = []
    for pair in pairs:
        re_pairs.append(pair)
        if pair[2] == 'conj':
            continue
        if pair[0] in conj_dict and pair[2] not in ['advmod']:
            for v in conj_dict[pair[0]]:
                re_pairs.append((v, pair[1], pair[2]))
        if pair[1] in conj_dict and pair[2] not in ['advmod']:
            for v in conj_dict[pair[1]]:
                re_pairs.append((pair[0], v, pair[2]))
    re_pairs = re_sort_wh(re_pairs)
    return re_pairs, pos_dict, conj_dict



def cut_first(q):
    def cut_seq(cut_s):
        l = len(cut_s)
        if q[:l] == cut_s:
            return q[l:]
        return q
    q = cut_seq('are there either any ')
    q = cut_seq('are there any ')
    q = cut_seq('are there ')
    q = cut_seq('are ')
    q = cut_seq('is there either any ')
    q = cut_seq('is there any ')
    q = cut_seq('is there ')
    q = cut_seq('is ')
    q = cut_seq('do ')
    q = cut_seq('does ')
    return q


def re_consturct_q(q):
    q_type = 0
    if q.find(' or ') != -1:
        if q.find('are there ') != -1 or q.find('is there ') != -1:
            q_type = 1
        else:
            q_type = 2
    q = cut_first(q)
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

        return q_type, [q1, q2]
    else:
        return q_type, [q]



def rel_chunk(pairs, text):
    """
    合并to the left of这种
    """
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
            if len(best_o_rel) > 0:
                o = best_o_rel
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
    return re_pairs



def re_construct_item_kind(q_list):
    """
    what kind of| what item of 句子依存解析错误导致的WG错误
    What item of furniture does the computer sit on? --[what item of furniture is, furniture does the computer sit on]
    :param q_list:
    :return:
    """

    re_q = []
    for q in q_list:
        if 'what kind of' in q or 'what item of' in q or 'what type of' in q:
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
                idx = find(q, k)  # 用find有问题
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





def re_pairs(pairs, words, conj_dict, pos_dict):
    is_chooses = [0] * len(pairs)
    def judge_conj(e1, e2):
        """
        判断两个二元组是否包含conj，是就不合并 比如：[A, B], [A, C] B和C是conJ关系就不合并
        :param e1:
        :param e2:
        :return:
        """
        def judge_temp(w1, w2):
            if w1 in conj_dict:
                if w2 in conj_dict[w1]:
                    return True
                for c in w2.split():
                    if c in conj_dict[w1]:
                        return True
            for c1 in w1.split():
                if c1 in conj_dict:
                    if w2 in conj_dict[c1]:
                        return True
                    for c2 in w2.split():
                        if c2 in conj_dict[c1]:
                            return True
            return False


        if e1[0] == e2[0]:
            return judge_temp(e1[1], e2[1]) or judge_temp(e2[1], e1[1])
        elif e1[0] == e2[1]:
            return judge_temp(e1[1], e2[0]) or judge_temp(e2[0], e1[1])
        elif e1[1] == e2[0]:
            return judge_temp(e1[0], e2[1]) or judge_temp(e2[1], e1[0])
        elif e1[1] == e2[1]:
            return judge_temp(e1[0], e2[0]) or judge_temp(e2[0], e1[0])
        else:
            return False

    if len(pairs) == 1 and pairs[0][2] == 'conj':
        return [[pairs[0][0]], [pairs[0][1]]]

    spo_list = []
    t = ' '.join(words)
    first_pair = handle_first_direction(pairs, words)
    if len(first_pair) > 0:
        spo_list.append(first_pair[:2])


    for i in range(len(pairs)):
        if is_chooses[i] == 1:
            continue
        e1 = pairs[i]
        if (e1[2] in ['amod', 'compound'] or (e1[2]=='advomd' and pos_dict.get(e1[0], 'O')[:2]=='JJ'))  and is_chooses[i] == 0:  # (('food', 'NN'), 'amod', ('fast', 'JJ'))  ['fast food is on the grill']
            spo_list.append(e1[:2] )
            is_chooses[i] = 1
            continue
        for j in range(i + 1, len(pairs)):
            e2 = pairs[j]
            if e2[2] in 'compound' or judge_conj(e1, e2) or (e2[2]=='advmod' and pos_dict.get(e2[0], 'O')[:2]=='JJ'):
                continue
            if e1[1] == e2[0]:
                spo_list.append([e1[0], e1[1], e2[1]])
                is_chooses[j] = 1
                is_chooses[i] = 1

        if is_chooses[i] == 0:
            spo_list.append(e1[:2] + [1])
            is_chooses[i] = 1

    re_pairs = []
    flags = [0] * len(spo_list)
    for i in range(0, len(spo_list)):
        if flags[i] == 1:
            continue
        e1 = spo_list[i]
        if len(e1) == 3 and e1[2] == 1:
            for j in range(i + 1, len(spo_list)):
                e2 = spo_list[j]
                if judge_conj(e1, e2):
                    continue
                if len(e2) == 3 and e2[2] == 1:
                    if e1[0] == e2[0]:
                        re_pairs.append([e1[1], e1[0], e2[1]])
                        flags[i] = 1
                        flags[j] = 1
                    elif e1[0] == e2[1]:
                        re_pairs.append([e1[1], e1[0], e2[0]])
                        flags[i] = 1
                        flags[j] = 1
                    elif e1[1] == e2[1]:
                        re_pairs.append([e1[0], e1[1], e2[0]])
                        flags[i] = 1
                        flags[j] = 1
                break
            if flags[i] == 0:
                re_pairs.append(e1[:2])
                flags[i] = 1
        else:

            re_pairs.append(e1[:2] if len(e1) == 3 and e1[2] == 1 else e1)
            flags[i] = 1
    # not_hit_conj = []
    for k in conj_dict:
        for pair in re_pairs:

            if k  in pair:
                idx = pair.index(k)
                for v in conj_dict[k]:
                    p = pair.copy()
                    p[idx] = v
                    if p not in re_pairs:
                        re_pairs.append(p)

    re_pairs = handle_preposition_last(re_pairs)
    re_pairs = [triple_first(t, item, pos_dict) for item in re_pairs]
    return re_pairs


def reconstruct_conj(pairs, conj_pair):
    def judge_in(s, pair):
        for p in pair:
            if s in p:
                return True
        return False
    re_pairs = [pairs[0]]
    hit_conj_pair = []
    for pair in pairs[1:]:
        if judge_in(conj_pair[0], pair):
            hit_conj_pair.append(pair)
        elif judge_in(conj_pair[1], pair):
            hit_conj_pair.append(pair)
        else:
            re_pairs.append(pair)
    return  re_pairs + hit_conj_pair if len(hit_conj_pair) > 0 else re_pairs# [[a, b], [e, f, g], [[[q1, q2, q3], [j1, j2, j3]]]]

def parse_be_sentence(s):
    s = clean_scene(s)
    s = clean_be(s)

    words = nltk.word_tokenize(s)
    if words[-1] == '?':
        words = words[:-1]
    s = ' '.join([w.lower() for w in words])
    pairs = []
    q_type, q_list =  re_consturct_q(s)

    q_list = re_construct_VB_end(q_list)
    q_list = re_construct_item_kind(q_list)
    conj_pair = []
    for q in q_list:
        pairs_, pos_dict, conj_dict = pares_sentence(q)
        pairs_ = rel_chunk(pairs_, s)
        pairs_ = re_pairs(pairs_, words, conj_dict, pos_dict)
        pairs = pairs + pairs_

        if len(conj_pair) == 0 and len(conj_dict) > 0:
            for k in conj_dict:
                conj_pair.append([k, conj_dict[k].pop()])
                break
    pairs = cut_redundance(pairs)
    if q_type == 0 or q_type == 1:
        pairs = [['yes', 'no']] + pairs
    else:
        pairs = conj_pair + pairs
    if q_type == 1 or q_type == 2:
        pairs = reconstruct_conj(pairs, conj_pair[0])
    return pairs



if __name__ == '__main__':
    print(parse_be_sentence('Is there a towel rack visible?'))