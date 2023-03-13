import openai, os, time, random, re, sys, colorama, threading, tempfile
import tkinter as tk
from tkinter import filedialog
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter
from colors import colors
from translator import translate_util
from key_bindings import get_key_bindings

is_insert_mode, response_completed, start_time, lang, translate, tmp_dir = None, None, None, None, None, None
msg_arr_cache={}

def init_globals(language:str="en"):
    global is_insert_mode, response_completed, start_time, lang, translate, tmp_dir
    is_insert_mode=False
    response_completed=""
    start_time=None
    lang=language
    translate=lambda msg: translate_util(msg, lang=lang)
    tmp_dir = tempfile.gettempdir()
    if not os.path.exists(tmp_dir+"/chatgpt-cache"): os.mkdir(tmp_dir+"/chatgpt-cache")
    tmp_dir=tmp_dir+"/chatgpt-cache/"

def log_msg(role:str, msg:str, role_color:str="blue", msg_color:str="reset"):
    if msg not in msg_arr_cache:
        msg_colored=color_code(msg, plain_color=msg_color)
        msg_arr_cache[msg]=msg_colored
    else: msg_colored=msg_arr_cache[msg]
    print(colors.get_color(role_color)+role+": ", end='', flush=True)
    print((colors.get_color(msg_color)+msg_colored).strip(), flush=True)

def print_msg_arr(msg_arr: list):
    for msg in msg_arr:
        if msg['role']=="user": log_msg(msg['role'], msg['content'], role_color="lightred", msg_color="orange")
        else: log_msg(msg['role'], msg['content'], role_color="blue")

def add_syntax_highlighting(code: str, language: str):
    language=programming_language_alias(language)
    lexer = get_lexer_by_name(language)
    formatter = Terminal256Formatter(style='monokai')
    highlighted_code = highlight(code, lexer, formatter)
    return highlighted_code

def contains(msg:str, arr:list):
    return [a for a in arr if a in msg.split()+[e[:-1] for e in msg.split() if len(e)>0]]

def get_programming_languages():
    try:
        with open(tmp_dir+"programming_languages.txt", "r") as f:
            langs=f.read().split("\n")
    except: 
        langs=['python','java','cpp', "csharp", "c++", "C++", "c#", "C#", "C", "c", "sql", "SQL"]
        with open(tmp_dir+"programming_languages.txt", "w") as f:
            f.write('\n'.join(langs))
    return langs

def add_programming_language(lang:str):
    langs=get_programming_languages()
    if lang not in langs: 
        with open(tmp_dir+"programming_languages.txt", "w") as f:
            f.write('\n'.join(langs+[lang]))

def programming_language_alias(lang:str):
    if lang in ["c++", "C++"]: return "cpp"
    elif lang in ["c#", "C#"]: return "csharp"
    else: return lang

def color_code(msg:str, plain_color:str):
    msg_arr=msg.split("```")
    for i in range(1,len(msg_arr),2):
        try:
            programming_language=msg_arr[i].split("\n")[0].strip()
            msg_arr[i]=add_syntax_highlighting(msg_arr[i], programming_language)
            add_programming_language(programming_language)
        except: 
            all_langs=get_programming_languages()
            langs=contains(msg_arr[i-1].lower(), all_langs)+\
                contains(msg_arr[i-1], all_langs)
            if len(langs)!=0:
                random.seed(time.time())
                lang=random.choice(langs)
                msg_arr[i]=add_syntax_highlighting(msg_arr[i], lang)
    plain_color_str=colors.get_color(plain_color)
    for i in range(0,len(msg_arr),2):
        msg_arr[i]=plain_color_str+msg_arr[i]
    return (plain_color_str+"```").join(msg_arr)



def get_question():
    custom_style = Style.from_dict({
        'prompt': 'ansired',
        '': 'ansiyellow',
    })
    history = FileHistory(tmp_dir+".history.txt") # This will create a history file to store your past inputs
    input_text = ""
    while (input_text.strip()==""):
        try:
            input_text = prompt(translate("Enter your question (or q to quit, r to refresh): "), style=custom_style, \
                history=history, key_bindings=get_key_bindings(), auto_suggest=AutoSuggestFromHistory())
        except KeyboardInterrupt:
            print(translate("Exiting..."))
            sys.exit(0)
    return input_text

def test_api_key() -> bool:
    try:
        openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": "Hello"}])
        return True
    except Exception as e:
        if "No API key provided" in str(e) or "Incorrect API key provided" in str(e) or \
            "You didn't provide an API key" in str(e):
            return False
        else: return True

def record_auth(org:str, api_key:str):
    with open(tmp_dir+"auth", "w") as f:
        f.write(f"{org}\n{api_key}")
    print(translate("Authentication successful. Your credentials are saved to")+f" {os.path.normpath(tmp_dir+'auth')}.")
    print(translate("You can now run the program without entering your credentials again."))

