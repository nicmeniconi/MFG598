####################################
### Records data window ###
####################################
import pandas as pd
import numpy as np
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
from utils.args import *

########################## Import run parameters ##########################
args = args_return()

recording = [] # buffer

def m5_handler(address, *args):
    # print(f"{address}: {args}")
    recording.append(args)
    return recording

dispatcher = Dispatcher()
dispatcher.map("/m5", m5_handler)
###########################################################################

def save_recording(recording, args):
    subject = args.subject
    activity = args.activity
    outpth = args.outpth
    trial = args.trial
    # rec_name = f"/{subject}_act{activity}_trial{trial}.csv" #_sampled window number
    rec_name = f"/{activity}/{subject}_trial{trial}.csv" #_sampled window number
    recording = np.array(recording)
    dict = {'aX': recording[:,0], 
            'aY': recording[:,1], 
            'aZ': recording[:,2], 
            'gX': recording[:,3], 
            'gY': recording[:,4], 
            'gZ': recording[:,5], 
            }

    df = pd.DataFrame(dict) 
    df.to_csv(outpth+rec_name) 
    print(f"RECORDING DONE.")
    print(f"Recording shape: {recording.shape}")
    print(f"Check {outpth+rec_name} for recording output.\n\n")

    
async def main_loop():
    """Example main loop that runs for <sec> seconds before finishing"""

    sec = args.sec # recording length in seconds
    print(f"\nRECORDING START\n--------------")
    await asyncio.sleep(sec) 

    return recording


async def init_main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    # recording = await main_loop()  # Enter main loop of program
    recording = await main_loop()
    save_recording(recording, args)
    # save_recording_thresh(threshold_recording, args)
    transport.close()  # Clean up serve endpoint
    


asyncio.run(init_main())