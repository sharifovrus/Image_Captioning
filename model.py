import torch
import torch.nn as nn
import torchvision.models as models


class EncoderCNN(nn.Module):
    def __init__(self, embed_size):
        super(EncoderCNN, self).__init__()
        resnet = models.resnet50(pretrained=True)
        for param in resnet.parameters():
            param.requires_grad_(False)
        
        modules = list(resnet.children())[:-1]
        self.resnet = nn.Sequential(*modules)
        self.embed = nn.Linear(resnet.fc.in_features, embed_size)

    def forward(self, images):
        features = self.resnet(images)
        features = features.view(features.size(0), -1)
        features = self.embed(features)
        return features
    

class DecoderRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers=1):
        super(DecoderRNN, self).__init__()
        self.embed_size = embed_size
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.num_layers = num_layers
        self.embed = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, vocab_size)
        pass
    
    def forward(self, features, captions):
        captions = captions[:, :-1]
        embeddings = self.embed(captions)
        embeddings = torch.cat((features.unsqueeze(1), embeddings),1)
        hiddens,_ = self.lstm(embeddings)
        outputs = self.linear(hiddens)
        return outputs
        pass

    def sample(self, inputs, states=None, max_len=20):
        x = []
        for i in range(max_len):
            lstm_out, states = self.lstm(inputs, states)
            lstm_out = lstm_out.squeeze(1)
            outputs = self.linear(lstm_out)
            maximum = torch.max(outputs, 1)[1]
            x.append(maximum.item())
            inputs = self.embed(maximum).unsqueeze(1)
        return x
        pass
        " accepts pre-processed image tensor (inputs) and returns predicted sentence (list of tensor ids of length max_len) "
        