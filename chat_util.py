import openai, os, time, random, re, pyperclip, sys, colorama
import tkinter as tk
from tkinter import filedialog
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.selection import SelectionType
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.filters import Condition
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter
import threading
from colors import colors

is_insert_mode=False
response_completed=""
start_time=None

def log_msg(role:str, msg:str, role_color:str="blue", msg_color:str="reset"):
    msg=color_code(msg, plain_color=msg_color)
    print(colors.get_color(role_color)+role+": ", end='', flush=True)
    print((colors.get_color(msg_color)+msg).strip(), flush=True)

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
        with open("programming_languages.txt", "r") as f:
            langs=f.read().split("\n")
    except: 
        langs=['python','java','cpp', "csharp", "c++", "C++", "c#", "C#", "C", "c", "sql", "SQL"]
        with open("programming_languages.txt", "w") as f:
            f.write('\n'.join(langs))
    return langs

def add_programming_language(lang:str):
    langs=get_programming_languages()
    if lang not in langs: 
        with open("programming_languages.txt", "w") as f:
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

def get_key_bindings():
    bindings = KeyBindings()
    
    @bindings.add(Keys.Tab)
    def _(event: KeyPressEvent):
        b = event.app.current_buffer
        b.insert_text(" "*4)
    
    @bindings.add("c-v")
    def _(event: KeyPressEvent):
        b = event.app.current_buffer
        s = pyperclip.paste()
        b.insert_text(s)
        
    @bindings.add("c-c")
    def _(event: KeyPressEvent):
        buffer = event.app.current_buffer
        selection = buffer.document.selection
        if selection and selection.type == SelectionType.CHARACTERS:
            from_, to = sorted([buffer.cursor_position, buffer.selection_state.original_cursor_position])
            selected_text = buffer.text[from_:to]
            pyperclip.copy(selected_text)
        else: sys.exit(0)
        
    @bindings.add("right")
    def _(event: KeyPressEvent):
        buffer = event.app.current_buffer
        selection = buffer.document.selection
        if selection and selection.type == SelectionType.CHARACTERS:
            buffer.document.selection.enter_shift_mode
            tgt = max(buffer.cursor_position, buffer.selection_state.original_cursor_position)
            buffer.exit_selection()
            buffer.cursor_position = tgt
        else:
            try: buffer.cursor_position += 1
            except Exception as e: pass
            
    @bindings.add("left")
    def _(event: KeyPressEvent):
        buffer = event.app.current_buffer
        selection = buffer.document.selection
        if selection and selection.type == SelectionType.CHARACTERS:
            tgt = min(buffer.cursor_position, buffer.selection_state.original_cursor_position)
            buffer.exit_selection()
            buffer.cursor_position = tgt
        else: 
            try: buffer.cursor_position -= 1
            except Exception as e: pass
    
    globals()['is_insert_mode'] = False
    
    @bindings.add(Keys.Insert)
    def _(event: KeyPressEvent): globals()['is_insert_mode'] = True
    
    @ bindings.add('escape')
    def _(event: KeyPressEvent): globals()['is_insert_mode'] = False
    
    @Condition
    def is_edit_mode() -> bool:
        return globals()['is_insert_mode']
    
    @ bindings.add(Keys.Enter, filter=is_edit_mode)
    def _(event: KeyPressEvent):
        event.current_buffer.newline()
    
    return bindings

def get_question():
    custom_style = Style.from_dict({
        'prompt': 'ansired',
        '': 'ansiyellow',
    })
    history = FileHistory(".history.txt") # This will create a history file to store your past inputs
    input_text = ""
    while (input_text.strip()==""):
        try:
            input_text = prompt("Enter your message (or q to quit): ", style=custom_style, \
                history=history, key_bindings=get_key_bindings(), auto_suggest=AutoSuggestFromHistory())
        except KeyboardInterrupt:
            print("Exiting...")
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
    with open("auth", "w") as f:
        f.write(f"{org}\n{api_key}")
    print("Authentication successful. Your credentials are saved to './auth'.")
    print("You can now run the program without entering your credentials again.")

