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
        "Default system prompt:": "默认系统提示符:",
        "Enter a new system prompt: ": "输入新的系统提示符:",
        "System prompt set to:": "系统提示符设置为:",
        'Max length of messages reached. Remove the earliest dialog.': '达到消息的最大长度，忽略最早的对话。',
        "Authentication failed. Please provide a valid API key.": "身份验证失败，请提供有效的API密钥。",
        "Chat is saved to": "聊天记录已保存到",
        "Exiting...": "正在退出...",
        "Keyboard interrupt!": "进程中断!",
        "Unable to resume chat. Starting a new chat session.": "无法恢复聊天，开始新的聊天会话。",
        "Save the chat log to a file if you want to resume the chat later.": "如果要稍后恢复聊天，请将聊天记录保存到文件。",
        "Unable to save chat log.": "无法保存聊天记录。",
        
    }
    return msg_map.get(msg, msg)