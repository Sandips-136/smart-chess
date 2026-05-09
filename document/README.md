# Smart Chess — Project Documentation

Simple, plain-English docs explaining what this project is and how it works.

## Read in this order

1. **[What is this project?](01-what-is-this-project.md)** — the big picture in 2 minutes.
2. **[How a single move works](02-how-a-move-works.md)** — follow one chess move from start to finish.
3. **[The files explained](03-the-files-explained.md)** — what every important file does.
4. **[How to make changes](04-how-to-make-changes.md)** — the edit-push-test workflow.
5. **[Known issues and quirks](05-known-issues.md)** — read before "fixing" config that looks wrong.

## In one sentence

> This project turns a wooden chessboard with magnets and LEDs into a smart board that can play chess against you (using the Stockfish engine), against another person in the room, or against someone over the internet — all controlled by a Raspberry Pi inside the board.

## The "map" of the system

```
   ┌─────────────────┐         ┌─────────────────┐
   │  Wooden board   │         │   OLED screen   │
   │  + LEDs + reed  │         │  (small text    │
   │     switches    │         │    display)     │
   └────────┬────────┘         └────────▲────────┘
            │                           │
            │ USB cable                 │ "show this text"
            │ (text messages)           │
            ▼                           │
   ┌─────────────────┐         ┌────────┴────────┐
   │     Arduino     │         │  Raspberry Pi   │
   │ (watches the    │◄───────►│ (the brain —    │
   │  switches)      │  USB    │  Python code)   │
   └─────────────────┘         └────────┬────────┘
                                        │
                          ┌─────────────┴────────────┐
                          │                          │
                          ▼                          ▼
                ┌──────────────────┐     ┌──────────────────┐
                │    Stockfish     │     │   Adafruit IO    │
                │  (chess engine,  │     │  (internet — for │
                │   plays vs you)  │     │  online matches) │
                └──────────────────┘     └──────────────────┘
```
