# Quick-n-dirty Fixed Point library

FP_DIGITS = 2 # 2 digits past the decimal point
FP_SCALE = 10 ** FP_DIGITS
FP_HALF_SCALE = 10 ** (FP_DIGITS >> 1) # any remainder is dealt with in the code below

POINT_FIVE = 5 * (FP_SCALE / 10) # Used here for ROUNDING

def debug_FP_SCALE():
    return FP_SCALE

def debug_FP_HALF_SCALE():
    return FP_HALF_SCALE

def print_FP(num):
    if num < 0:
        print '-',
        num *= -1
    print num / FP_SCALE,
    print '.',
    print num % FP_SCALE,

def print_labeled_FP(label, num):
    print label,
    print_FP(num)

def to_FP(integer, fraction):
    if integer < 0:
        return integer * FP_SCALE - fraction
    else:
        return integer * FP_SCALE + fraction

def from_FP(fixed_point):
    return (fixed_point + POINT_FIVE) / FP_SCALE

def multiply_FP(a, b):
    # To maximize precision, attempt to apply the scaling adjustment afterwards
    # This requires working with absolute values, and applying the sign at the end
    sign = 1
    if a < 0:
        a *= -1
        if b < 0:
            b *= -1
        else:
            sign = -1
    else:
        if b < 0:
            b *= -1
            sign = -1

    temp = a * b
    if (temp < a) or (temp < b): # Overflow!
        # We will have to prescale instead of postscale
        if (FP_DIGITS & 1): # if odd number, won't divide evenly
            if a > b:
                a /= (FP_HALF_SCALE * 10)
                b /= FP_HALF_SCALE
            else:
                a /= FP_HALF_SCALE
                b /= (FP_HALF_SCALE * 10)
        else:
            a /= FP_HALF_SCALE
            b /= FP_HALF_SCALE
        return (a / b) * sign
    else:
        temp /= FP_SCALE
        return temp * sign

def divide_FP(a, b):
    return a / (b / FP_SCALE)
