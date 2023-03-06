# ChatGPT Terminal
Interactive ChatGPT terminal implemented in Python.

## Setup:
1. Run `git clone https://github.com/williamlus/chatgpt-terminal.git`, and then `cd chatgpt-terminal`.
2. Run `pip install -r requirements.txt` or `pip3 install -r requirements.txt` to install required packages.
3. Create your OpenAI API account at https://platform.openai.com.
3. Use your account to generate your `OPENAI_API_KEY` from https://platform.openai.com/account/api-keys, and add it to your system environment. I will run `os.getenv("OPENAI_API_KEY")` to obtain your API key for authentication.

## Usage:
### For Windows users:
Run `chat.bat` to start a new chat, or `chatr.bat` to resume a chat.
### For Linux/MacOS users:
Run `./chat.sh` to start a new chat, or `./chatr.sh` to resume a chat.

## Useful Shortcuts:
1. Press `ctrl-C` to copy the selected text, or terminate the program if no selection exists.
2. Press `ctrl-V` to paste the text from the clipboard.
3. Press `ctrl-I` to switch to edit mode, in which you can press `enter` to add a new line.
4. Press `esc` to quit the edit mode, then you can press `enter` to submit your question to ChatGPT. 
