# The files in this project — explained simply

This project has a lot of files. Here's what each important one actually does, in plain English. You can ignore anything not listed here.

## The main entry point

### [StartChessGame.py](../RaspberryPiCode/StartChessGame.py)
**This is the main program.** When you turn the board on, this is what runs. It:
- Asks you what mode you want (vs. computer / vs. human / online).
- Listens for moves coming from the Arduino.
- Checks they're legal.
- Talks to Stockfish or the internet.
- Tells the Arduino what to light up.

If you only read one file, read this one.

## The chess rules

### [ChessBoard.py](../RaspberryPiCode/ChessBoard.py)
A big library (~42 KB) that knows all the chess rules — what a knight can do, when it's checkmate, en passant, castling, etc. **Don't edit this.** It was written by someone else (John Eriksson) and the rest of the code depends on it working exactly the way it does.

### [HowToUseChessBoard.txt](../RaspberryPiCode/HowToUseChessBoard.txt)
A cheat sheet showing how to use the ChessBoard.py library above. Useful reading if you want to understand the chess code.

## The screen (OLED)

### [printToOLED.py](../RaspberryPiCode/printToOLED.py)
A tiny program whose only job is to put text on the small OLED screen. Other programs run it like this:

```
python3 printToOLED.py -a "Your turn" -b "White to move"
```

…and the message appears on the screen.

### [oled_test.py](../RaspberryPiCode/oled_test.py)
A test script. Run it to check the OLED screen is wired up correctly.

## Online play

### [update-online.py](../RaspberryPiCode/update-online.py)
Sends your move to the internet (via Adafruit IO) so a remote opponent can see it.

### [receive-online.py](../RaspberryPiCode/receive-online.py)
Watches the internet for your opponent's move and grabs it when it appears.

> ⚠️ **Both files contain account passwords ("API keys") in plain text.** Don't share screenshots of them.

## Older / leftover versions

These are earlier versions of the main program from before everything was combined into [StartChessGame.py](../RaspberryPiCode/StartChessGame.py). They mostly do the same thing but only support one mode each:

- [StartChessGameStockfish.py](../RaspberryPiCode/StartChessGameStockfish.py) — only plays against the computer.
- [StartChessGameRemote.py](../RaspberryPiCode/StartChessGameRemote.py) — only plays online.

You usually don't need to touch these, but they're kept around as backup.

## Test scripts (safe to ignore)

- [serial_test.py](../RaspberryPiCode/serial_test.py), [test_serial.py](../RaspberryPiCode/test_serial.py), [TestPyhonReceivingScript.py](../RaspberryPiCode/TestPyhonReceivingScript.py) — test the USB connection between Pi and Arduino.
- [Maxchessdemo.py](../RaspberryPiCode/Maxchessdemo.py) — a demo of the chess library.
- [ChessClient.py](../RaspberryPiCode/ChessClient.py) — a graphical chess game using the [img/](../RaspberryPiCode/img/) folder for piece images. Not used by the real board.

## System / config files

- [chessDIYM.service](../RaspberryPiCode/chessDIYM.service) — tells the Pi to start the chess program automatically when it boots up.
- [WorkSans-Medium.ttf](../RaspberryPiCode/WorkSans-Medium.ttf) — the font used on the OLED screen.
- [stockfish 7 x64.exe](../RaspberryPiCode/stockfish%207%20x64.exe) — the Windows version of Stockfish. **The actual one used on the Pi is installed separately**; this `.exe` is only here by accident from when someone tested on Windows.

## Deploy scripts (in this Mac, not the Pi)

- [deploy/push-to-pi.sh](../deploy/push-to-pi.sh) — copies your code from your Mac to the Raspberry Pi over the network.
- [command/ssh-pi.sh](../command/ssh-pi.sh) — opens a remote terminal on the Pi from your Mac.
- [command/start.sh](../command/start.sh) — SSH in and start the chess game.
- [command/reboot-pi.sh](../command/reboot-pi.sh) — reboot the Pi remotely.
