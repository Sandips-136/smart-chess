# How a single chess move works

Let's walk through one move, step by step. This is the easiest way to understand the whole system.

## Scenario: You're playing against the computer. You move a pawn from e2 to e4.

### Step 1 — You pick up the pawn
The magnetic switch under square **e2** opens. The Arduino notices.

### Step 2 — You put the pawn down on e4
The magnetic switch under square **e4** closes. The Arduino now knows: "a piece moved from e2 to e4".

### Step 3 — Arduino tells the Raspberry Pi
The Arduino sends a tiny text message over a USB cable to the Pi. The message looks like this:

```
heypime2e4
```

- `heypi` = "hey Raspberry Pi, I'm talking to you"
- `m` = "this is a move"
- `e2e4` = the move itself

### Step 4 — The Pi checks the move
The Pi runs a Python program called [StartChessGame.py](../RaspberryPiCode/StartChessGame.py). It uses a chess rules library called [ChessBoard.py](../RaspberryPiCode/ChessBoard.py) to check: *"Is e2-e4 a legal move?"*

- If yes → continue.
- If no → tell the Arduino to flash a warning LED.

### Step 5 — The Pi asks Stockfish what to do
Now it's the computer's turn. The Pi sends the full game so far to **Stockfish** (the chess engine) and basically asks: *"What's your best move?"*

Stockfish thinks for a moment and replies with something like `e7e5`.

### Step 6 — The Pi tells the Arduino the computer's move
The Pi sends a message back to the Arduino:

```
heyArduinome7e5
```

The Arduino lights up the LEDs under **e7** and **e5** so you can see where to move the computer's piece for it.

### Step 7 — You move the piece for the computer
You pick up the black pawn on e7 and put it on e5. The switches confirm it. The LEDs turn off.

### Step 8 — The OLED screen updates
The little screen shows whose turn it is now, or "check", or whatever's relevant.

**Now it's your turn again. Loop back to Step 1.**

---

## What about playing online?

Same as above, except instead of asking Stockfish, the Pi:

1. Sends your move to a website called **Adafruit IO** (think of it as a shared notepad on the internet).
2. Waits, checking every 3 seconds, for your opponent to write *their* move on the same notepad.
3. When their move appears, lights up the LEDs just like Stockfish's move.

That's all there is to it.
