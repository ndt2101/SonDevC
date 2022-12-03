import re
import pandas as pd
import numpy as np
import pickle

from gensim.models.phrases import Phrases, Phraser
from gensim.models import Word2Vec
from gensim.models import KeyedVectors

#process materials:
ev_path = "processors/Englishwords.xlsx"
sf_path =  "processors/Shortform.xlsx"
stopwords_vn_path = "processors/stopwords_vn_dash.txt"
englishwords = pd.read_excel(ev_path, index_col= "English")
shortform = pd.read_excel(sf_path, index_col= "Short")

#phraser for word2vec
bigram = Phraser.load("saves/bigram.pkl")

#word2idx
word2idx = pickle.load(open("saves/word2idx.pickle", "rb"))

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)
def preprocess(text):
  #bỏ tag html và emoji
  text = re.sub('<[^>]*>', '', text)
  text = deEmojify(text)

  #thay chữ cái viết hoa thành viết thường
  text = text.lower()

  #xóa dấu ngắt câu, xóa link và các chữ có chứa chữ số
  clean_text = []
  punc_list = r'.,;:?!\|/&@`~()-_@#$%^*\'\"'
  for w in (text.split()):
    if "http" in w:
      continue
    clean_text.append(w)
  text = ' '.join(clean_text)
  for punc in punc_list:
    text = text.replace(punc, ' ')

  #xóa bỏ các chữ cái lặp liên tiếp nhau (đỉnhhhhhhhhhh, vipppppppppppppppp)
  length = len(text)
  char = 0
  while char <length-1:
    if text[char] == text[char+1]:
      text = text[:char]+text[char+1:]
      #print(text)
      length-=1
      continue
    char+=1  
  numbers = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
  #chuyển đổi các từ tiếng anh và viết tắt thông dụng sang tiếng Việt chuẩn:
  text_split = text.split()
  for i, w in enumerate(text_split):
    if w in englishwords.index:
      text_split[i] = str(englishwords.loc[w, "Vietnamese"])
    if w in shortform.index:
      text_split[i] = str(shortform.loc[w, "Long"])
    if w.isdigit():
      text_split[i] = ' '.join([numbers[int(c)] for c in w]) 
  text = ' '.join(text_split)

  #loại bỏ tất cả các kí tự đặc biệt còn lại
  digits_and_characters = 'aăâbcdđeêfghijklmnoôơpqrstuưvxywzáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ0123456789 '
  text = ''.join([i for i in text if i in digits_and_characters])
  return text

#split all sentences in corpus
def splitCorpus(corpus):
  t = [sentence.split() for sentence in corpus]
  return t
#join all splited sentences to a big text document
def joinAllSplit(tokenized_sentences):
  sentences = [' '.join(sentence) for sentence in tokenized_sentences]
  return ' '.join(sentences)

#below function get performe preprocessing and remove unknown words
def prepros(sentences):
  new_sentences = [preprocess(sentence) for sentence in sentences]
  splitted_sentences = splitCorpus(new_sentences)
  new = []
  for sentence in bigram[splitted_sentences]:
    new_sentence = ' '.join([word for word in sentence if word in word2idx.keys()])
    new.append(new_sentence)
  return new

#convert words to numbers
def sentenceToInt(sentences):
  #print(sentences)
  int_sentences = []
  for sentence in sentences:
    int_sentence = [word2idx[word] for word in sentence.split()]   
    int_sentences.append(int_sentence)
  return int_sentences

#pad int_sentences to the feature_leng
def padFeature(sentences, feature_leng = 50):
  smatrix = np.zeros((len(sentences), feature_leng))
  for sen_index, sentence in enumerate(sentences):
    padding = max(0, feature_leng - len(sentence))
    for word_index in range(feature_leng):
      if word_index < padding:
        smatrix[sen_index, word_index] = 0
      else:
        smatrix[sen_index, word_index] = sentence[word_index-padding]
  return smatrix

def process(sentences, feature_leng = 50):
  int_sentences = sentenceToInt(sentences)
  feature_matrix = padFeature(int_sentences, feature_leng = 50)
  return feature_matrix
