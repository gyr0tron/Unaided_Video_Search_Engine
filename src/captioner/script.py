from celery import Celery
from celery.schedules import crontab
import shutil
app = Celery('script', broker="redis://localhost:6379/0")
# disable UTC so that Celery can use local time
app.conf.enable_utc = False


@app.task
def scheduled_task():
    import subprocess
    import os
    from shelljob import proc

    input_video_paths = list()
    input_video_names = list()
    PROCESSED_PATH = '../data/processed/'
    STATS_FILE_PATH = f'stats.csv'
    RAW_PATH = '../data/raw/'
    if os.path.exists(STATS_FILE_PATH):
        os.remove(STATS_FILE_PATH)

    with os.scandir(RAW_PATH) as entries:
        for entry in entries:
            input_video_names.append(entry.name)
            input_video_paths.append(f'../data/raw/{entry.name}')

    processed_images_path = f'{PROCESSED_PATH}images'
    processed_scenes_path = f'{PROCESSED_PATH}scenes'

    # process_cli = f'scenedetect --input {input_video_paths[0]} --output {PROCESSED_PATH} --stats {STATS_FILE_PATH} detect-content --min-scene-len 30 --threshold 27 list-scenes save-images --output {processed_images_path} --num-images 1 split-video --output {processed_scenes_path}'
    # subprocess.Popen(process_cli, stdout=subprocess.PIPE).stdout.read()

    process_cli = f'scenedetect --input {input_video_paths[0]} --output {PROCESSED_PATH} --stats {STATS_FILE_PATH} detect-content --min-scene-len 30 --threshold 27 list-scenes save-images --output {processed_images_path} --num-images 1 split-video --output {processed_scenes_path}'
    # g = proc.Group()
    # p = g.run(process_cli)

    os.system(process_cli)
    shutil.move(input_video_paths[0], "../data/processed")

    from keras.utils import to_categorical
    from keras.preprocessing.sequence import pad_sequences
    from keras.preprocessing.text import Tokenizer
    from keras.applications.inception_v3 import preprocess_input
    from keras import optimizers
    from keras import Input, layers
    from keras.models import Model
    from keras.preprocessing import image
    from keras.applications.inception_v3 import InceptionV3
    from keras.layers.merge import add
    from keras.layers.wrappers import Bidirectional
    from keras.optimizers import Adam, RMSprop
    from keras.layers import LSTM, Embedding, TimeDistributed, Dense, RepeatVector, Activation, Flatten, Reshape, concatenate, Dropout, BatchNormalization
    from keras.models import Sequential
    from keras.preprocessing import sequence
    from time import time
    from pickle import dump, load
    import glob
    from PIL import Image
    import string
    import numpy as np
    from numpy import array
    import pandas as pd
    import matplotlib.pyplot as plt

    def load_text_captions(filename):
        file = open(filename, 'r', encoding="ISO-8859-1")
        text = file.read()
        file.close()
        return text

    filename = "dataset/30k_captions.txt"
    text_captions = load_text_captions(filename)

    def load_filename_dict(text_captions):
        dictonary = dict()
        for line in text_captions.split('\n'):
            tokens = line.split()
            if len(line) < 2:
                continue
            # first token = image id
            image_id, image_desc = tokens[0], tokens[1:]
            # remove .jpg
            image_id = image_id.split('.')[0]
            # description to string
            image_desc = ' '.join(image_desc)
            if image_id not in dictonary:
                dictonary[image_id] = list()
            dictonary[image_id].append(image_desc)
        return dictonary

    descriptions = load_filename_dict(text_captions)
    print('Loaded descriptions: %d ' % len(descriptions))

    def clean_descriptions(descriptions):
        # translation table for removing punctuation; third param for removal
        table = str.maketrans('', '', string.punctuation)
        for key, desc_list in descriptions.items():
            for i in range(len(desc_list)):
                desc = desc_list[i]
                desc = desc.split()
                desc = [word.lower() for word in desc]
                # using trans table to remove punctuation from each token
                desc = [w.translate(table) for w in desc]
                # remove s/a
                desc = [word for word in desc if len(word) > 1]
                # words with nos
                desc = [word for word in desc if word.isalpha()]
                desc_list[i] = ' '.join(desc)

    # clean descriptions
    clean_descriptions(descriptions)

    # vocab words

    def to_vocab(descriptions):
        # all description strings
        all_desc = set()
        for key in descriptions.keys():
            [all_desc.update(d.split()) for d in descriptions[key]]
        return all_desc

    # summarize vocabulary
    vocabulary = to_vocab(descriptions)
    print('Vocabulary Size: %d' % len(vocabulary))

    def save_descriptions(descriptions, filename):
        lines = list()
        for key, desc_list in descriptions.items():
            for desc in desc_list:
                lines.append(key + ' ' + desc)
        data = '\n'.join(lines)
        file = open(filename, 'w')
        file.write(data)
        file.close()

    save_descriptions(descriptions, 'dataset/descriptions.txt')

    # load train ids

    def load_set(filename):
        doc = load_text_captions(filename)
        dataset = list()
        for line in doc.split('\n'):
            # skip empty lines
            if len(line) < 1:
                continue
            identifier = line.split('.')[0]
            dataset.append(identifier)
        return set(dataset)

    filename = 'dataset/flickr30k_train.txt'
    train = load_set(filename)
    print('Dataset: %d' % len(train))

    def load_clean_descriptions(filename, dataset):
        # load document
        doc = load_text_captions(filename)
        descriptions = dict()
        for line in doc.split('\n'):
            tokens = line.split()
            image_id, image_desc = tokens[0], tokens[1:]
            if image_id in dataset:
                # create list
                if image_id not in descriptions:
                    descriptions[image_id] = list()
                desc = 'startseq ' + ' '.join(image_desc) + ' endseq'
                # store
                descriptions[image_id].append(desc)
        return descriptions

    train_descriptions = load_clean_descriptions(
        'dataset/descriptions.txt', train)
    print('Descriptions: train=%d' % len(train_descriptions))

    # all training captions
    all_train_captions = []
    for key, val in train_descriptions.items():
        for cap in val:
            all_train_captions.append(cap)
    len(all_train_captions)

    # words appearing at least 10 times
    word_count_threshold = 10
    word_counts = {}
    nsents = 0
    for sent in all_train_captions:
        nsents += 1
        for w in sent.split(' '):
            word_counts[w] = word_counts.get(w, 0) + 1

    vocab = [w for w in word_counts if word_counts[w] >= word_count_threshold]
    print('preprocessed words %d -> %d' % (len(word_counts), len(vocab)))

    # inception v3 model
    model = InceptionV3(weights='imagenet')

    # remove the last layer (output layer) from inception v3; [-1] = last layer's output, [-2] = last layer
    model_new = Model(model.input, model.layers[-2].output)

    def preprocess(image_path):
        # 299x299 needed by the inception v3 model
        img = image.load_img(image_path, target_size=(299, 299))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        return x

    # encode image into a vector of size (2048, )

    def encode(image):
        image = preprocess(image)
        fea_vec = model_new.predict(image)
        fea_vec = np.reshape(fea_vec, fea_vec.shape[1])
        return fea_vec

    # all the images
    images = 'dataset/flickr30k-images/'
    img = glob.glob(images + '*.jpg')

    train_images_file = 'dataset/flickr30k_train.txt'
    train_images = set(open(train_images_file, 'r').read().strip().split('\n'))

    train_img = []

    for i in img:
        if i[len(images):] in train_images:
            train_img.append(i)

    test_images_file = 'dataset/flickr30k_test.txt'
    test_images = set(open(test_images_file, 'r').read().strip().split('\n'))

    # Create a list of all the test images with their full path names
    test_img = []

    for i in img:
        if i[len(images):] in test_images:
            test_img.append(i)

    train_features = load(
        open("dataset/Pickle/encoded_train_images.pkl", "rb"))
    print('Photos: train=%d' % len(train_features))

    # word to index and vice versa
    ixtoword = {}
    wordtoix = {}

    ix = 1
    for w in vocab:
        wordtoix[w] = ix
        ixtoword[ix] = w
        ix += 1
    vocab_size = len(ixtoword) + 1  # one for appended 0's

    def to_lines(descriptions):
        all_desc = list()
        for key in descriptions.keys():
            [all_desc.append(d) for d in descriptions[key]]
        return all_desc

    def max_length(descriptions):
        lines = to_lines(descriptions)
        return max(len(d.split()) for d in lines)

    # determine the maximum sequence length
    max_length = max_length(train_descriptions)
    print('Description Length: %d' % max_length)

    # Load Glove vectors
    glove_dir = 'dataset/glove'
    embeddings_index = {}
    f = open(os.path.join(glove_dir, 'glove.6B.200d.txt'), encoding="utf-8")

    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()
    print('Found %s word vectors.' % len(embeddings_index))

    embedding_dim = 200

    embedding_matrix = np.zeros((vocab_size, embedding_dim))

    for word, i in wordtoix.items():
        # if i < max_words:
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

    # image feature extractor model
    inputs1 = Input(shape=(2048,))
    fe1 = Dropout(0.5)(inputs1)
    fe2 = Dense(256, activation='relu')(fe1)
    # partial caption sequence model
    inputs2 = Input(shape=(max_length,))
    se1 = Embedding(vocab_size, embedding_dim, mask_zero=True)(inputs2)
    se2 = Dropout(0.5)(se1)
    se3 = LSTM(256)(se2)
    # decoder (feed forward) model
    decoder1 = add([fe2, se3])
    decoder2 = Dense(256, activation='relu')(decoder1)
    outputs = Dense(vocab_size, activation='softmax')(decoder2)
    # merge the two input models
    model = Model(inputs=[inputs1, inputs2], outputs=outputs)

    # graph.append(tf.get_default_graph())

    print(model.summary())

    # embedding matrix from pre-trained Glove
    model.layers[2].set_weights([embedding_matrix])
    model.layers[2].trainable = False

    model.compile(loss='categorical_crossentropy', optimizer='adam')
    model.load_weights('./model_weights/3/model_30_final.h5')
    images = 'dataset/flickr30k-images/'
    with open("dataset/Pickle/encoded_test_images.pkl", "rb") as encoded_pickle:
        encoding_test = load(encoded_pickle)

    def greedySearch(photo):
        in_text = 'startseq'
        for i in range(max_length):
            sequence = [wordtoix[w] for w in in_text.split() if w in wordtoix]
            sequence = pad_sequences([sequence], maxlen=max_length)
            yhat = model.predict([photo, sequence], verbose=0)
            yhat = np.argmax(yhat)
            word = ixtoword[yhat]
            in_text += ' ' + word
            if word == 'endseq':
                break
        final = in_text.split()
        final = final[1:-1]
        final = ' '.join(final)
        return final

    def disp_caption(img_to_cap):
        # global graph
        # with graph[0].as_default():
        from keras.preprocessing import image
        image_loc = img_to_cap
        img = image.load_img(image_loc, target_size=(299, 299))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        image = x
        fea_vec = model_new.predict(image)
        fea_vec = np.reshape(fea_vec, fea_vec.shape[1])
        image = fea_vec.reshape((1, 2048))
        # x = plt.imread(image_loc)
        # plt.imshow(x)
        caption_pre = greedySearch(image)
        return caption_pre

    images_paths = list()
    imgs_file_path = '../data/processed/images/'
    with os.scandir(imgs_file_path) as entries:
        for entry in entries:
            # images_paths.append(entry.name)
            images_paths.append(f'../data/processed/images/{entry.name}')

    # if __name__ == "__main__":
    import mysql.connector

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="UVSE"
    )

    mycursor = mydb.cursor()
    for location in images_paths:
        image_name = location[25:]
        print(image_name)
        vid_name_temp = image_name[:-7]
        vid_name = vid_name_temp + ".mp4"
        print(vid_name)
        img_caption = disp_caption(location)
        print(img_caption)
        sql = "INSERT INTO captions (vid_name, img_name, caption) VALUES (%s, %s, %s)"
        val = (vid_name, image_name, img_caption)
        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")


app.conf.beat_schedule = {
    "scheduled-task": {
        "task": "script.scheduled_task",
        "schedule": crontab(minute="*/2")
    }
}
