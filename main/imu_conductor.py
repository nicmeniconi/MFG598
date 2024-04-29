################################################################################################
### Prints network output for <sec> seconds and sends to MIDI (see utils.record_window_utils ###
# % python print_imu.py --sec=number of seconds to keep on (float)
###############################################################################################

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import matplotlib.pyplot as plt
import argparse
import asyncio
import numpy as np
import csv
import pandas as pd 
import scipy as sp
from scipy import special


import torch.optim as optim
import torch.utils.data
import torch.backends.cudnn as cudnn
import torchvision
from torchvision import transforms as transforms
from torch import nn

from utils.args import *


SEED = 1337
np.random.seed(SEED)
torch.manual_seed(SEED)

number_activities=4
window_len=30
model_dir = '/Users/niccolomeniconi/Dropbox (ASU)/Mac/Documents/Arduino/MFG598_project/main/utils/models'
enc_model =f'best_FCN_{number_activities}_enc_model.pth'# 'Encoder1d'
dec_model = f'best_FCN_{number_activities}_dec_model.pth' #'DecoderLin1d'
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

mean = []
std = []

with open(model_dir+'/mean_and_std.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # print(row['loss'], row['accuracy'])
        mean.append(row['mean'])
        std.append(row['std'])

mean = mean[0].strip('[]')
mean = np.fromstring(mean, sep=',')
mean_train = np.array([mean[0], mean[0], mean[0], mean[1], mean[1], mean[1]])
std = std[0].strip('[]')
std = np.fromstring(std, sep=',')
std_train = np.array([std[0], std[0], std[0], std[1], std[1], std[1]])


enc_pth = f'{model_dir}/{enc_model}'
dec_pth = f'{model_dir}/{dec_model}'

class EncoderFCN(nn.Module): # has same conv layers as CNN_3d
    
    def __init__(self, window_len, verbose):
        super().__init__()

        self.encoder_lin = nn.Sequential(
            # First linear layer
            nn.Linear(6*window_len, 125),
            nn.ReLU(True),
            # Second linear layer
            nn.Linear(125, 64),
            nn.ReLU(True),
            nn.Linear(64, 32),
            nn.ReLU(True),
            )

        ### Flatten layer
        self.flatten = nn.Flatten(start_dim=1)
        
    def forward(self, x_in, verbose = False):
        if verbose: print('x_in shape:', x_in.shape)
        x_fl = self.flatten(x_in)
        x_fl = torch.unsqueeze(x_fl, 1)
        if verbose: print('x_fl shape:', x_fl.shape)
        x_lin = self.encoder_lin(x_fl)
        x_out = x_lin
        if verbose: print("x_out shape:", x_out.shape)
        return x_out

class DecoderFCN(nn.Module):
    
    def __init__(self, window_len, verbose, number_activities):
        super().__init__()

        self.decoder_lin = nn.Sequential(
            # First linear layer
            nn.Linear(32, 16),
            nn.ReLU(True),
            # Second linear layer
            nn.Linear(16, number_activities), 
            )

    def forward(self, x_in, verbose = False):
        if verbose: print('decoder input shape:', x_in.shape)
        x_dec = self.decoder_lin(x_in)
        if verbose: print('x_dec shape:', x_dec.shape)
        x = torch.sigmoid(x_dec)
        x_uns = torch.squeeze(x, 1)
        x_out = x_uns
        if verbose: print("x_out shape:", x_out.shape)
        
        return x_out

encoder = EncoderFCN(window_len=window_len, verbose=False)
decoder = DecoderFCN(window_len=window_len, number_activities=number_activities, verbose=False)
encoder.load_state_dict(torch.load(enc_pth))
decoder.load_state_dict(torch.load(dec_pth))

def input_norm(input, mean_train, std_train):
    input_df = np.array(input).T
    input_norm = (input_df - mean_train[:, None]) / std_train[:, None]
    return input_norm

def deploy_model(encoder, decoder, device, input):

    encoder.eval()
    decoder.eval()
    
    input_image = torch.from_numpy(input)
    input_image = torch.unsqueeze(input_image, 0)
    input_image = input_image.type(torch.FloatTensor)

    with torch.no_grad(): 

        image = input_image.to(device)
        encoded_data = encoder(image)
        label_out = decoder(encoded_data)
        label_out = torch.squeeze(label_out, 1)
        label_output = np.array(label_out.cpu())[0] 
        label_out_softmax = special.softmax(label_output)
        prediction_idx = np.where(label_out_softmax == np.max(label_out_softmax))        

    return prediction_idx[0][0] #, np.array(image_noisy.cpu())#, val_loss.data



recording = [] 

def handler(address, *args):
    recording.append(args)
    global model_out
    if len(recording) == window_len+1: # window_len + header
        recording.pop(0)
        recording_norm = input_norm(input=recording, mean_train=mean_train, std_train=std_train)
        model_out = deploy_model(encoder, decoder, device, input=recording_norm)
        print("MODEL OUT:", model_out)
        
    return recording



args = args_return()
dispatcher = Dispatcher()
dispatcher.map("/m5", handler)

async def main_loop():
    """Example main loop that runs for <sec> seconds before finishing"""

    sec = args.sec # recording length in seconds
    print(f"\nRECORDING START\n--------------")
    await asyncio.sleep(sec) 

    return recording


async def init_main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    A = await main_loop()  # Enter main loop of program
    print("Buffer shape:", np.array(A).shape)
    transport.close()  # Clean up serve endpoint
    


asyncio.run(init_main())