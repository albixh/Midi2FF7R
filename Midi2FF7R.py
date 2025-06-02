import sys
import rtmidi
import threading
import pydirectinput
import time

# This script listens to MIDI input and simulates key presses based on the received MIDI notes.
# It is designed to work with Final Fantasy VII Rebirth.
# Make sure to install the required libraries:
# pip install python-rtmidi pydirectinput-rgx

leftHandOctaves = 3
currentLeftOctave = 3
currentRightOctave = 4
currentLeftMode = 0 # 0 = chords, 1 = monotones
currentLeftChordMode = 3 # 1 = diminished, 2 = suspended 4th, 3 = triad, 4 = 7th, 5 = major 7th, 6 = 9th
lastNoteLeft = 'None'
lastNoteRight = 'None'

chordScanDelay = 0.005  # Delay for chord scanning

left_hand_timer = None
left_hand_timer_lock = threading.Lock()

activeLeftNotes = []
#activeRightNotes = []

# Define note names for MIDI notes
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Define chord types and their intervals
chord_types = {
    "_Maj": [0, 4, 7],                 # Major
    "_m": [0, 3, 7],                   # Minor
    "_dim": [0, 3, 6],                 # Diminished
    "_7": [0, 4, 7, 10],               # Dominant 7th
    "_9": [0, 2, 4, 7],                # Major add 9th
    "_m7": [0, 3, 7, 10],              # Minor 7th
    "_m9": [0, 2, 3, 7],               # Minor add 9th
    "_Maj7": [0, 4, 7, 11],            # Major 7th
    "_mM7": [0, 3, 7, 11],             # Minor Major 7th
    "_sus4": [0, 5, 7]                 # Suspended 4th
}

def handle_left_hand_chord():
    global activeLeftNotes, currentLeftMode, lastNoteLeft

    chordName = getChordFromNotes()
    if chordName != 'None':
        chordRoot = chordName.split('_')[0]
        if currentLeftMode == 1:
            pydirectinput.keyDown('4')
            pydirectinput.keyUp('4')
            currentLeftMode = 0
        if lastNoteLeft != chordRoot:
            pydirectinput.keyUp(getKeyFromNote(lastNoteLeft))

        chordT = chordName.split('_')[1]
        #print(f"Detected chord: {chordName} with root {chordRoot} and type {chordT}")
        setChordType(chordT)
        setHandSharp(chordRoot + str(currentLeftOctave))
        pydirectinput.keyDown(getKeyFromNote(chordRoot + str(currentLeftOctave)))
        lastNoteLeft = chordRoot + str(currentLeftOctave)
    else:
        if currentLeftMode == 0:
            pydirectinput.keyDown('4')
            pydirectinput.keyUp('4')
            currentLeftMode = 1
        if activeLeftNotes:
            note = activeLeftNotes[-1]

            setHandOctave(note)
            setHandSharp(note)
            pydirectinput.keyDown(getKeyFromNote(note))
            lastNoteLeft = note

def getChordFromNotes():
    global activeLeftNotes

    if not activeLeftNotes or len(activeLeftNotes) < 2:
        return 'None'

    # Convert note names to MIDI note numbers
    def note_name_to_midi(note):
        note_base = note[:-1]
        octave = int(note[-1])
        semitone_map = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        return semitone_map[note_base] + 12 * (octave + 1)

    midi_notes = [note_name_to_midi(n) for n in activeLeftNotes]
    unique_notes = sorted(set([n % 12 for n in midi_notes]))

    for root in unique_notes:
        intervals = [(n - root) % 12 for n in unique_notes]
        for chord_type, chord_intervals in chord_types.items():
            if set(intervals) == set(chord_intervals):
                root_name = note_names[root]
                chord_name = f"{root_name}{chord_type}"
                #print(f"chord name: {chord_name}")
                return chord_name

    return 'None'

