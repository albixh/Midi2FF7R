import sys
import rtmidi
import threading
import pydirectinput

# This script listens to MIDI input and simulates key presses based on the received MIDI notes.
# It is designed to work with Final Fantasy VII Rebirth.
# Make sure to install the required libraries:
# pip install python-rtmidi pydirectinput-rgx

leftHandOctaves = 3
currentLeftOctave = 3
currentRightOctave = 4
lastNoteLeft = 'None'
lastNoteRight = 'None'

def getKeyFromNote(noteName):
    key = None
    if( noteName == 'C1' or noteName == 'C2' or noteName == 'C3' or noteName == 'C0' or noteName == 'C#1' or noteName == 'C#2' or noteName == 'C#3' or noteName == 'C#0'):
        key = 'w'
    elif( noteName == 'D1' or noteName == 'D2' or noteName == 'D3' or noteName == 'D0' or noteName == 'D#1' or noteName == 'D#2' or noteName == 'D#3' or noteName == 'D#0'):
        key = 'e'
    elif( noteName == 'E1' or noteName == 'E2' or noteName == 'E3' or noteName == 'E0'):
        key = 'd'
    elif( noteName == 'F1' or noteName == 'F2' or noteName == 'F3' or noteName == 'F0' or noteName == 'F#1' or noteName == 'F#2' or noteName == 'F#3' or noteName == 'F#0'):
        key = 'c'
    elif( noteName == 'G1' or noteName == 'G2' or noteName == 'G3' or noteName == 'G0' or noteName == 'G#1' or noteName == 'G#2' or noteName == 'G#3' or noteName == 'G#0'):
        key = 'x'
    elif( noteName == 'A1' or noteName == 'A2' or noteName == 'A3' or noteName == 'A0' or noteName == 'A#1' or noteName == 'A#2' or noteName == 'A#3' or noteName == 'A#0'):
        key = 'y'
    elif( noteName == 'B1' or noteName == 'B2' or noteName == 'B3' or noteName == 'B0'):
        key = 'a'

    if( noteName == 'C4' or noteName == 'C5' or noteName == 'C6' or noteName == 'C#4' or noteName == 'C#4' or noteName == 'C#5' or noteName == 'C#6'):
        key = 'i'
    elif( noteName == 'D4' or noteName == 'D5' or noteName == 'D6' or noteName == 'D7' or noteName == 'D#4' or noteName == 'D#5' or noteName == 'D#6' or noteName == 'D#7'):
        key = 'o'
    elif( noteName == 'E4' or noteName == 'E5' or noteName == 'E6' or noteName == 'E7'):
        key = 'l'
    elif( noteName == 'F4' or noteName == 'F5' or noteName == 'F6' or noteName == 'F7' or noteName == 'F#4' or noteName == 'F#5' or noteName == 'F#6' or noteName == 'F#7'):
        key = '.'
    elif( noteName == 'G4' or noteName == 'G5' or noteName == 'G6' or noteName == 'G7' or noteName == 'G#4' or noteName == 'G#5' or noteName == 'G#6' or noteName == 'G#7'):
        key = ','
    elif( noteName == 'A4' or noteName == 'A5' or noteName == 'A6' or noteName == 'A7' or noteName == 'A#4' or noteName == 'A#5' or noteName == 'A#6' or noteName == 'A#7'):
        key = 'm'
    elif( noteName == 'B4' or noteName == 'B5' or noteName == 'B6' or noteName == 'B7'):
        key = 'j'
    elif( noteName == 'C5' or noteName == 'C6' or noteName == 'C7' or noteName == 'C8' or noteName == 'C#5' or noteName == 'C#6' or noteName == 'C#7' or noteName == 'C#8'):
        key = 'u'

    return key

#defines what hand the note is played with
def getHand(noteName):
    global leftHandOctaves

    octave = noteName[1]
    if octave == '#':
        octave = noteName[2]
    if octave == '-':
        return 'left'
    if int(octave) <= leftHandOctaves:
        return 'left'
    else:
        return 'right'

