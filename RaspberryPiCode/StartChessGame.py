# Interactive Chessboard - www.DIYmachines.co.uk
# This codes includes large sections kindly shared on www.chess.fortherapy.co.uk, which itself incorporates alot of other peoples code.
# Please feel free to modify, adapt and share. Any excisting licenses included must remain intact as well as including acknowledgment to those who have contribued.
# This program plays chess using Stockfish the open source chess engine, using the ChessBoard library to manage the board.
# It is written in Python 2.7 because chessboard is.
# It assumes you have got the python libraries chessboard, subprocess and time


# initiate chessboard
from ChessBoard import ChessBoard
import subprocess, time, serial, sys, traceback, re, threading
from datetime import datetime
maxchess = ChessBoard()


def dbg(msg):
    """Timestamped debug print that flushes immediately so we see it over SSH."""
    ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print('[DBG {0}] {1}'.format(ts, msg), flush=True)


def log_serial_state(ser_obj, label=''):
    """Dump everything we can see about the serial port state."""
    try:
        info = {
            'label': label,
            'port': getattr(ser_obj, 'port', '?'),
            'baudrate': getattr(ser_obj, 'baudrate', '?'),
            'timeout': getattr(ser_obj, 'timeout', '?'),
            'is_open': getattr(ser_obj, 'is_open', '?'),
        }
        try:
            info['in_waiting'] = ser_obj.in_waiting
        except Exception as e:
            info['in_waiting'] = 'ERR: {0}'.format(e)
        try:
            info['out_waiting'] = ser_obj.out_waiting
        except Exception as e:
            info['out_waiting'] = 'ERR: {0}'.format(e)
        dbg('SERIAL_STATE {0}'.format(info))
    except Exception as e:
        dbg('SERIAL_STATE failed: {0}'.format(e))


SERIAL_PORT = '/dev/ttyUSB0'   # for Pi Zero use '/dev/ttyAMA0' and for others use '/dev/ttyUSB0'.
SERIAL_BAUD = 9600

# Tolerant fallback for the "heypi" prefix. The Arduino occasionally drops a
# single byte from its serial output when NeoPixel.show() disables interrupts
# during a UART transmission, so a strict "heypi" check loses real messages
# (e.g. "heyp-4285" instead of "heypi-4285"). This regex requires the literal
# "hey" anchor, allows 0-3 chars where "pi" should be, and then expects one of
# the known protocol typecodes the Arduino emits.
HEYPI_RE = re.compile(r'^hey[a-z]{0,3}([mngxc\-g])(.*)$', re.IGNORECASE)

if __name__ == '__main__':
    dbg('Opening serial port {0} @ {1} baud, timeout=1s'.format(SERIAL_PORT, SERIAL_BAUD))
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    except Exception as e:
        dbg('FATAL: failed to open serial port: {0!r}'.format(e))
        traceback.print_exc()
        raise
    dbg('Serial port opened OK')
    log_serial_state(ser, 'after-open')

    # --- Force-reset the Arduino by pulsing DTR ---
    # Some boards (or USB-serial chips with the auto-reset cap removed) don't
    # reset just by opening the port. Without a reset, the Arduino sketch stays
    # in whatever state the previous run left it in — typically stuck inside
    # receiveMoveFromPi() waiting for a "heyArduinom..." that will never come.
    # Pulsing DTR low->high forces the bootloader to run, so the Arduino starts
    # fresh in setup() -> waitForPiToStart() every time we launch.
    try:
        dbg('Forcing Arduino reset: DTR=False (high)')
        ser.dtr = False
        time.sleep(0.25)
        dbg('Forcing Arduino reset: DTR=True (low) — pulse complete')
        ser.dtr = True
    except Exception as e:
        dbg('DTR pulse FAILED (continuing anyway): {0!r}'.format(e))

    ser.flush()
    dbg('ser.flush() done')

import time
dbg('Sleeping 3s to let Arduino bootloader run + setup() complete')
time.sleep(3)
log_serial_state(ser, 'after-3s-sleep')
ser.reset_input_buffer()
dbg('ser.reset_input_buffer() done — discarded any boot-time noise')
log_serial_state(ser, 'after-reset-input-buffer')

# initiate stockfish chess engine

engine = subprocess.Popen(
    'stockfish',
    universal_newlines=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    bufsize=1,   # line-buffered: every '\n' flushes to Stockfish immediately
    )

def get():
    return ""

