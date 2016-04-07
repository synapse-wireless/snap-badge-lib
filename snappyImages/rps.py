"""RPS - Rock, Paper, Scissors game
   A timeless classic way to make life's many unimportant decisions. Let random fate decide!
   SPLUNGE!

Usage:
  Press Left or Right button to reset game.
  Use classic "down" motion with badge to sequence through RPS states: 1-2-3-SHOW.
  On 'SHOW' your random choice will be displayed, and sent to other players!
  Multiplayer results are as follows:
    If it's a tie, all winners will flash.
    If you win, you'll see a victory animation.
    If you lose, you just see your choice. It is possible for all players to lose (all re-do!)

  Restart by pressing either button.

"""

from drivers.snap_badge import *
from drivers.Doodads import *
from animation import *
from drivers.true_random import *
from gestures import *
from drivers.fonts_8x8 import *
from drivers.DEF8x8 import *

# By default, we are traditional RPS. Use S7 to unlock Spock Mode.
spock_mode = False 

rps_state = 0

# Animation icons are the following indices of Doodads fontset
rps_startup_anim_icons = '\x61\x62\x63\x64\x65\x66\x67\x68'  # Radar
rps_await_result_icons = '\x73\x74\x75\x76\x77\x78'          # Sine wave
rps_result_icons = '\x79\x7a\x7b\x90\x91'  # Scissors, Rock, Paper, Lizard, Spock

rps_choice = 0
RPS_SCISSORS = 0
RPS_ROCK = 1
RPS_PAPER = 2
RPS_LIZARD = 3
RPS_SPOCK = 4

# Rules are tuples where [0] beats [1]
RPS_RULES = ((RPS_ROCK, RPS_SCISSORS),
             (RPS_PAPER, RPS_ROCK),
             (RPS_SCISSORS, RPS_PAPER),
             (RPS_ROCK, RPS_LIZARD),
             (RPS_LIZARD, RPS_SPOCK),
             (RPS_SPOCK, RPS_SCISSORS),
             (RPS_SCISSORS, RPS_LIZARD),
             (RPS_LIZARD, RPS_PAPER),
             (RPS_PAPER, RPS_SPOCK),
             (RPS_SPOCK, RPS_ROCK)
            )

app_exit = None

RPS_NEARBY_SIGNAL = 55   # Threshold for nearby badges we want to associate with (-dBm)

rps_rx_enable = False

# Score is "WIN, LOSE, or TIE"
rps_score = 0
RPS_LOSE = 1
RPS_WIN  = 2
RPS_TIE  = 3

def rps_start():
    """Startup hook when run standalone"""
    global current_context
    current_context = rps_context
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    rps_init()
    
def rps_init():
    """Initialize application - get our animation icons loaded up"""
    global rps_state, spock_mode, rps_rx_enable
    rps_state = 0
    rps_rx_enable = False
    
    # No blinking
    as1115_wr(FEATURE, 0)
    
    # Check DIP switch S7 - if set, add Lizard/Spock to the mix :)
    sw = ~as1115_rd(KEYB)
    spock_mode = (sw & DIP_S7)
    
    # Init gesture lib
    gesture_update_accel()
    gesture_set_callback(rps_gestures)
    
    # Init animation
    load_font(Doodads, Doodads_widths)
    anim_init(rps_startup_anim_icons, 8, rps_startup_anim_done)
    anim_begin(200)
    
def rps_startup_anim_done():
    """Should only get here if left in startup mode for a couple minutes"""
    if app_exit:
        app_exit()
    else:
        anim_begin(200)

def rps_gestures(gest_type):
    """Callback from gesture detection lib"""
    if gest_type == GESTURE_DOWN:
        rps_fist()

def rps_fist():
    """Fist down event"""
    global rps_state, rps_rx_enable, rps_choice, rps_score
    
    # Number of fist-down events depends on mode: 1-2-3-show, or 1-2-3-4-5-show
    if spock_mode:
        choose_state = 5
        show_state = 6
    else:
        choose_state = 3
        show_state = 4
    
    if rps_state == 0:
        anim_stop()
        load_font(DEF8x8, DEF8x8_widths)
    
    rps_state += 1
    if rps_state < choose_state:
        display_drv(get_indexed_sym(ord('0') + rps_state))
        
    elif rps_state == choose_state:
        display_drv(get_indexed_sym(ord('0') + rps_state))
        
        # Choose now!
        divisor = 820 if spock_mode else 1366
        rps_choice = true_random() / divisor
        rps_score = RPS_WIN  # Be optimistic :)
        
        # At this point, we will accept other players choices
        rps_rx_enable = True
        
    elif rps_state == show_state:
        # Done! Play final animation while awaiting stragglers...
        load_font(Doodads, Doodads_widths)
        anim_init(rps_await_result_icons, 5, rps_result_anim_done)
        anim_begin(4)   # duration = 50ms * 6 icons * 4 loops = 1.2 sec
        mcastRpc(1, 1, 'rps', rps_choice)
    
    else:
        pass

def rps_result_anim_done():
    """Waiting is over - show choice now."""
    global rps_rx_enable
    display_drv(get_indexed_sym(ord(rps_result_icons[rps_choice])))
    rps_rx_enable = False
    
    if rps_score == RPS_WIN:
        # We won! Play a cool animation...
        rps_win_icons = rps_result_icons[rps_choice] + '\x8d\x8e\x8f'
        print "WIN, ", rps_win_icons
        anim_init(rps_win_icons, 30, rps_win_anim_done)
        anim_begin(25)   # duration = 300ms * 4 icons * 25 loops = 30 sec
    elif rps_score == RPS_TIE:
        # Tied - blink annoyingly
        as1115_wr(FEATURE, AS_BLINK_EN)
    else:
        # Lost - do nothing
        pass
        
def rps_win_anim_done():
    if app_exit:
        app_exit()
    else:
        anim_begin(25)

def rps(opponent_choice):
    """Over the air call - an opponent's choice"""
    global rps_score
    # Only respond if badge is in "rps" mode, and signal is nearby
    if current_context == rps_context and getLq() < RPS_NEARBY_SIGNAL:
        # Update our score
        if rps_rx_enable and rps_score != RPS_LOSE:
            result = rps_apply_rules(rps_choice, opponent_choice)
            if result != RPS_WIN:
                rps_score = result

def rps_apply_rules(me, you):
    if me == you:
        return RPS_TIE
    
    rule_len = 10 if spock_mode else 3
    
    for i in xrange(rule_len):
        rule = RPS_RULES[i]
        if me == rule[0] and you == rule[1]:
            return RPS_WIN
        elif you == rule[0] and me == rule[1]:
            return RPS_LOSE
    
    return RPS_TIE

def rps_tick10ms():
    """Called by system every 10ms"""
    global rps_inertial_debounce

    gesture_poll_10ms()

    anim_tick10ms()

    # Allow restart with button press
    if not (readPin(BUTTON_RIGHT) and readPin(BUTTON_LEFT)):
        rps_init()



# Hook context, for multi-app switching via app_switch.py
rps_context = (rps_init, None, rps_tick10ms, None, None, None)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, rps_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, rps_tick10ms)



    