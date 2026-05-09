# Known issues and quirks

These are things that don't quite line up in the project. Read this before changing config or "fixing" what looks broken — some of these are just quirks of how it was set up.

## 1. The deploy script points to the wrong folder

[deploy/config.sh](../deploy/config.sh) has this line:

```bash
LOCAL_PATH=/Users/sandipsingh/SmartChess/RaspberryPiCode    # Capital S, no dash
```

But your project actually lives at:

```
/Users/sandipsingh/smart-chess/RaspberryPiCode               # lowercase, dash
```

**Fix:** edit `LOCAL_PATH` in `deploy/config.sh` to the correct path before running the push script. Otherwise it will either fail or push the wrong files.

## 2. The systemd service file has a different folder than the deploy script

- [chessDIYM.service](../RaspberryPiCode/chessDIYM.service) expects the code at: `/home/pi/downloads`
- The deploy script pushes the code to: `/home/pi/SmartChess/RaspberryPiCode`

So the service won't actually find the code. **Don't blindly fix one** — figure out which path is the right one and update the other to match. Ask first if you're not sure.

## 3. The OLED font path is hardcoded

[printToOLED.py](../RaspberryPiCode/printToOLED.py) looks for the font here:

```
/home/pi/SmartChess/RaspberryPiCode/WorkSans-Medium.ttf
```

If the project lives anywhere else on the Pi, the OLED will fail. The two scripts that call `printToOLED.py` also disagree on how to call it:

- [StartChessGameStockfish.py](../RaspberryPiCode/StartChessGameStockfish.py) calls it by **filename only** (so it depends on the current folder).
- [StartChessGame.py](../RaspberryPiCode/StartChessGame.py) calls it by **full path** `/home/pi/SmartChess/RaspberryPiCode/printToOLED.py`.

If you change how the program is launched, you may break one of these.

## 4. There's a Windows Stockfish file checked in

[stockfish 7 x64.exe](../RaspberryPiCode/stockfish%207%20x64.exe) is in the repo but is **not used** — Stockfish on the Pi is installed separately as a Linux program. You can ignore this file, or delete it to save space.

## 5. The online-play files have real-looking secrets

- [update-online.py](../RaspberryPiCode/update-online.py) has placeholder text: `AddYourKeyHere`, `AddYurUserNameHere`. (The misspelling is in the original.)
- [receive-online.py](../RaspberryPiCode/receive-online.py) appears to contain a **real** Adafruit IO key.

**Treat both as secret.** Don't paste them into screenshots or commit any new keys to git.

## 6. Two Python virtual environments exist

The folders `chessenv/` and `smartenv/` are both Python virtual environments (toolboxes of installed Python packages). Only `chessenv/` is the one actually used on the Pi. Both are gitignored, so you won't see them in git, but they may exist on your machine.

## 7. The Adafruit IO receive loop polls every 3 seconds

When playing online, the board checks for your opponent's move every 3 seconds. So there's always a small delay — that's normal, not a bug.

## 8. Pawn promotion is hardcoded to Queen

If you push a pawn to the back rank, it always becomes a Queen. There's no option to choose Knight/Bishop/Rook. This is on purpose to keep the hardware simple (no extra menu on the OLED).