def getKeyFromNote(noteName):
    key = None
    
    if noteName == 'None':
        return key
    
    note = noteName[0]
    octave = noteName[1]
    if octave == '#':
        note += octave
        octave = noteName[2]
    
    if (int(octave) <= leftHandOctaves):
        if( note == 'C' or note == 'C#'):
            key = 'w'
        elif( note == 'D' or note == 'D#'):
            key = 'e'
        elif( note == 'E'):
            key = 'd'
        elif( note == 'F' or note == 'F#'):
            key = 'c'
        elif( note == 'G' or note == 'G#'):
            key = 'x'
        elif( note == 'A' or note == 'A#'):
            key = 'y'
        elif( note == 'B'):
            key = 'a'
    else:
        if( note == 'C' or note == 'C#'):
            key = 'i'
        elif( note == 'D' or note == 'D#'):
            key = 'o'
        elif( note == 'E'):
            key = 'l'
        elif( note == 'F' or note == 'F#'):
            key = '.'
        elif( note == 'G' or note == 'G#'):
            key = ','
        elif( note == 'A' or note == 'A#'):
            key = 'm'
        elif( note == 'B'):
            key = 'j'
        
    if( noteName == 'C7'or noteName == 'C#7' ):
        key = 'u'


    '''if( noteName == 'C1' or noteName == 'C2' or noteName == 'C3' or noteName == 'C0' or noteName == 'C#1' or noteName == 'C#2' or noteName == 'C#3' or noteName == 'C#0'):
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
        key = 'u' '''

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
    
def setChordType(chordType):
    global leftHandOctaves
    global currentLeftChordMode
    global currentLeftMode
    oldLeftChordMode = currentLeftChordMode
    
    if chordType == 'dim':
        currentLeftChordMode = 1
        setMinorChord(0)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('1')
        pydirectinput.keyUp('1')
        pydirectinput.keyDown('1')
        pydirectinput.keyUp('1')
    elif chordType == 'sus4':
        currentLeftChordMode = 2
        setMinorChord(0)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('1')
        pydirectinput.keyUp('1')
    elif chordType == 'Maj':
        currentLeftChordMode = 3
        setMinorChord(0)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
    elif chordType == 'm':
        currentLeftChordMode = 3
        setMinorChord(1)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
    elif chordType == '7':
        currentLeftChordMode = 4
        setMinorChord(0)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
    elif chordType == 'm7':
        currentLeftChordMode = 4
        setMinorChord(1)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
    elif chordType == 'Maj7':
        currentLeftChordMode = 5
        setMinorChord(0)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
    elif chordType == 'mMj7':
        currentLeftChordMode = 5
        setMinorChord(1)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
    elif chordType == '9':
        currentLeftChordMode = 6
        setMinorChord(0)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
    elif chordType == 'm9':
        currentLeftChordMode = 6
        setMinorChord(1)
        pydirectinput.keyDown('2')
        pydirectinput.keyUp('2')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')
        pydirectinput.keyDown('3')
        pydirectinput.keyUp('3')


    '''steps = currentLeftChordMode - oldLeftChordMode

    if steps < 0:
        for i in range(abs(steps)):        
            if currentLeftChordMode == leftHandOctaves:
                return
            pydirectinput.keyDown('3')
            pydirectinput.keyUp('3')
    elif steps > 0:
        for i in range(abs(steps)):
            if currentLeftChordMode == 1:
                return
            pydirectinput.keyDown('1')
            pydirectinput.keyUp('1')'''

def setMinorChord(value):
    if value == 1:
        pydirectinput.keyDown("ctrl")
    else:
        pydirectinput.keyUp("ctrl")
            
