import sys
import argparse
from chat_util import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", default=False, help="Resume a previous chat session. (Default: False)")
    parser.add_argument("--customize_system", action="store_true", default=False, help="Customize the system prompt. (Default: False)")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args=parse_args()
    setup_theme()
    setup()
    if args.resume:
        try:
            msg_arr=read_msg_arr()
            msg_arr=resume_chat(msg_arr)
        except Exception as e:
            print(e)
            print("Unable to resume chat. Starting a new chat session.", flush=True)
            msg_arr=start_chat(args.customize_system)
    else:
        msg_arr=start_chat(args.customize_system)
    
    print("Save the chat log to a file if you want to resume the chat later.", flush=True)
    try:
        save_msg_arr(msg_arr)
    except:
        print("Unable to save chat log.", flush=True)
        exit()