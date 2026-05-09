# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A DIY "smart chessboard" (based on www.DIYmachines.co.uk). The runtime is a **Raspberry Pi** that:

1. Talks to an **Arduino** over USB serial (the physical board with reed switches / LEDs).
2. Runs **Stockfish** for the PC opponent.
3. Drives a small **SSD1306 I²C OLED** for status text.
4. Optionally relays moves through **Adafruit IO** for remote two-player games.

The Mac in this working directory is just an editing station — nothing actually runs locally. All Python depends on Pi-only hardware libraries (`board`, `digitalio`, `adafruit_ssd1306`, `serial`, the `stockfish` binary on `$PATH`, etc.), so most files cannot be executed or imported on macOS. **Don't run scripts here to "test" them — push to the Pi and run there.**

## Deploying / running

```bash
./deploy/push-to-pi.sh                    # rsync everything (excludes venvs, pyc)
./deploy/push-to-pi.sh --dry-run          # preview
./deploy/push-to-pi.sh <file-or-folder>   # push a single path
./ssh-pi.sh                               # ssh into the Pi
./ssh-pi.sh "<remote command>"            # one-shot remote command
```

Deploy creds are hardcoded in [deploy/config.sh](deploy/config.sh) (`pi@192.168.29.6`, password `pi`). `sshpass` must be installed locally (`brew install sshpass`).

> **Known config drift to be aware of:**
> - `deploy/config.sh` sets `LOCAL_PATH=/Users/sandipsingh/SmartChess/RaspberryPiCode` (capital S), but this repo lives at `/Users/sandipsingh/smart-chess/RaspberryPiCode`. Update `LOCAL_PATH` before pushing, or the script will fail / push the wrong directory.
> - `RaspberryPiCode/chessDIYM.service` runs `python2 -u StartChessGame.py` from `WorkingDirectory=/home/pi/downloads`, but `config.sh` pushes to `/home/pi/SmartChess/RaspberryPiCode`. The service file's paths and the deploy target don't match — confirm with the user which is canonical before "fixing" either.
> - `printToOLED.py` hardcodes `/home/pi/SmartChess/RaspberryPiCode/WorkSans-Medium.ttf`, but `StartChessGameStockfish.py` invokes `printToOLED.py` by bare filename (relative to cwd) while `StartChessGame.py` invokes it by absolute path `/home/pi/SmartChess/RaspberryPiCode/printToOLED.py`. Be careful when changing how scripts are launched.

On the Pi, the game is run by hand or via the systemd unit:

```bash
# manual:
python2 StartChessGame.py            # main entrypoint (selects mode at startup)
python2 StartChessGameStockfish.py   # legacy: stockfish-only
python2 StartChessGameRemote.py      # legacy: adafruit-IO remote-only

# service:
sudo systemctl {start,stop,status} chessDIYM
```

## Python version split (important)

This repo mixes Python 2 and Python 3 deliberately:

- **`ChessBoard.py`, `ChessClient.py`, `Maxchessdemo.py`, `StartChessGame*.py`** — **Python 2.7**. `ChessBoard.py` is the upstream John Eriksson library (GPL) and uses `print` as a statement; the game-loop scripts inherit from that constraint and use `raw_input`, `engine.stdin.write('uci\n')` against a `Popen` opened in `universal_newlines=True`, etc. Don't "modernize" these without porting `ChessBoard.py` first.
- **`printToOLED.py`, `oled_test.py`, `update-online.py`, `receive-online.py`** — **Python 3** (CircuitPython / Blinka requires it). These are launched as separate subprocesses (`subprocess.Popen(["python3", "printToOLED.py", ...])`) precisely so the Py2 game loop and the Py3 hardware layer can coexist.

The two halves communicate exclusively via subprocess pipes (stdin/stdout text), not via imports. When editing this boundary, preserve the line-oriented text protocol.

## Architecture: how a move flows

```
[Arduino board]  <-- USB serial (9600 baud) -->  [Pi: StartChessGame.py]
                                                   |   ^
                                              spawns|   |stdin/stdout pipes
                                                   v   |
                                       [stockfish]  [printToOLED.py (Py3)]  [update-online.py (Py3, Adafruit IO)]
```

**Serial protocol with the Arduino** (see `getboard()` / `sendtoboard()` in `StartChessGame.py`):

- Pi reads lines on `/dev/ttyUSB0` (or `/dev/ttyAMA0` for Pi Zero — see top of each `Start*` script).
- Inbound from board: lines prefixed `heypi…`. The first byte after `heypi` is the opcode:
  - `m<from><to>` — a move, e.g. `heypime2e4`
  - `n…` — new game
  - `heypixshutdown` — shut the Pi down
  - other payloads carry mode/skill/movetime selections during setup
- Outbound to board: lines prefixed `heyArduino…`. Game replies use `m<from><to>-<hint>` for legal moves and `error<reason><move>` (or `e<reason><move>`) for rejects. Mode-setup tokens include `ChooseMode`, `ReadyStockfish`, `ReadyOnlinePlay`.

**Game state**: `maxchess = ChessBoard()` is the single source of truth. Stockfish is fed the entire move list each turn (`position startpos moves <space-separated AN moves>` + `go movetime <ms>`), not FEN — the original author noted FEN was unreliable. Promotion is hardcoded to queen via `setPromotion(QUEEN)`.

**OLED**: every status update spawns a fresh `python3 printToOLED.py -a … -b … -c … -s …` subprocess. There is no persistent display process.

**Adafruit IO remote play**: `update-online.py` is a long-lived Py3 subprocess driven by stdin commands (`send` / `receive`, then a colour, then a move). Two feeds: `whiteplayermove` and `blackplayermove`. The receive loop polls every 3s until the value differs from `previousData`. Credentials are hardcoded — `update-online.py` has placeholder strings (`AddYourKeyHere` / `AddYurUserNameHere`), while `receive-online.py` contains a real-looking key. Treat both as secrets when editing; do not commit real keys.

## Files you will rarely need to touch

- `ChessBoard.py` (~42 KB, vendored upstream library) — full chess rules engine. API summary lives in `HowToUseChessBoard.txt`.
- `img/` — piece sprites for the optional `ChessClient.py` pygame UI (not used by the production board flow).
- `chessenv/`, `smartenv/`, `__pycache__/`, `*.pyc` — gitignored; `chessenv` is the active Pi virtualenv.

## When making changes

- Always double-check whether you are editing a Py2 or Py3 file before adding f-strings, `print()` calls with `end=`, type hints, etc.
- The three `StartChessGame*.py` scripts share large copy-pasted blocks (`bmove`, `getboard`, `sendboard`/`sendtoboard`, `newgame`). If you fix a bug in one, check whether it exists in the others before claiming the fix is done.
- Hardware-touching changes (serial device path, OLED font path, stockfish invocation) usually need to be tested **on the Pi**, not locally. Say so explicitly when you can't verify.
