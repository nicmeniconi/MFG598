import argparse

# TODO: write function that grabs mean and std vector from a text file output from the training loop

def args_return():

    parser = argparse.ArgumentParser()

    parser.add_argument("--SEED",
        type = int, 
        default=1137, 
        help="Set randomness seed") 

    parser.add_argument("--ip",
        type = str, 
        default="192.168.8.142", 
        help="The ip to listen on") # conductorRX (goodlife) router IP = 192.168.8.142
                                    

    parser.add_argument("--port",
        type=int, 
        default=8000, 
        help="The port to listen on") # Arduino TX port = 8000

    parser.add_argument("--outpth", # IMU data folder, target folder for data collection. Data used to train model.
        type=str, 
        default='../data_collection',
        help="Recording out directory")

    parser.add_argument("--subject",
        type=str, 
        default='NicM', 
        help="Subject being recorded, [convention: 3 letter first name + 1 letter last name]")

    parser.add_argument("--trial",
        type=int, 
        default=1, 
        help="trial(s) in recording session")

    parser.add_argument("--window_len",
        type=int, 
        default=30, 
        help="input window length of model (samples)")

    parser.add_argument("--activity",
        type=str, 
        default='junk_activity', 
        help="Activity label(s)")

    parser.add_argument("--sec",
        type =float, 
        default=5., 
        help="Print data for <sec> amount of seconds") # TODO: does not work, only saves last recording

    parser.add_argument("--threshold",
        type=float, 
        default=1.7, 
        help="Acceleration magnitude thresholding (output True if aMag >= threshold)")

    parser.add_argument("--model_dir", # IMU data folder, target folder for data collection. Data used to train model.
        type=str, 
        default='/Users/niccolomeniconi/Dropbox (ASU)/Mac/Documents/Arduino/Conductor/main/utils/data/modeling_conduct3', 
        help="Recording out directory")

    parser.add_argument("--mean_train",
        type = list, 
        default=[0.05020382,  0.04779168,  0.06841457, -1.66366605, -1.76010894,  0.36274367], 
        help="mean vector of training dataset across aX,Y,Z, gX,Y,Z channels") 

    parser.add_argument("--std_train",
        type = list, 
        default=[0.01163283, 0.01594797, 0.01679968, 1.54755639, 1.52335691, 1.66935455], 
        help="std vector of training dataset across aX,Y,Z, gX,Y,Z channels") 

    return parser.parse_args()


    