def putAdafruit(command):
    print('\nTrying to send to AdafruitIO:\n\t'+command)
    remotePlayer.stdin.write("send\n")
    remotePlayer.stdin.write(colourChoice+'\n')
    remotePlayer.stdin.write(command+'\n')
    while True :
        text = remotePlayer.stdout.readline().strip()
        if text[6:17] == 'piece moved':
            print(text)
            break


def getAdafruit():
    print('\nTrying to read remote boards move from AdafruitIO:\n\t')
    remotePlayer.stdin.write("receive\n")
    remotePlayer.stdin.write(colourChoice+'\n')
    while True :
        text = remotePlayer.stdout.readline().strip()
        #if text[0:11] == 'Piece moved':
        print('The remote move was: ' + text)
        return text


def sget():

    # using the 'isready' command (engine has to answer 'readyok')
    # to indicate current last line of stdout
    stx=""
    engine.stdin.write('isready\n')
    engine.stdin.flush()
    print('\nengine:')
    while True :
        text = engine.stdout.readline().strip()
        #if text == 'readyok':
         #   break
        if text !='':
            print('\t'+text)
        if text[0:8] == 'bestmove':
            mtext=text
            return mtext

def getboard():
    dbg('***************** ASKING ARDUINO FOR INPUT *****************')
    dbg('getboard() ENTER — waiting for line from Arduino')
    log_serial_state(ser, 'getboard-enter')

    poll_count = 0
    last_log_t = time.time()
    started_t = time.time()
    non_heypi_lines = 0
    stuck_warned = False

    while True:
        poll_count += 1

        # Periodic heartbeat so we know the loop is alive (don't spam every iteration)
        now = time.time()
        if now - last_log_t >= 5.0:
            try:
                iw = ser.in_waiting
            except Exception as e:
                iw = 'ERR: {0!r}'.format(e)
            dbg('getboard() still polling — polls={0} in_waiting={1}'.format(poll_count, iw))
            last_log_t = now

        try:
            in_w = ser.in_waiting
        except Exception as e:
            dbg('getboard() ser.in_waiting raised: {0!r}'.format(e))
            traceback.print_exc()
            log_serial_state(ser, 'in_waiting-exception')
            raise

        if in_w > 0:
            dbg('getboard() in_waiting={0} — about to readline()'.format(in_w))
            try:
                raw = ser.readline()
            except serial.SerialException as e:
                dbg('getboard() SerialException during readline: {0!r}'.format(e))
                log_serial_state(ser, 'readline-SerialException')
                traceback.print_exc()
                # Try a recovery: drain + small sleep + retry once so we can see
                # whether this is a transient hiccup or a real disconnect.
                try:
                    dbg('getboard() attempting recovery: reset_input_buffer + 0.5s sleep + retry readline')
                    ser.reset_input_buffer()
                    time.sleep(0.5)
                    raw = ser.readline()
                    dbg('getboard() recovery readline returned: {0!r}'.format(raw))
                except Exception as e2:
                    dbg('getboard() recovery FAILED: {0!r}'.format(e2))
                    traceback.print_exc()
                    log_serial_state(ser, 'recovery-failed')
                    raise
            except Exception as e:
                dbg('getboard() unexpected exception during readline: {0!r}'.format(e))
                traceback.print_exc()
                log_serial_state(ser, 'readline-other-exception')
                raise

            dbg('getboard() raw bytes from readline: {0!r} (len={1})'.format(raw, len(raw)))

            if not raw:
                dbg('getboard() readline returned empty — continuing to poll')
                continue

            try:
                btxt = raw.decode('utf-8').rstrip().lower()
            except UnicodeDecodeError as e:
                dbg('getboard() UTF-8 decode failed for {0!r}: {1!r} — skipping'.format(raw, e))
                continue

            dbg('getboard() decoded line: {0!r}'.format(btxt))

            if btxt.startswith('heypixshutdown'):
                dbg('getboard() shutdown command received')
                shutdownPi()
                break

            if btxt.startswith('heypi'):
                btxt = btxt[len('heypi'):]
                dbg('getboard() stripped heypi prefix -> {0!r}'.format(btxt))
            else:
                m = HEYPI_RE.match(btxt)
                if m:
                    recovered = m.group(1) + m.group(2)
                    dbg('getboard() RECOVERED corrupted prefix from {0!r} -> {1!r}'.format(btxt, recovered))
                    btxt = recovered
                else:
                    non_heypi_lines += 1
                    dbg('getboard() line did not start with heypi — ignoring (non-heypi count={0})'.format(non_heypi_lines))
                    # If we've been getting Arduino chatter but no heypi protocol
                    # lines for >15s, the Arduino is alive but in the wrong state
                    # (e.g. stuck mid-game from a previous run, or running a
                    # different sketch). Surface this loudly so it's not silent.
                    if not stuck_warned and (time.time() - started_t) > 15.0 and non_heypi_lines >= 2:
                        dbg('!!! ARDUINO LOOKS STUCK — receiving non-protocol chatter but no "heypi..." reply')
                        dbg('!!! Likely cause: Arduino did not reset on serial open, so it is past waitForPiToStart()')
                        dbg('!!! Action: physically press RESET on the Arduino, OR power-cycle it, then re-run ./start.sh')
                        stuck_warned = True
                    continue

            # Do NOT strip a leading 'm' here. The main loop dispatches on
            # bmessage[0] expecting 'm' for moves, and bmove() reads
            # bmessage[1:5] for the from/to squares. Every other caller (mode,
            # skill, movetime) strips its own typecode via [1:] / [1:3] etc.
            # The legacy StartChessGameStockfish.py.getboard() has the same
            # behaviour — return the payload with typecode intact.

            dbg('***************** GOT INPUT FROM ARDUINO: {0!r} *****************'.format(btxt))
            dbg('getboard() RETURN {0!r}'.format(btxt))
            print(btxt)
            return btxt