def setHandSharp(noteName):
    global leftHandOctaves

    strSharp = noteName[1]

    if strSharp != '#':
        if getHand(noteName) == 'left':
            pydirectinput.keyUp("shift")
        elif getHand(noteName) == 'right':
            pydirectinput.keyUp("-")
    else:
        if getHand(noteName) == 'left':
            pydirectinput.keyDown('shift')
        elif getHand(noteName) == 'right':
            pydirectinput.keyDown('-')

def setHandOctave(noteName):
    global leftHandOctaves

    octave = noteName[1]
    if octave == '-' or octave == '0':
        pydirectinput.keyDown('1')
        pydirectinput.keyUp('1')
        pydirectinput.keyDown('1')
        pydirectinput.keyUp('1')
        pydirectinput.keyDown('1')
        pydirectinput.keyUp('1')
        pydirectinput.keyDown('1')
        pydirectinput.keyUp('1')
        return
    if octave == '#':
        octave = noteName[2]
    if int(octave) <= leftHandOctaves:
        global currentLeftOctave
        steps = currentLeftOctave - int(octave)
        if steps < 0:
            if currentLeftOctave == 3:
                return
            for i in range(abs(steps)):
                pydirectinput.keyDown('3')
                pydirectinput.keyUp('3')
        elif steps > 0:
            if currentLeftOctave == 1:
                return
            for i in range(abs(steps)):
                pydirectinput.keyDown('1')
                pydirectinput.keyUp('1')

        currentLeftOctave = int(octave)

    else:
        global currentRightOctave
        if( int(octave) > 6):
            octave = '6'
        steps = currentRightOctave - int(octave)

        if steps < 0:
            if currentRightOctave == 6:
                return
            for i in range(abs(steps)):
                pydirectinput.keyDown('9')
                pydirectinput.keyUp('9')
        elif steps > 0:
            if currentRightOctave == 4:
                return
            for i in range(abs(steps)):
                pydirectinput.keyDown('7')
                pydirectinput.keyUp('7')

        currentRightOctave = int(octave)
    
def on_midi_input(midi, port):
    global lastNoteLeft
    global lastNoteRight
    noteName = midi.getMidiNoteName(midi.getNoteNumber())
    if midi.isNoteOn():
        #print ('%s: ON: ' % port, noteName, midi.getVelocity())
        if getHand(noteName) == 'left':
            pydirectinput.keyUp(getKeyFromNote(lastNoteLeft))
            lastNoteLeft = noteName
        elif getHand(noteName) == 'right':
            pydirectinput.keyUp(getKeyFromNote(lastNoteRight))
            lastNoteRight = noteName

        setHandOctave(noteName)
        setHandSharp(noteName)
        pydirectinput.keyDown(getKeyFromNote(noteName))

    elif midi.isNoteOff():
        #print ('%s: OFF:' % port, noteName)

        if noteName == lastNoteLeft or noteName == lastNoteRight:
            if getHand(noteName) == 'left' and lastNoteLeft != 'None':
                pydirectinput.keyUp(getKeyFromNote(lastNoteLeft))
                lastNoteLeft = 'None'
            elif getHand(noteName) == 'right' and lastNoteRight != 'None':
                pydirectinput.keyUp(getKeyFromNote(lastNoteRight))
                lastNoteRight = 'None'


    elif midi.isController():
        print ('%s: CONTROLLER' % port, midi.getControllerNumber(), midi.getControllerValue())

class Collector(threading.Thread):
    def __init__(self, device, port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.quit = False

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
            if self.quit:
                return
            msg = self.device.getMessage()
            if msg:
                on_midi_input(msg, self.portName)


dev = rtmidi.RtMidiIn()
collectors = []
for i in range(dev.getPortCount()):
    device = rtmidi.RtMidiIn()
    print('OPENING',dev.getPortName(i))
    collector = Collector(device, i)
    collector.start()
    collectors.append(collector)


print('HIT ENTER TO EXIT')
sys.stdin.read(1)
for c in collectors:
    c.quit = True