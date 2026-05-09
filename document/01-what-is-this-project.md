# What is this project?

This is a **smart chessboard** you can play on with real wooden pieces — but the board is "smart" because it knows where every piece is, lights up squares, and can even play against you by itself.

Think of it like a normal chessboard, but with electronics inside.

## The big idea

You have three ways to play:

1. **Play against the computer** — the board tells you where the computer wants to move by lighting up LEDs.
2. **Play another human in the same room** — the board just keeps score and stops you from making illegal moves.
3. **Play someone over the internet** — your move is sent online; their move comes back and lights up on your board.

That's it. The rest of this document explains how the pieces fit together.

## The hardware (the physical stuff)

- **The wooden chessboard** — has tiny magnetic switches under each square. When you put a piece down or pick one up, the board knows.
- **An Arduino** — a small microcontroller inside the board. It watches the switches and controls the LEDs.
- **A Raspberry Pi** — a small computer (also inside the board). This is the "brain" that runs the chess rules and talks to the internet.
- **A small OLED screen** — shows messages like "Your turn", "Checkmate", etc.
- **LEDs under each square** — light up to show you where to move pieces.

## The software (what makes it work)

- **Stockfish** — a famous free chess engine. This is what plays *against* you when you choose "computer".
- **Python scripts on the Pi** — the main code that ties everything together (this is what's in this repo).
- **Adafruit IO** — a free internet service used to send moves back and forth when playing online.

## Where it came from

This is a DIY project from **www.DIYmachines.co.uk** — meaning someone built and shared the design online and we're using their code as a starting point.