def sendtoboard(stxt):
    """ sends a text string to the board """
    dbg('***************** SENDING OUTPUT TO ARDUINO: {0!r} *****************'.format(stxt))
    dbg('sendtoboard() ENTER payload={0!r}'.format(stxt))
    log_serial_state(ser, 'sendtoboard-enter')
    print("\n Sent to board: heyArduino" + stxt)
    payload = bytes(str(stxt).encode('utf8'))
    full = b"heyArduino" + payload + b"\n"
    dbg('sendtoboard() sleeping 2s before write (preserves original timing)')
    time.sleep(2)
    dbg('sendtoboard() writing {0} bytes: {1!r}'.format(len(full), full))
    try:
        n = ser.write(full)
        dbg('sendtoboard() write() returned {0}'.format(n))
        try:
            ser.flush()
            dbg('sendtoboard() flush() done')
        except Exception as e:
            dbg('sendtoboard() flush() raised: {0!r}'.format(e))
    except Exception as e:
        dbg('sendtoboard() write FAILED: {0!r}'.format(e))
        traceback.print_exc()
        log_serial_state(ser, 'sendtoboard-write-failed')
        raise
    log_serial_state(ser, 'sendtoboard-after-write')


def newgame():
    sendToScreen('NEW','GAME','','30')
    get()
    put('uci')
    get()

    skill = skillFromArduino
    if skill is None:
        print("Setup desync detected. Restarting setup phase.")
        return None

    if not skill.isdigit():
        print("Invalid skill received:", skill)
        return None

    skill = str(int(skill))

    put('setoption name Skill Level value ' + skill)
    get()
    put('setoption name Hash value 128')
    get()

    put('ucinewgame')
    ser.reset_input_buffer()

    maxchess.resetBoard()
    maxchess.setPromotion(maxchess.QUEEN)

    print("Promotion set to ")
    print(maxchess.getPromotion())

    fmove = ""
    brdmove=""
    time.sleep(2)
    sendToScreen ('Please enter','your move:','')
    return fmove

def newgameOnline():
    maxchess.resetBoard()
    maxchess.setPromotion(maxchess.QUEEN)
    print("Promotion set to ")
    print(maxchess.getPromotion())
    fmove=""
    brdmove=""
    return fmove



def bmove(fmove):
    """ assume we get a command of the form ma1a2 from board"""
    fmove=fmove
    # Get a move from the board
    brdmove = bmessage[1:5].lower()
    # now validate move
    # if invalid, get reason & send back to board
      #  maxchess.addTextMove(move)
    if maxchess.addTextMove(brdmove) == False :
                        etxt = "error"+ str(maxchess.getReason())+brdmove
                        maxchess.printBoard()
                        sendToScreen ('Illegal move!','Enter new','move...','14')
                        sendtoboard(etxt)
                        return fmove

