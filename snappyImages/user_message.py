"""user message - allow selection of new message for show_scroller.
"""
from menu_select import *
from app_switch import *
from drivers.fonts_8x8 import *
from drivers.DEF8x8 import *

# Alphanumerics, plus "backspace, erase, exit" icons
DEF8x8_BACK = '\x1b'
DEF8x8_ERASE = '\x14'
DEF8x8_EXIT = '\x13'
user_menu_icons = '!"#$%&\'()*+,-./0123456789:;<=>?@' + DEF8x8_EXIT + DEF8x8_ERASE + DEF8x8_BACK +  \
                  ' ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'


USER_MSG_MAXLEN = 80
user_msg_text = ""

def user_message_init():
    global user_msg_text
    user_msg_text = loadNvParam(NV_USER_MSG)
    init_index = ord('A') - ord(' ') + 3  # Compensate for 3 extra chars
    menu_define(user_menu_icons, DEF8x8, DEF8x8_widths, user_message_select_hook, init_index)
    app_switch(menu_context)
    
def user_message_select_hook(i_select):
    global user_msg_text, show_scroller_text
    select_char = user_menu_icons[i_select]

    # If still holding both buttons down, we save and exit
    down_count = 5000
    while not (readPin(BUTTON_LEFT) or readPin(BUTTON_RIGHT)):
        down_count -= 1
        if down_count == 0:
            user_message_save(user_msg_text)
            return
        
    # Take action based on selected characters
    if select_char == DEF8x8_EXIT:
        app_exit()
    elif select_char == DEF8x8_BACK:
        user_msg_text = user_msg_text[:-1]
    elif select_char == DEF8x8_ERASE:
        user_msg_text = ""
    elif len(user_msg_text) < USER_MSG_MAXLEN:
        user_msg_text += select_char
    else:
        app_exit()

def user_message_save(msg):
    saveNvParam(NV_USER_MSG, msg)
    app_exit()

    
# Hook context, for multi-app switching via app_switch.py
user_message_context = (user_message_init, None, None, None, None, None)
