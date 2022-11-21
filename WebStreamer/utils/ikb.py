from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def ikb(rows=None) -> InlineKeyboardMarkup:
    """
    :param rows: list of list of buttons
    :return: InlineKeyboardMarkup
    """
    if rows is None:
        rows = []
    lines = []
    for row in rows:
        line = []
        for button in row:
            button = btn(*button)  # InlineKeyboardButton
            line.append(button)
        lines.append(line)
    return InlineKeyboardMarkup(inline_keyboard=lines)
    # return {'inline_keyboard': lines}


def btn(text, value, t="callback_data"):
    """
    :param text: button text
    :param value: button value
    :param t: button type
    :return: InlineKeyboardButton
    """
    return InlineKeyboardButton(text, **{t: value})
    # return {'text': text, type: value}
