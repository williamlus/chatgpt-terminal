import sys
import pyperclip
import openai, os, time, random, colorama
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
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter
import threading

is_insert_mode=False
response_completed=False
start_time=None

def log_msg(role:str, msg:str, role_color:str="blue", msg_color:str="reset"):
    # mapping from string to colorama.Fore attributes
    color_map = {
        "blue": colorama.Fore.BLUE,
        "red": colorama.Fore.RED,
        "green": colorama.Fore.GREEN,
        "yellow": colorama.Fore.YELLOW,
        "reset": colorama.Fore.RESET,
    }
    if role=="assistant": msg=color_code(msg)
    print(color_map[role_color]+role+": ", end='', flush=True)
    print((color_map[msg_color]+msg).strip(), flush=True)

def print_msg_arr(msg_arr: list):
    for msg in msg_arr:
        if msg['role']=="user": log_msg(msg['role'], msg['content'], role_color="yellow")
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

def color_code(msg:str):
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
            
    return "```".join(msg_arr)

def get_key_bindings():
    bindings = KeyBindings()
    
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
    
    @Condition
    def not_edit_mode(): return not is_insert_mode
    
    @bindings.add('c-i', filter=not_edit_mode)
    def _(event: KeyPressEvent): globals()['is_insert_mode'] = True
    
    @Condition
    def is_edit_mode(): return is_insert_mode
    
    @ bindings.add('escape', filter=is_edit_mode)
    def _(event: KeyPressEvent): globals()['is_insert_mode'] = False
    
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
    while (input_text==""):
        input_text = prompt("Enter your message (or q to quit): ", style=custom_style, history=history, key_bindings=get_key_bindings())
    return input_text

def setup():
    openai.organization = "org-ggL1uiODdaNr1nCveaaGixyP"
    try:
        api_key=os.getenv("OPENAI_API_KEY")
        assert(api_key!=None)
        openai.api_key = api_key
    except:
        print("Please set the environment variable OPENAI_API_KEY to your OpenAI API key to automatically authenticate requests.")
        while(True):
            api_key=input("Enter your OpenAI API key (or q to quit):")
            if api_key.lower()=="q": exit()
            else: 
                openai.api_key = api_key
                try:
                    openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": "Hello"}])
                    os.system('setx OPENAI_API_KEY "{}"'.format(api_key))
                    break
                except:
                    print("Invalid API key.")

def setup_theme():
    colorama.init()

def ask_question(ques:list):
    global response_completed, start_time
    response_completed, start_time=False, time.time()
    
    def rotating_bar():
        global response_completed, start_time
        bar_chars="/-\\|"
        while not response_completed:
            time_passed=round(time.time()-start_time, 1)
            msg=f"Waiting for response {bar_chars[int(time_passed/0.2)%4]} ({time_passed}s)"
            sys.stdout.write(colorama.Fore.LIGHTBLACK_EX+msg)
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b'*len(msg))
            sys.stdout.flush()
        time_passed=round(time.time()-start_time, 1)
        print(colorama.Fore.LIGHTBLACK_EX+f"Response finished ({time_passed}s)".ljust(len(msg)), flush=True)
        
    bar_thread=threading.Thread(target=rotating_bar)
    bar_thread.start()
    completion=openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=ques)
    response_completed=True
    bar_thread.join()
    return completion

def start_chat(customize_system: bool):
    msg_arr=[]
    system_msg="You are a helpful assistant."
    print(f"Default system prompt: {system_msg}")
    if customize_system: 
        system_msg=input("Enter a new system prompt: ")
        print(f"System prompt set to: {system_msg}")
    msg_arr.append({"role": "system", "content": system_msg})
    input_text=""
    while(input_text.lower()!="q"):
        input_text=get_question()
        if input_text.lower()=="q": break
        msg_arr.append({"role": "user", "content": input_text})
        try: completion=ask_question(msg_arr)
        except Exception as e:
            print(e, flush=True) 
            msg_arr.pop()
            continue
        resp=completion.choices[0].message.content
        msg_arr.append({"role": "assistant", "content": resp})
        log_msg("assistant", resp)
    return msg_arr

def resume_chat(msg_arr: list):
    print_msg_arr(msg_arr)
    input_text=""
    while(input_text.lower()!="q"):
        input_text=get_question()
        if input_text.lower()=="q": break
        msg_arr.append({"role": "user", "content": input_text})
        while(True):
            try:
                completion=ask_question(msg_arr)
                break
            except:
                time.sleep(1)
                continue  
        resp=completion.choices[0].message.content
        msg_arr.append({"role": "assistant", "content": resp})
        log_msg("assistant", resp)
    return msg_arr

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