#  elif valid  make the move and send Fen to board

    else:
        maxchess.printBoard()
        print ("brdmove")
        print(brdmove)
        sendToScreen (brdmove[0:2] + '->' + brdmove[2:4] ,'','Thinking...','20')

        fmove =fmove+" " +brdmove

        cmove = "position startpos moves"+fmove
        print (cmove)

            #        if fmove == True :
            #                move = "position startpos moves "+move
            #        else:
            #               move ="position fen "+maxfen

        # put('ucinewgame')
        # get()


        put(cmove)
        # send move to engine & get engines move


        put("go movetime " +movetime)
        # time.sleep(6)
        # text = get()
        # put('stop')
        text = sget()
        print (text)
        smove = text[9:13]
        hint = text[21:25]
        if maxchess.addTextMove(smove) != True :
                        stxt = "e"+ str(maxchess.getReason())+smove
                        maxchess.printBoard()
                        sendtoboard(stxt)

        else:
                        temp=fmove
                        fmove =temp+" " +smove
                        stx = smove+hint
                        maxchess.printBoard()
                        # maxfen = maxchess.getFEN()
                        print ("computer move: " +smove)
                        sendToScreen (smove[0:2] + '->' + smove[2:4] ,'','Your go...','20')
                        smove ="m"+smove
                        sendtoboard(smove +"-"+ hint)
                        return fmove

def bmoveOnline(fmove):
    """ assume we get a command of the form ma1a2 from board"""
    fmove=fmove
    print ("F move is now set to ")
    print(fmove)
    # Extract the move from the message received from the chessboard
    brdmove = bmessage[1:5].lower()
    print ("Brdmove is now set to ")
    print(brdmove)
    # now validate move
    # if invalid, get reason & send back to board
    #  maxchess.addTextMove(move)
    if maxchess.addTextMove(brdmove) == False :
        print("The move is illegal")
        etxt = "error"+ str(maxchess.getReason())+brdmove
        maxchess.printBoard()
        sendtoboard(etxt)
        return fmove

#  elif valid  make the move and send to AdafruitIO

    else:
        print("The move is legal")
        maxchess.printBoard()
        print ("brdmove")
        print(brdmove)
        putAdafruit(brdmove)

        fmove =fmove+" " +brdmove

        cmove = "position startpos moves"+fmove
        print (cmove)
        sendToScreen ('Waiting for' ,'the other','Player...','20')


        #Wait for remote player move to be posted online.
        text = getAdafruit()
        print (text)
        smove = text
        hint = "xxxx"
        temp=fmove
        fmove =temp+" " +smove
        stx = smove+hint
        maxchess.printBoard()
        print ("Remote players move: " +smove)

        if maxchess.addTextMove(smove) != True :
                stxt = "e"+ str(maxchess.getReason())+smove
                maxchess.printBoard()
                sendtoboard(stxt)

        else:
                temp=fmove
                fmove =temp+" " +smove
                stx = smove+hint
                maxchess.printBoard()
                sendToScreen (smove[0:2] + '->' + smove[2:4] ,'','Your go...','20')
                smove ="m"+smove
                sendtoboard(smove +"-"+ hint)

        return fmove


def put(command):
    print('\nyou:\n\t'+command)
    engine.stdin.write(command+'\n')
    engine.stdin.flush()  # belt-and-braces in case bufsize=1 isn't honored

def shutdownPi():
    sendToScreen ('Shutting down...','Wait 20s then','disconnect power.')
    time.sleep(5)
    from subprocess import call
    call("sudo nohup shutdown -h now", shell=True)
    time.sleep(10)

