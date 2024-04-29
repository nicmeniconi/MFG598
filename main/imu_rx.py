####################################
### Prints data on terminal line ###
####################################

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import argparse
import asyncio
import numpy as np
import csv
import pandas as pd 
from utils.args import *



########################## Arguments import and handler function ##########################
args = args_return()
dispatcher = Dispatcher()
decimal_places=3

def print_handler_rx(address, *args):
    rounded_args = np.round(args, decimal_places)
    formatted_output = ["{: .3f}".format(num) if num >= 0 else "{:.3f}".format(num) for num in rounded_args]
    print(f"{address}: {formatted_output}")

###########################################################################

dispatcher.map("/m5", print_handler_rx)

async def main_loop():
    """Example main loop that runs for <sec> seconds before finishing"""

    sec = args.sec # recording length in seconds
    print(f"\nRECORDING START\n--------------")
    await asyncio.sleep(sec) 


async def init_main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
    await main_loop()  # Enter main loop of program
    transport.close()  # Clean up serve endpoint
    
asyncio.run(init_main())