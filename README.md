# ChatGPT Terminal
Interactive ChatGPT terminal implemented in Python.

## Setup:
1. Run `git clone https://github.com/williamlus/chatgpt-terminal.git`, and then `cd chatgpt-terminal`.
2. Run `pip install -r requirements.txt` or `pip3 install -r requirements.txt` to install required packages.
3. Create your OpenAI API account at https://platform.openai.com.
4. Use your account to generate your `OPENAI_API_KEY` from https://platform.openai.com/account/api-keys.
5. Provide your OpenAI Organization and API Key to login.

## Usage:
### For Windows users:
Run `chat.bat` to start a new chat, or `chatr.bat` to resume a chat.
### For Linux/MacOS users:
1. First give permission to .sh files by running `chmod +x chat.sh` and `chmod +x chatr.sh`.
2. Run `./chat.sh` to start a new chat, or `./chatr.sh` to resume a chat.
3. If GUI (tkinter) is not available in your OS, run `./chat.sh --nogui` and `./chatr.sh --nogui` instead.

## Installation:
To compile the program into an executable file, run `compile.bat`. You will find `chat` or `chat.exe` in `./dist/` after compilation.

## Useful Shortcuts:
1. Press  `ctrl-E` or `→` to insert a suggestion, `alt-F` to insert the first suggested word.
2. Press `ctrl-C` to copy the selected text, `ctrl-D` to terminate the program.
3. Press `ctrl-V` to paste the text from the clipboard.
4. Press `insert` to switch to edit mode, in which you can press `enter` to add a new line.
5. Press `esc` to quit the edit mode, then you can press `enter` to submit your question to ChatGPT. 