def sendToScreen(line1, line2, line3, size='14'):
    """Send three lines of text to the small OLED screen.

    Args are passed as separate list elements (NOT '-a ' + line1) so getopt
    parses them correctly without a leading-space artifact.
    Stderr is captured in a daemon thread so any printToOLED.py crash gets
    surfaced through the dbg() log instead of silently disappearing.
    """
    dbg('sendToScreen() spawn: lines={0!r}|{1!r}|{2!r} size={3!r}'.format(line1, line2, line3, size))
    screenScriptToRun = [
        "python3", "/home/pi/SmartChess/RaspberryPiCode/printToOLED.py",
        '-a', str(line1), '-b', str(line2), '-c', str(line3), '-s', str(size),
    ]
    try:
        proc = subprocess.Popen(screenScriptToRun, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        dbg('sendToScreen() Popen FAILED: {0!r}'.format(e))
        return

    def _drain(p):
        try:
            out, err = p.communicate(timeout=10)
            if p.returncode != 0 or err:
                dbg('OLED subprocess rc={0} stderr={1!r} stdout={2!r}'.format(p.returncode, err, out))
        except Exception as e:
            dbg('OLED subprocess drain failed: {0!r}'.format(e))

    threading.Thread(target=_drain, args=(proc,), daemon=True).start()

#Choose a moe of gameplay on the Arduino
dbg('=== STARTUP: about to send ChooseMode to Arduino ===')
time.sleep(1)
sendtoboard("ChooseMode")
print ("Waiting for mode of play to be decided on the Arduino")
sendToScreen ('Choose opponent:','1) Against PC','2) Remote human')
dbg('=== STARTUP: calling getboard() to read gameplay mode ===')
_raw_mode = getboard()
dbg('STARTUP gameplay mode raw return={0!r}'.format(_raw_mode))
gameplayMode = _raw_mode[1:].lower()
print ("Requested gameplay mode:")
print(gameplayMode)
dbg('STARTUP parsed gameplayMode={0!r}'.format(gameplayMode))


if gameplayMode == 'stockfish':
    while True:
        dbg('=== STOCKFISH branch: sending ReadyStockfish ===')
        sendtoboard("ReadyStockfish")

        # get intial settings (such as level)
        print ("Waiting for level command to be received from Arduino")
        sendToScreen ('Choose computer','difficulty level:','(0 -> 8)')
        dbg('=== STOCKFISH: calling getboard() for skill level ===')
        _raw_skill = getboard()
        dbg('STOCKFISH skill raw return={0!r}'.format(_raw_skill))
        skillFromArduino = _raw_skill[1:3].lower()
        # If a heypi line gets corrupted past prefix recovery (e.g. it gets
        # parsed as a move 'M...' or color 'C...'), the value here won't be
        # digits. Discard and re-read until we get a valid skill payload.
        while not skillFromArduino.isdigit():
            dbg('!!! skill payload {0!r} from raw {1!r} is not digits — discarding and re-reading'.format(skillFromArduino, _raw_skill))
            _raw_skill = getboard()
            dbg('STOCKFISH skill raw return (retry)={0!r}'.format(_raw_skill))
            skillFromArduino = _raw_skill[1:3].lower()
        print ("Requested skill level:")
        print(skillFromArduino)
        dbg('STOCKFISH parsed skillFromArduino={0!r}'.format(skillFromArduino))

        # get intial settings (such as move time)
        print ("Waiting for move time command to be received from Arduino")
        sendToScreen ('Choose computer','move time:','(0 -> 8)')
        dbg('=== STOCKFISH: calling getboard() for move time ===')
        _raw_movetime = getboard()
        dbg('STOCKFISH movetime raw return={0!r}'.format(_raw_movetime))
        movetimeFromArduino = _raw_movetime[1:].lower()
        while not movetimeFromArduino.isdigit():
            dbg('!!! movetime payload {0!r} from raw {1!r} is not digits — discarding and re-reading'.format(movetimeFromArduino, _raw_movetime))
            _raw_movetime = getboard()
            dbg('STOCKFISH movetime raw return (retry)={0!r}'.format(_raw_movetime))
            movetimeFromArduino = _raw_movetime[1:].lower()
        print ("Requested time out setting:")
        print(movetimeFromArduino)
        dbg('STOCKFISH parsed movetimeFromArduino={0!r}'.format(movetimeFromArduino))


        # assume new game
        print ("\n Chess Program \n")
        sendToScreen ('NEW','GAME','','30')
        time.sleep(2)
        sendToScreen ('Please enter','your move:','')
        skill = skillFromArduino
        movetime = movetimeFromArduino #6000
        dbg('STOCKFISH setup complete — exiting setup loop')
        break

dbg('=== STARTUP: calling newgame() ===')
fmove = newgame()
dbg('STARTUP newgame() returned fmove={0!r}'.format(fmove))

while True:

        # Get  message from board
        dbg('=== MAIN LOOP: calling getboard() for next move ===')
        bmessage = getboard()
        print ("Move command received from Arduino")
        print(bmessage)
        dbg('MAIN LOOP bmessage={0!r}'.format(bmessage))
        # Message options   Move, Newgame, level, style
        code = bmessage[0]
        dbg('MAIN LOOP code={0!r}'.format(code))



        # decide which function to call based on first letter of txt
        fmove=fmove
        if code == 'm':
            fmove = bmove(fmove)
        elif code == 'n':
            fmove = newgame()
        #elif code == 'l':
        #    level()
        #elif code == 's':
        #    style()
        else :
            sendtoboard('error at option')
 
