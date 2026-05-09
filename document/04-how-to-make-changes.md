# How to make changes to this project

You edit code on your **Mac**, then push it to the **Raspberry Pi** to actually run it. Nothing in this project will run on the Mac itself — it needs the Pi's hardware (the chess board, OLED, Arduino).

## The normal workflow

```
1. Edit a file on your Mac (in this folder).
2. Push the change to the Pi:    ./deploy/push-to-pi.sh
3. Connect to the Pi:            ./ssh-pi.sh
4. Run the chess program on the Pi to test it.
```

That's the whole loop.

## Useful commands

### From your Mac

| What you want to do | Command |
|---|---|
| Send all your changes to the Pi | `./deploy/push-to-pi.sh` |
| Preview what would be sent (no actual change) | `./deploy/push-to-pi.sh --dry-run` |
| Send just one file | `./deploy/push-to-pi.sh path/to/file.py` |
| Open a terminal on the Pi | `./ssh-pi.sh` |
| Run one command on the Pi | `./ssh-pi.sh "ls"` |

### Once you're on the Pi

| What you want to do | Command |
|---|---|
| Start the chess game manually | `python2 StartChessGame.py` |
| Start it as a background service | `sudo systemctl start chessDIYM` |
| Stop the background service | `sudo systemctl stop chessDIYM` |
| See if the service is running | `sudo systemctl status chessDIYM` |

## ⚠️ Important things to know before editing

### 1. The code uses TWO different versions of Python

This is a quirk you'll bump into a lot:

- **Python 2** is used by: [StartChessGame.py](../RaspberryPiCode/StartChessGame.py), [ChessBoard.py](../RaspberryPiCode/ChessBoard.py), [Maxchessdemo.py](../RaspberryPiCode/Maxchessdemo.py), [ChessClient.py](../RaspberryPiCode/ChessClient.py)
- **Python 3** is used by: [printToOLED.py](../RaspberryPiCode/printToOLED.py), [oled_test.py](../RaspberryPiCode/oled_test.py), [update-online.py](../RaspberryPiCode/update-online.py), [receive-online.py](../RaspberryPiCode/receive-online.py)

**Why?** The chess library was written in Python 2 and never updated. The OLED hardware library only works in Python 3. So they live side by side and talk to each other.

**What this means for you:** before editing a file, look at the top of it. If it uses `print "hello"` (no parentheses) or `raw_input(...)`, it's Python 2. Don't add Python-3-only stuff like f-strings (`f"hello {name}"`) to Python 2 files — it'll crash.

### 2. The same code is copy-pasted in three places

The functions for talking to the chess board (`getboard`, `sendtoboard`, `bmove`, `newgame`) appear in **all three** Start*.py files. If you fix a bug in one, **check the other two** for the same bug.

### 3. There are config mismatches in the project

A previous developer left a few inconsistent paths between files. See [05-known-issues.md](05-known-issues.md) for the full list — read it before you go hunting bugs.

### 4. You can't really "test" things on the Mac

If you change anything that talks to:
- The chess board
- The Arduino
- The OLED screen
- Stockfish

…you have to push to the Pi and run it there. The Mac doesn't have any of those.
