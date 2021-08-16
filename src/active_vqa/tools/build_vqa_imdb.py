import numpy as np
import json
import os
from collections import defaultdict
import sys
from Utils import text_processing
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, required=True, help="data directory")
parser.add_argument("--out_dir", type=str, required=True, help="imdb output directory")
args = parser.parse_args()

data_dir = args.data_dir
out_dir = args.out_dir


vocab_answer_file = os.path.join(out_dir, 'answers_vqa.txt')
gt_layout_file = os.path.join(out_dir, 'gt_layout_%s_new_parse.npy')

annotation_file = os.path.join(data_dir, 'image_%s_annotations.json')
question_file = os.path.join(data_dir, 'image_%s_questions.json')


#image_dir = '../vqa-dataset/Images/%s/'
#feature_dir = './resnet_res5c/%s/'



answer_dict = text_processing.VocabDict(vocab_answer_file)
valid_answer_set = set(answer_dict.word_list)

def extract_answers(q_answers):
    all_answers = [answer["answer"] for answer in q_answers]
    valid_answers = [a for a in all_answers if a in valid_answer_set]
    return all_answers, valid_answers

def build_imdb(image_set):
    print('building imdb %s' % image_set)
    if image_set in ['train', 'val']:
        load_answer = True
        load_gt_layout = True
        with open(annotation_file % image_set) as f:
            annotations = json.load(f)["annotations"]
            qid2ann_dict = {ann['question_id']: ann for ann in annotations}
        qid2layout_dict = np.load(gt_layout_file % image_set)[()]
    else:
        load_answer = False
        load_gt_layout = False
    with open(question_file % image_set) as f:
        questions = json.load(f)['questions']
    coco_set_name = image_set.replace('-dev', '')
    #abs_image_dir = os.path.abspath(image_dir % coco_set_name)
    #abs_feature_dir = os.path.abspath(feature_dir % coco_set_name)
    image_name_template = 'img_' + coco_set_name + '_%010d'
    imdb = [None]*len(questions)

    unk_ans_count = 0
    for n_q, q in enumerate(questions):
        if (n_q+1) % 10000 == 0:
            print('processing %d / %d' % (n_q+1, len(questions)))
        image_id = q['image_id']
        question_id = q['question_id']
        image_name = image_name_template % image_id
        #image_path = os.path.join(abs_image_dir, image_name + '.jpg')
        feature_path = image_name + '.npy'
        #feature_path = os.path.join(abs_feature_dir, image_name + '.npy')
        question_str = q['question']
        question_tokens = text_processing.tokenize(question_str)

        iminfo = dict(image_name=image_name,
              image_id=image_id,
              question_id=question_id,
              feature_path=feature_path,
              question_str=question_str,
              question_tokens=question_tokens)

        # load answers
        if load_answer:
            ann = qid2ann_dict[question_id]
            all_answers, valid_answers = extract_answers(ann['answers'])
            if len(valid_answers) == 0:
                valid_answers = ['<unk>']
                unk_ans_count += 1
            iminfo['all_answers'] = all_answers
            iminfo['valid_answers'] = valid_answers

        if load_gt_layout:
            gt_layout_tokens = qid2layout_dict[question_id]
            iminfo['gt_layout_tokens'] = gt_layout_tokens

        imdb[n_q] = iminfo
    print('total %d out of %d answers are <unk>' % (unk_ans_count, len(questions)))
    return imdb

imdb_trainq = build_imdb('trainq')
imdb_valq = build_imdb('valq')
imdb_testq = build_imdb('testq')
imdb_test_devq = build_imdb('test-devq')


imdb_dir = os.path.join(out_dir,'imdb')
os.makedirs(imdb_dir, exist_ok=True)
np.save(os.path.join(imdb_dir, 'imdb_trainq.npy'), np.array(imdb_trainq))
np.save(os.path.join(imdb_dir, 'imdb_valq.npy'), np.array(imdb_valq))
np.save(os.path.join(imdb_dir, 'imdb_trainvalq.npy'), np.array(imdb_trainq + imdb_valq))
np.save(os.path.join(imdb_dir, 'imdb_testq.npy'), np.array(imdb_testq))
np.save(os.path.join(imdb_dir, 'imdb_test-devq.npy'), np.array(imdb_test_devq))