def setup(reset=False):
    if os.path.exists("auth") and not reset:
        try:
            with open("auth", "r") as f:
                org,key=f.read().split("\n")
                openai.organization=org
                openai.api_key=key
                return
        except: pass
            
    history = FileHistory(".auth") # authentification history
    openai.organization=prompt("Enter your organization:",history=history, key_bindings=get_key_bindings())
    openai.api_key=prompt("Enter your OpenAI API key:",history=history, key_bindings=get_key_bindings())
    if test_api_key():
        record_auth(openai.organization, openai.api_key) 
        return
    else:
        print("Authentication failed. Please try again.")
        setup(reset=True)

def setup_theme():
    colorama.init()

def start_bar_clock() -> threading.Thread:
    def rotating_bar():
        global response_completed, start_time
        bar_chars="/-\\|"
        while response_completed=='started':
            time_passed=round(time.time()-start_time, 1)
            msg=f"Waiting for response {bar_chars[int(time_passed/0.2)%4]} ({time_passed}s)"
            print(colors.get_color('darkgrey')+msg, flush=True, end='')
            time.sleep(0.1)
            print('\b'*len(msg), flush=True, end='')
        time_passed=round(time.time()-start_time, 1)
        if response_completed=='finished':
            print(colors.get_color('darkgrey')+f"Response finished ({time_passed}s)".ljust(len(msg)), flush=True)
    bar_thread=threading.Thread(target=rotating_bar)
    bar_thread.start()
    return bar_thread

def ask_question(ques:list):
    global response_completed, start_time
    response_completed, start_time="started", time.time()
    bar_thread=start_bar_clock()
    try:
        completion=openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=ques)
        response_completed="finished"
    except Exception as e:
        response_completed="failed"
        bar_thread.join()
        raise e
    except KeyboardInterrupt as e:
        response_completed="failed"
        bar_thread.join()
        raise e
    bar_thread.join()
    return completion


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

def start_chat(customize_system: bool, msg_arr=[], msg_arr_whole=[]):
    if len(msg_arr_whole)==0: # start a new chat
        system_msg="You are a helpful assistant."
        print(f"Default system prompt: {system_msg}")
        if customize_system: 
            system_msg=input("Enter a new system prompt: ")
            print(f"System prompt set to: {system_msg}")
        msg_arr.append({"role": "system", "content": system_msg})
        msg_arr_whole.append({"role": "system", "content": system_msg})
        
    input_text=""
    while(input_text.lower()!="q"):
        if msg_arr[-1]['role']!="user":
            input_text=get_question()
            if input_text.lower()=="q": break
            msg_arr.append({"role": "user", "content": input_text})
            msg_arr_whole.append({"role": "user", "content": input_text})
        
        try: completion=ask_question(msg_arr)
        except Exception as e:
            if ("reduce the length of the messages" in str(e)):
                print(f'Max length of messages reached. Remove the earliest dialog.')
                msg_arr_left=cut_msg_arr(msg_arr, 4096)
                if len(msg_arr)>=2 and len(msg_arr_left)==len(msg_arr):
                    print(f"Cutting 2 from {len(msg_arr)} messages..."\
                        .ljust(len(f"Waiting for response - (10.1s)")))
                    msg_arr.pop(1)
                    if len(msg_arr)>=2: msg_arr.pop(1)
                else: msg_arr=msg_arr_left
            elif ("Rate limit reached for" in str(e)): time.sleep(1)
            elif ("Incorrect API key provided" in str(e)):
                print("Authentication failed. Please provide a valid API key.")
                setup(reset=True)
            else:
                print(e)
                break
            continue
        except KeyboardInterrupt as e:
            print("\nKeyboard interrupt!")
            return msg_arr_whole
        
        resp=completion.choices[0].message.content
        msg_arr.append({"role": "assistant", "content": resp})
        msg_arr_whole.append({"role": "assistant", "content": resp})
        log_msg("assistant", resp)
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
    print(f"Chat is saved to {file_path}")

def read_msg_arr():
    file_path = ask_path(op="open")
    # read the array from the selected file location
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        my_list = []
        for line in lines:
            my_list.append(eval(line.strip())) # Use eval function to convert string to object
        return my_list