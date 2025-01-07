
def tokenize(text):
    """
    Splits a string into a list of tokens, preserving whitespace as separate tokens.

    :param text: The string to tokenize.
    :return: A list of tokens.

    Examples:
        >>> tokenize("Hello, world!")
        ['Hello,', ' ', 'world!']
        >>> tokenize("Hello,  World!")
        ['Hello,', ' ', ' ', 'World!']
    """
    tokens = []
    token = ""
    for char in text:
        if char.isspace():
            if token:
                tokens.append(token)
                token = ""
            tokens.append(char)
        else:
            token += char
    if token:
        tokens.append(token)
    return tokens


def wrap_text(text, width):
    """
    Wraps text to a specified width, breaking lines on whitespace.

    :param text: The text to wrap.
    :param width: The maximum width of a line.
    :return: A list of wrapped lines.

    Examples:
        >>> wrap_text("This is a sample text that needs to be wrapped.", 10)
        ['This is a ', 'sample ', 'text that ', 'needs to ', 'be ', 'wrapped.']
    """
    tokens = tokenize(text)
    wrapped = []
    current_line = ""
    for token in tokens:
        if token == "\n":
            wrapped.append(current_line)
            current_line = ""
        elif len(current_line) + len(token) <= width:
            current_line += token
        else:
            wrapped.append(current_line)
            current_line = token
    wrapped.append(current_line)
    return wrapped
