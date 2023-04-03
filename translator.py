def translate_util(msg:str, lang:str="cn"):
    if lang not in ["cn", "en"]: 
        raise Exception(f"{lang} not supported.")
    if lang=="en": return msg
    msg_map={
        "Enter your organization:": "输入您的组织:",
        "Enter your OpenAI API key:": "输入您的OpenAI API密钥:",
        "Enter your question (or q to quit): ": "输入您的问题(或输入q退出):",
        "Authentication successful. Your credentials are saved to": "身份验证成功，您的凭据已保存到",
        "You can now run the program without entering your credentials again.": "您现在可以运行程序而无需再次输入您的凭据。",
        "Authentication failed. Please try again.": "身份验证失败，请重试。",
        # "Waiting for response": "等待响应",
        # "Response finished": "响应完成",
        "Default system prompt:": "默认系统提示:",
        "Enter a new system prompt: ": "输入新的系统提示:",
        "System prompt set to:": "系统提示设置为:",
        'Max length of messages reached. Remove the earliest dialog.': '达到消息的最大长度，忽略最早的对话。',
        "Authentication failed. Please provide a valid API key.": "身份验证失败，请提供有效的API密钥。",
        "Chat is saved to": "聊天记录已保存到",
        "Exiting...": "正在退出...",
        "Keyboard interrupt!": "进程中断!",
        "Unable to resume chat. Starting a new chat session.": "无法恢复聊天，开始新的聊天会话。",
        "Save the chat log to a file if you want to resume the chat later.": "如果要稍后恢复聊天，请将聊天记录保存到文件。",
        "Unable to save chat log.": "无法保存聊天记录。",
        "Enter your question (h for command list): ": "输入您的问题(或输入h查看命令列表):",
        "h\t:list of commands\n"+\
            "q\t:quit with saving\n"+\
            "q!\t:quit without saving (Ctrl-D)\n"+\
            "r\t:refresh screen\n"+\
            "-clc\t:clear the context\n"+\
            "-hf\t:half the context\n"+\
            "-key\t:show the login key\n"+\
            "-l\t:reset login key\n"+\
            "-ls\t:list the context messages left\n"+\
            "-lsp\t:list the files in the working directory\n"+\
            "-pop <n>:remove the first <n> messages in context\n"+\
            "-pwd\t:change the working directory\n"+\
            "-rl\t:reload all chat messages to the context\n"+\
            "-s <fp>\t:save the chat to a file path <fp> relative to the current working dir\n"\
            "-sys\t:edit the system message\n"+\
            "":
            "h\t:命令列表\n"+\
            "q\t:退出并保存\n"+\
            "q!\t:退出不保存 (Ctrl D)\n"+\
            "r\t:刷新屏幕\n"+\
            "-clc\t:清除上下文\n"+\
            "-hf\t:上下文减半\n"+\
            "-key\t:显示登录密钥\n"+\
            "-l\t:重置登录密钥\n"+\
            "-ls\t:列出上下文中剩余的消息\n"+\
            "-lsp\t:列出工作目录中的文件\n"+\
            "-pop <n>:删除上下文中的前 <n> 条消息\n"+\
            "-pwd\t:更改工作目录\n"+\
            "-rl\t:将所有聊天消息重新加载到上下文中\n"+\
            "-s <fp>\t:将聊天保存到相对于当前工作目录的文件路径 <fp>\n"\
            "-sys\t:编辑系统消息\n"+\
            "",
        
    }
    return msg_map.get(msg, msg)