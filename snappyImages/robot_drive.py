"""Drive the robot"""

from drivers.snap_badge import *
from snap_shields.ada_moto_v2 import *

@setHook(HOOK_STARTUP)
def start():
    badge_start()
    ada_moto_init()
    