def setup(reset=False):
    if os.path.exists(tmp_dir+"auth") and not reset:
        try:
            with open(tmp_dir+"auth", "r") as f:
                org,key=f.read().split("\n")
                openai.organization=org
                openai.api_key=key
                return
        except: pass
            
    history = FileHistory(tmp_dir+".auth") # authentification history
    openai.organization=prompt(translate("Enter your organization:"),history=history, key_bindings=get_key_bindings())
    openai.api_key=prompt(translate("Enter your OpenAI API key:"),history=history, key_bindings=get_key_bindings())
    if test_api_key():
        record_auth(openai.organization, openai.api_key) 
        return
    else:
        print(translate("Authentication failed. Please try again."))
        setup(reset=True)

def setup_theme():
    colorama.init()

def ask_question(ques:list):
    ans=""
    try:
        response=openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=ques,stream=True)
        for r in response:
            delta=r.choices[0].delta
            if "role" in delta:
                print(colors.fg.blue+str(delta["role"])+": "+colors.reset+"", end="", flush=True)
            elif "content" in delta:
                ans+=delta["content"]
                print(delta["content"], end="", flush=True)
            else: continue
        print()
    except Exception as e:
        if len(ans)!=0:
            return ans
        else: raise e
    return ans

def cut_msg_arr(msg_arr:list, max_len:int):
    sys_msg=msg_arr[0]
    msg_arr_left=[sys_msg]
    total_len=len(str(sys_msg).split())
    for i in range(-1, -len(msg_arr), -1):
        curr_msg=str(msg_arr[i])
        processed_msg = re.sub(r'[^\w\s]', ' ', curr_msg)
        non_alnum_count = len(re.findall(r"[^\w\s]", curr_msg))
        total_len+=len(processed_msg.split())+non_alnum_count//16
        if total_len>max_len: break
        msg_arr_left.insert(1, msg_arr[i])
    print(f"Cutting {len(msg_arr)-len(msg_arr_left)} from {len(msg_arr)} messages..."\
        .ljust(len(f"Waiting for response - (10.1s)")))
    return msg_arr_left

def refresh(msg_arr_whole:list):
    os.system('cls' if os.name=='nt' else 'clear')
    print_msg_arr(msg_arr_whole)

def start_chat(customize_system: bool, msg_arr=[], msg_arr_whole=[]):
    if len(msg_arr_whole)==0: # start a new chat
        system_msg="You are a helpful assistant."
        print(translate("Default system prompt:")+f" {system_msg}")
        if customize_system: 
            system_msg=input(translate("Enter a new system prompt: "))
            print(translate("System prompt set to:")+f" {system_msg}")
        msg_arr.append({"role": "system", "content": system_msg})
        msg_arr_whole.append({"role": "system", "content": system_msg})
        
    input_text=""
    while(input_text.lower()!="q"):
        if msg_arr[-1]['role']!="user":
            input_text=get_question()
            if input_text=="q": break
            elif input_text=="r": refresh(msg_arr_whole); continue
                
            msg_arr.append({"role": "user", "content": input_text})
            msg_arr_whole.append({"role": "user", "content": input_text})
        
        try: response=ask_question(msg_arr)
        except Exception as e:
            if ("reduce the length of the messages" in str(e)):
                print(translate('Max length of messages reached. Remove the earliest dialog.'))
                msg_arr_left=cut_msg_arr(msg_arr, 4096)
                if len(msg_arr)>=2 and len(msg_arr_left)==len(msg_arr):
                    print(f"Cutting 2 from {len(msg_arr)} messages..."\
                        .ljust(len(f"Waiting for response - (10.1s)")))
                    msg_arr.pop(1)
                    if len(msg_arr)>=2: msg_arr.pop(1)
                else: msg_arr=msg_arr_left
            elif ("Rate limit reached for" in str(e)): time.sleep(1)
            elif ("Incorrect API key provided" in str(e)):
                print(translate("Authentication failed. Please provide a valid API key."))
                setup(reset=True)
            else:
                print(e)
                break
            continue
        except KeyboardInterrupt as e:
            print("\n"+translate("Keyboard interrupt!"))
            return msg_arr_whole
        
        msg_arr.append({"role": "assistant", "content": response})
        msg_arr_whole.append({"role": "assistant", "content": response})
        
        # refresh screen if new code exists
        if "```" in response:
            refresh(msg_arr_whole)
    return msg_arr_whole

def resume_chat(msg_arr_whole: list):
    print_msg_arr(msg_arr_whole)
    msg_arr=msg_arr_whole.copy()
    msg_arr_whole=start_chat(customize_system=False, msg_arr=msg_arr, msg_arr_whole=msg_arr_whole)
    return msg_arr_whole

def ask_path(op: str="save"):
    # create a Tkinter root window
    root = tk.Tk()
    root.withdraw()
    # open a file dialog box and allow the user to select a file location
    if op=="save":
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    elif op=="open":
        file_path = filedialog.askopenfilename(defaultextension=".txt")
    else:
        raise ValueError("op must be either 'save' or 'open'")
    return file_path

def save_msg_arr(msg_arr):
    file_path = ask_path(op="save")
    # save the array to the selected file location
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in msg_arr:
            f.write(str(item) + '\n')
    print(translate("Chat is saved to")+f" {file_path}")

def read_msg_arr():
    file_path = ask_path(op="open")
    # read the array from the selected file location
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        my_list = []
        for line in lines:
            my_list.append(eval(line.strip())) # Use eval function to convert string to object
        return my_list