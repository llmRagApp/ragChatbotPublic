import random
import math
import numpy as np
import logging
from datetime import datetime

import torch
from torch.utils.data import DataLoader
from datasets import load_dataset
from sentence_transformers import SentenceTransformer, models, LoggingHandler, losses, util
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from sentence_transformers.readers import InputExample
from sentence_transformers.datasets import NoDuplicatesDataLoader

pretrained_model_name = 'klue/roberta-base'
nli_num_epochs = 1
sts_num_epochs = 4
train_batch_size = 32

nli_model_save_path = 'output/training_nli_by_MNRloss_'+pretrained_model_name.replace("/", "-")+'-'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
sts_model_save_path = 'output/training_sts_continue_training-'+pretrained_model_name.replace("/", "-")+'-'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# load KLUE-NLI Dataset
klue_nli_train = load_dataset("klue", "nli", split='train')

print('Length of Train : ',len(klue_nli_train))

def make_nli_triplet_input_example(dataset):
    '''
    Transform to Triplet format and InputExample
    '''
    # transform to Triplet format
    train_data = {}
    def add_to_samples(sent1, sent2, label):
        if sent1 not in train_data:
            train_data[sent1] = {'contradiction': set(), 'entailment': set(), 'neutral': set()}
        train_data[sent1][label].add(sent2)

    for i, data in enumerate(dataset):
        sent1 = data['hypothesis'].strip()
        sent2 = data['premise'].strip()
        if data['label'] == 0:
            label = 'entailment'
        elif data['label'] == 1:
            label = 'neutral'
        else:
            label = 'contradiction'

        add_to_samples(sent1, sent2, label)
        add_to_samples(sent2, sent1, label) #Also add the opposite

    # transform to InputExmaples
    input_examples = []
    for sent1, others in train_data.items():
        print('sent1 : ', sent1, 'others : ',others)
        if len(others['entailment']) > 0 and len(others['contradiction']) > 0:  ## entail과 contradiction이 모두 채워졌을때, exampes에 추가
            input_examples.append(InputExample(texts=[sent1, random.choice(list(others['entailment'])), random.choice(list(others['contradiction']))]))
            input_examples.append(InputExample(texts=[random.choice(list(others['entailment'])), sent1, random.choice(list(others['contradiction']))]))

    return input_examples

# Train Dataloader
nli_train_dataloader = NoDuplicatesDataLoader( # avoid duplicates within a batch
    nli_train_examples,
    batch_size=train_batch_size,
)


# load KLUE-STS Dataset

# 실습에 사용할 데이터는 klue-sts 데이터셋이다. 해당 데이터셋은 'train', 'validation'으로만 구성되어있지만, 'train'셋의 10%를 샘플링하여 validation 으로 사용하고 기존 'validation'을 test용도로 사용하였다.

klue_sts_train = load_dataset("klue", "sts", split='train[:90%]')
klue_sts_valid = load_dataset("klue", "sts", split='train[-10%:]') # train의 10%를 validation set으로 사용
klue_sts_test = load_dataset("klue", "sts", split='validation')

print('Length of Train : ',len(klue_sts_train))
print('Length of Valid : ',len(klue_sts_valid))
print('Length of Test : ',len(klue_sts_test))


def make_sts_input_example(dataset):
    '''
    Transform to InputExample
    '''
    input_examples = []
    for i, data in enumerate(dataset):
        sentence1 = data['sentence1']
        sentence2 = data['sentence2']


        score = (data['labels']['label']) / 5.0  # normalize 0 to 5
        input_examples.append(InputExample(texts=[sentence1, sentence2], label=score))

    return input_examples


# 학습에 사용할 train 데이터는 배치학습을 위해 DataLoader()로 묶고, EmbeddingSimilarityEvaluator() 을 통해 학습 시 사용할 validation 검증기와 모델 평가 시 사용할 test 검증기를 만들었다.


# Train Dataloader
sts_train_dataloader = DataLoader(
    sts_train_examples,
    shuffle=True,
    batch_size=train_batch_size,
)

# Evaluator by sts-validation
val_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
    sts_valid_examples,
    name="sts-val",
)

# Evaluator by sts-test
test_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
    sts_test_examples,
    name="sts-test",
)

# Pooling 레이어의 경우, 논문 실험 기준 가장 성능이 좋은 mean pooling을 정의하였다.

# Load Embedding Model
embedding_model = models.Transformer(
    model_name_or_path=pretrained_model_name,
    max_seq_length=512,
    do_lower_case=True
)

# Only use Mean Pooling -> Pooling all token embedding vectors of sentence.
pooling_model = models.Pooling(
    embedding_model.get_word_embedding_dimension(),
    pooling_mode_mean_tokens=True,
    pooling_mode_cls_token=False,
    pooling_mode_max_tokens=False,
)

model = SentenceTransformer(modules=[embedding_model, pooling_model])

from sentence_transformers import losses

# config
# 논문과 동일하게 1 epochs, learning-rate warm-up의 경우 train의 10%를 설정
sts_num_epochs = 1
train_batch_size = 32
nli_model_save_path = 'output/training_nli_by_MNRloss_'+pretrained_model_name.replace("/", "-")+'-'+datetime.now()

# Use MultipleNegativesRankingLoss
train_loss = losses.MultipleNegativesRankingLoss(model)

# warmup steps
warmup_steps = math.ceil(len(nli_train_examples) * nli_num_epochs / train_batch_size * 0.1) #10% of train data for warm-up, learning-rate warm-up 지정 (설명은 아래)
logging.info("Warmup-steps: {}".format(warmup_steps))

# Training
model.fit(
    train_objectives=[(nli_train_dataloader, train_loss)],
    evaluator=val_evaluator,
    epochs=nli_num_epochs,
    evaluation_steps=int(len(nli_train_dataloader)*0.1),
    warmup_steps=warmup_steps,
    output_path=nli_model_save_path,
    use_amp=False       #Set to True, if your GPU supports FP16 operations
)



