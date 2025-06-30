import streamlit as st
import re
from streamlit_code_block import code_block

def render_message_with_copy_buttons(message_content: str):
    """
    Renders a message, replacing markdown code blocks with a component
    that has a copy-to-clipboard button.
    
    Args:
        message_content: The string content of the message to render.
    """
    # Pattern to find code blocks: ```(optional language)\n(code)\n```
    code_block_pattern = r"```(\w*)\n([\s\S]*?)\n```"
    
    last_end = 0
    # Use finditer to iterate through all matches
    for match in re.finditer(code_block_pattern, message_content):
        # Render the markdown text that comes before the code block
        st.markdown(message_content[last_end:match.start()])
        
        # Extract language and the code content
        language = match.group(1)
        code_content = match.group(2)
        
        # Render the code block using the streamlit-code-block component
        code_block(code_content, language=language if language else "plaintext", show_lines=True)
        
        # Update the position for the next part of the text
        last_end = match.end()
        
    # Render any remaining text after the last code block
    if last_end < len(message_content):
        st.markdown(message_content[last_end:])