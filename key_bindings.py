import pyperclip, sys
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.selection import SelectionType
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.filters import Condition

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
        b.cursor_position += len(s)
        
    @bindings.add("c-c")
    def _(event: KeyPressEvent):
        buffer = event.app.current_buffer
        selection = buffer.document.selection
        if selection and selection.type == SelectionType.CHARACTERS:
            from_, to = sorted([buffer.cursor_position, buffer.selection_state.original_cursor_position])
            selected_text = buffer.text[from_:to]
            pyperclip.copy(selected_text)
        else: pass
    
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