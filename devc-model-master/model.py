import torch
import re
import pandas as pd
import pickle
from preprocess import prepros, process
from SentimentLSTM import SentimentLSTM

#word2idx
word2idx = pickle.load(open("saves/word2idx.pickle", "rb"))

# Load model
emb_matrix = torch.zeros((len(word2idx)+1,200))
model = SentimentLSTM(output_size= 3, embedding_dim=200, hidden_dim= 128, n_layers= 2, n_cell = 50, emb_matrix=emb_matrix, drop_prob = 0.2)
state = torch.load('model_state.pt')
model.load_state_dict(state)

# Predict
def predict(net, comments, sequence_length=50, train_on_gpu = False):
    
    net.eval()
    #preprocess:
    cleaned_comments = prepros(comments)
    #print(cleaned_comments)
    #process:
    features = process(cleaned_comments)
    #print(features)
    feature_tensor = torch.from_numpy(features)
    feature_tensor = feature_tensor.type(torch.LongTensor)
    batch_size = feature_tensor.size(0)
    #print(feature_tensor.size(0))
    # initialize hidden state
    h = net.init_hidden(batch_size)
    
    if(train_on_gpu):
        feature_tensor = feature_tensor.cuda()
    
    # get the output from the model
    output, h = net(feature_tensor, h)
    #print(output.squeeze())
    # convert output probabilities to prediction
    pred = torch.argmax(output, dim = 1)
    # printing output value, before rounding
    #print(pred)
    return pred, output, cleaned_comments

#
#   Cho test vào đây. Test là 1 list toàn comment. Trả về 1 list label. map list label vào original data để update lên db với label mới.
#   Goi ham nay de lay dc predictions
#
def getReviewPredictList(comments):
    # Read test dataset
    pred, output, cleaned_comments = predict(model, comments= comments, sequence_length= 50, train_on_gpu= False)

    list_pred = pred.tolist()
    # for i, n in enumerate(list_pred):
    #     if n == 0:
    #         list_pred[i] = '=>  tiêu cực'
    #     elif n == 1:
    #         list_pred[i] = '=>  trung lập'
    #     else:
    #         list_pred[i] = "=>  tích cực"
        # for i in range (400):
            # print(comments[i][:50], "=>", cleaned_comments[i][:50], list_pred[i])

    return list_pred


