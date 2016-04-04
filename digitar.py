# Digitar algorithm for plucked-string synthesis
# Demo with "Frere Jacques"
# Abe Karplus, 2016

import wave
import array

sampling = 48e3 # Hz
bpm = 100

notenames = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def notepitch(n):
    step = notenames[n[0]]
    octind = 2
    if n[1] == '#':
        step += 1
    elif n[1] == 'b':
        step -= 1
    else:
        octind = 1
    octv = int(n[octind:])
    exp = 12*octv+step-57
    return 440 * 2**(exp/12)

def lerp(tbl, phase):
    whole, frac = phase >> 16, phase & 0xFFFF
    x0 = tbl[whole]
    x1 = tbl[(whole+1)&0xFF]
    return ((x0 * ((1<<16)-frac)) + (x1 * frac))>>16

def randwords():
    y = 2463534242
    while True:
        y ^= (y << 13) & 0xFFFFFFFF
        y ^= (y >> 17)
        y ^= (y << 5) & 0xFFFFFFFF
        yield (y & 0xFFFF) - 32768
        yield (y >> 16) - 32768

rw = randwords()
def pluck(note, dur):
    out = []
    tbl = [next(rw)//4 for n in range(256)]
    phase = 0
    pos = 0
    inc = int(round(notepitch(note)*2**24/sampling))
    for n in range(int(dur*sampling)):
        tbl[pos] = (tbl[pos] + tbl[(pos-1)&0xFF])//2
        pos += 1
        pos &= 0xFF
        out.append(lerp(tbl, phase))
        phase += inc
        phase &= 0xFFFFFF
    return out

crochet = 60/bpm

song = []
songdur = 0.0
dampfrac = 1/8

def addnotes(notes, tm):
    global songdur
    for n in notes:
        song.append((n, songdur, tm*(1-dampfrac), tm*dampfrac))
    songdur += tm

def quarter(notes):
    addnotes(notes, crochet)

def eighth(notes):
    addnotes(notes, crochet/2)

def half(notes):
    addnotes(notes, crochet*2)

quarter(['F3'])
quarter(['G3'])
quarter(['A3'])
quarter(['F3'])
quarter(['F3'])
quarter(['G3'])
quarter(['A3'])
quarter(['F3'])
quarter(['A3'])
quarter(['B3'])
half(['C4'])
quarter(['A3'])
quarter(['B3'])
half(['C4'])
eighth(['C4'])
eighth(['D4'])
eighth(['C4'])
eighth(['B3'])
quarter(['A3'])
quarter(['F3'])
eighth(['C4'])
eighth(['D4'])
eighth(['C4'])
eighth(['B3'])
quarter(['A3'])
quarter(['F3'])
quarter(['F3'])
quarter(['C3'])
half(['F3'])
quarter(['F3'])
quarter(['C3'])
half(['F3'])

with wave.open('pluck.wav', 'wb') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sampling)
    
    out = array.array('h', [0]*int(sampling*songdur))
    for note, start, dur, damp in song:
        buf = pluck(note, dur+damp)
        for n in range(int(dur*sampling)):
            out[n+int(start*sampling)] += buf[n]
        for n in range(int(dur*sampling), int((dur+damp)*sampling)):
            out[n+int(start*sampling)] += int(buf[n]*((dur+damp)*sampling-n)/(damp*sampling))

    f.writeframes(array.array('h', out))
