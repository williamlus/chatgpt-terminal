import argparse, multiprocessing
from chat_util import *
from translator import translate_util

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", default=False, help="Resume a previous chat session. (Default: False)")
    parser.add_argument("--customize_system", action="store_true", default=False, help="Customize the system prompt. (Default: False)")
    parser.add_argument("--nogui", action="store_true", default=False, help="Run the chatbot without GUI. (Default: False)")
    parser.add_argument("-lang", type=str, default="en", help="Language of the chat. (Default: en)")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    multiprocessing.freeze_support()
    args=parse_args()
    setup_theme()
    init_globals(args.lang)
    setup()
    setup_request_process()
    if args.nogui: disable_gui()
    if args.resume:
        try:
            msg_arr=read_msg_arr()
            msg_arr=resume_chat(msg_arr)
        except Exception as e:
            print(e)
            print(translate_util("Unable to resume chat. Starting a new chat session.",lang=args.lang), flush=True)
            msg_arr=start_chat(args.customize_system)
    else:
        msg_arr=start_chat(args.customize_system)
    
    print(translate_util("Save the chat log to a file if you want to resume the chat later.",lang=args.lang), flush=True)
    try:
        save_msg_arr(msg_arr)
    except Exception as e:
        print(translate_util("Unable to save chat log.",lang=args.lang), flush=True)
    except: pass
    finally:
        terminate_request_process()
        sys.exit(0)