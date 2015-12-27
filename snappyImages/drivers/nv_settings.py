# Copyright (C) 2014 Synapse Wireless, Inc.
"""NV settings initialization"""
from synapse.nvparams import *

def init_nv_settings(mcast_proc, mcast_fwd, cs, ca, cd):
    """Set mcast processed groups, forwarding groups, CSMA settings, etc."""
    global _needs_reboot
    _needs_reboot = False

    # RPC CRC
    check_nv(NV_FEATURE_BITS_ID, 0x011F)
    check_nv(NV_GROUP_INTEREST_MASK_ID, mcast_proc)
    check_nv(NV_GROUP_FORWARDING_MASK_ID, mcast_fwd)
    check_nv(NV_CARRIER_SENSE_ID, cs)
    check_nv(NV_COLLISION_AVOIDANCE_ID, ca)
    check_nv(NV_COLLISION_DETECT_ID, cd)
    
    if _needs_reboot:
        reboot()

def check_nv(param, val):
    global _needs_reboot    
    if loadNvParam(param) != val:
        saveNvParam(param, val)
        _needs_reboot = True

    