def setHandSharp(noteName):
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
    global currentLeftOctave
    global currentRightOctave

    octave = noteName[1]
    if octave == '#':
        octave = noteName[2]
    if int(octave) <= leftHandOctaves:
        steps = currentLeftOctave - int(octave)
        if steps < 0:
            for i in range(abs(steps)):
                if currentLeftOctave == leftHandOctaves:
                    return
                pydirectinput.keyDown('3')
                pydirectinput.keyUp('3')
        elif steps > 0:
            for i in range(abs(steps)):
                if currentLeftOctave == 1:
                    return
                pydirectinput.keyDown('1')
                pydirectinput.keyUp('1')

        currentLeftOctave = int(octave)

    else:
        global currentRightOctave
        if( int(octave) > 6):
            octave = '6'
        steps = currentRightOctave - int(octave)

        if steps < 0:
            for i in range(abs(steps)):
                if currentRightOctave == 6:
                    return
                pydirectinput.keyDown('9')
                pydirectinput.keyUp('9')
        elif steps > 0:
            for i in range(abs(steps)):
                if currentRightOctave == leftHandOctaves+1:
                    return
                pydirectinput.keyDown('7')
                pydirectinput.keyUp('7')

        currentRightOctave = int(octave)
    
def on_midi_input(midi, port):
    global lastNoteLeft
    global lastNoteRight
    global currentLeftOctave
    global currentRightOctave
    global chordScanDelay
    noteName = midi.getMidiNoteName(midi.getNoteNumber())
    if midi.isNoteOn():
        octave = noteName[1]
        if octave == '-' or octave == '0':
            currentLeftOctave = 3
            currentRightOctave = 4

            pydirectinput.keyDown('2')
            pydirectinput.keyUp('2')
            pydirectinput.keyDown('4')
            pydirectinput.keyUp('4')
            pydirectinput.keyDown('2')
            pydirectinput.keyUp('2')
            pydirectinput.keyDown('4')
            pydirectinput.keyUp('4')
            pydirectinput.keyDown('8')
            pydirectinput.keyUp('8')

            return

        #print ('%s: ON: ' % port, noteName, midi.getVelocity())
        if getHand(noteName) == 'left':
            global currentLeftModem
            pydirectinput.keyUp(getKeyFromNote(lastNoteLeft))
            activeLeftNotes.append(noteName)

            def start_left_timer():
                global left_hand_timer, chordScanDelay, lastNoteLeft
                with left_hand_timer_lock:
                    # Always release the previous key first
                    pydirectinput.keyUp(getKeyFromNote(lastNoteLeft))
                    
                    if left_hand_timer and left_hand_timer.is_alive():
                        left_hand_timer.cancel()
                        #return
                    left_hand_timer = threading.Timer(chordScanDelay, handle_left_hand_chord)
                    left_hand_timer.start()

            #start_left_timer()
            handle_left_hand_chord()

        elif getHand(noteName) == 'right':
            pydirectinput.keyUp(getKeyFromNote(lastNoteRight))
            lastNoteRight = noteName
            #activeRightNotes.append(noteName)
            
            setHandOctave(noteName)
            setHandSharp(noteName)
            pydirectinput.keyDown(getKeyFromNote(noteName))


    elif midi.isNoteOff():
        #print ('%s: OFF:' % port, noteName)
        if getHand(noteName) == 'left':
            global chordScanDelay

            chordName = getChordFromNotes()

            if chordName != 'None':
                if left_hand_timer and left_hand_timer.is_alive():
                    left_hand_timer.cancel()
                chordRoot = chordName.split('_')[0] + str(currentLeftOctave)
                if lastNoteLeft == chordRoot:
                    pydirectinput.keyUp(getKeyFromNote(lastNoteLeft))
                    if noteName in activeLeftNotes:
                        activeLeftNotes.remove(noteName)
                    lastNoteLeft = 'None'
            if lastNoteLeft == noteName:
                pydirectinput.keyUp(getKeyFromNote(noteName))
            if noteName in activeLeftNotes:
                activeLeftNotes.remove(noteName)

            pydirectinput.keyUp("ctrl")
            #pydirectinput.keyUp("shift")

        elif getHand(noteName) == 'right':
            pydirectinput.keyUp(getKeyFromNote(noteName))
            pydirectinput.keyUp("-")

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
with left_hand_timer_lock:
    if left_hand_timer and left_hand_timer.is_alive():
        left_hand_timer.cancel()
for c in collectors:
    c.quit = True