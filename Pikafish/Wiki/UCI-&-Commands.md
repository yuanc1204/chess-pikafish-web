The [Universal Chess Interface](https://backscattering.de/chess/uci/) (UCI) is a standard text-based protocol used to communicate with a xiangqi engine and is the recommended way to do so for typical graphical user interfaces (GUI) or chess tools. Pikafish implements the majority of its options.

Developers can see the default values for the UCI options available in Pikafish by typing `./pikafish uci` in a terminal, but most users should typically use a xiangqi GUI to interact with Pikafish.

## Standard commands

### `quit`

Quit the program as soon as possible.

### `uci`

Tell the engine to use the UCI (universal chess interface).  
This will be sent once, by a GUI, as a first command after the program boots to tell the engine to switch to UCI mode.  
After receiving the `uci` command the engine will identify itself with the `id` command and send the `option` commands to tell the GUI which engine settings the engine supports.  
After that, the engine will send `uciok` to acknowledge the UCI mode.  
If no `uciok` is sent within a certain time period, the engine task will be killed by the GUI.

<details>
  <summary>Example</summary>

  ```
  > uci
    id name Pikafish dev-20240822-nogit
    id author the Pikafish developers (see AUTHORS file)

    option name Debug Log File type string default
    option name NumaPolicy type string default auto
    option name Threads type spin default 1 min 1 max 1024
    option name Hash type spin default 16 min 1 max 33554432
    option name Clear Hash type button
    option name Ponder type check default false
    option name MultiPV type spin default 1 min 1 max 128
    option name Move Overhead type spin default 10 min 0 max 5000
    option name nodestime type spin default 0 min 0 max 10000
    option name UCI_ShowWDL type check default false
    option name EvalFile type string default pikafish.nnue
    uciok
  ```
</details>

### `setoption`

Usage: `setoption name <id> [value <x>]`  

This is sent to the engine when the user wants to change the internal parameters of the engine. For the `button` type no value is needed.  
One string will be sent for each parameter and this will only be sent when the engine is waiting.  

Examples:
```
> setoption name Threads value 6
> setoption name EvalFile value pikafish.nnue
> setoption name UCI_ShowWDL value true
> setoption name Clear Hash
```

List of options:

  * `Debug Log File` `type string default`  
    Write all communication to and from the engine into a text file.

  * `NumaPolicy` `type string default auto`
    Bind threads to ensure execution on a specific NUMA node. 
    Improves performance on systems with multiple CPUs or CPUs with multiple NUMA domains. 
    The following values can be used:
       * `system` - gathers NUMA node information from the system (including affinities preset by the user or the GUI), for each thread binds it to a single NUMA node
       * `none` - assumes there is 1 NUMA node, never binds threads
       * `auto` - this is the default value, automatically selects `system` or `none` depending on the number of set threads and available NUMA nodes. Will only select `system` when the number of threads reaches a system-dependent threshold.
       * `hardware` - gathers NUMA node information for the underlying hardware (disregards and overrides affinities preset by the user or the GUI), for each thread binds it to a single NUMA node
       * `[[custom]]` - specify precisely the available CPUs per numa domain. ':' separates numa nodes; ',' separates cpu indices; supports "first-last" range syntax for cpu indices, for example `0-15,32-47:16-31,48-63`

  * `Threads` `type spin default 1 min 1 max 1024`  
    The number of CPU threads used for searching a position. For best performance, set this equal to the number of CPU cores available.

  * `Hash` `type spin default 16 min 1 max 33554432`  
    The size of the hash table in MB. It is recommended to set Hash after setting Threads.

  * `Clear Hash` `type button`  
    Clear the hash table.

  * `Ponder` `type check default false`  
    Let Pikafish ponder its next move while the opponent is thinking.

  * `MultiPV` `type spin default 1 min 1 max 500`  
    Output the N best lines (principal variations, PVs) when searching.
    Leave at 1 for the best performance.

  * `Move Overhead` `type spin default 10 min 0 max 5000`  
    Assume a time delay of x ms due to network and GUI overheads. This is useful to avoid losses on time in those cases.

  * `nodestime` `type spin default 0 min 0 max 10000`  
    Tells the engine to use nodes searched instead of wall time to account for elapsed time. Useful for engine testing. When this option is set, the engine is only limited by the total amount of nodes searched per game; this limit is calculated once per game. The initial time control values in milliseconds (time `time` and increment per move `inc`) are used as input values to calculate the total number of nodes per game (`totalnodes`). The increment per move `inc` is used as if it was just one move per game. The formula is `totalnodes = (time + inc * 1) * nodestime`. Suppose you specified `nodestime = 600`, and the time control per game is 300 seconds plus 3 seconds increment per move ("300+3s"), or 300000 milliseconds plus 3000 milliseconds increment per move. In that case, the maximum total number of nodes searched per game by the engine is `totalnodes = (300000 + 3000 * 1) * 1000 = 181800000` (one hundred eighty-one million, eight hundred thousand) nodes, regardless of how much wall time it will actually take.

  * `UCI_ShowWDL` `type check default false`  
    If enabled, show approximate WDL statistics as part of the engine output.
    These WDL numbers model expected game outcomes for a given evaluation and game ply for engine self-play at fishtest LTC conditions (60+0.6s per game).

  * `EvalFile` `type string default pikafish.nnue`  
    The name of the file of the NNUE evaluation parameters. Depending on the GUI the filename might have to include the full path to the folder/directory that contains the file. Other locations, such as the directory that contains the binary and the working directory, are also searched.

### `position`

Usage: `position [fen <fenstring> | startpos ]  moves <move1> .... <movei>`

Set up the position described in `fenstring`.  
> [!NOTE]
> If this position is from a different game than the last position sent to the engine, the GUI should have sent a `ucinewgame` in between.

Examples:
```
> position startpos
> position fen rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1
> position fen rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1 moves h2e2 h9g7 h0g2 g6g5
```

### `ucinewgame`

This is sent to the engine when the next search (started with `position` and `go`) will be from a different game. This can be a new game the engine should play or a new game it should analyze but also the next position from a test suite with positions only.  
If the GUI hasn't sent a `ucinewgame` before the first `position` command, the engine won't expect any further `ucinewgame` commands as the GUI is probably not supporting the `ucinewgame` command.  
So the engine will not rely on this command even though all new GUIs should support it.  
As the engine's reaction to `ucinewgame` can take some time the GUI should always send `isready` after `ucinewgame` to wait for the engine to finish its operation. The engine will respond with `readyok`.

_This clears the hash and any information which was collected during the previous search._

<details>
  <summary>Example</summary>

  ```
  > ucinewgame
  > isready
  readyok
  > position startpos
  > go depth 1
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 8 nodes 74 nps 37000 hashfull 0 tbhits 0 time 2 pv b2e2
  bestmove b2e2
  > ucinewgame
  > isready
  readyok
  > position fen rnbakabr1/9/1c4nc1/p1p1p2Rp/6p2/9/P1P1P1P1P/1C2C1N2/9/RNBAKAB2 b - - 7 4
  ```
</details>

### `isready`

This is used to synchronize the engine with the GUI.  
When the GUI has sent a command or multiple commands that can take some time to complete, this command can be used to wait for the engine to be ready again or to ping the engine to find out if it is still alive.  
e.g. this should be sent after setting the path to the tablebases as this can take some time.  
This command is also required once, before the engine is asked to do any searching, to wait for the engine to finish initializing.  
This command will always be answered with `readyok` and can be sent also when the engine is calculating in which case the engine will also immediately answer with `readyok` without stopping the search.

Example:
```
> isready
readyok
```

### `go`

Start calculating on the current position set up with the `position` command.  
There are a number of parameters that can follow this command and all will be sent in the same string.  
If no parameter is sent, then `go depth 245` will be executed.

<details>
  <summary>Example: go infinite</summary>

  ```
  > position startpos
  > go infinite
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 8 nodes 74 nps 37000 hashfull 0 tbhits 0 time 2 pv b2e2
  info depth 2 seldepth 2 multipv 1 score cp 20 nodes 191 nps 95500 hashfull 0 tbhits 0 time 2 pv h2e2
  info depth 3 seldepth 2 multipv 1 score cp 21 nodes 267 nps 89000 hashfull 0 tbhits 0 time 3 pv b2e2
  info depth 4 seldepth 2 multipv 1 score cp 65 nodes 342 nps 114000 hashfull 0 tbhits 0 time 3 pv b2e2
  info depth 5 seldepth 2 multipv 1 score cp 320 nodes 389 nps 129666 hashfull 0 tbhits 0 time 3 pv b2e2
  info depth 6 seldepth 6 multipv 1 score cp 30 nodes 925 nps 231250 hashfull 0 tbhits 0 time 4 pv h2e2 h7e7 h0g2
  info depth 7 seldepth 5 multipv 1 score cp 35 nodes 1636 nps 327200 hashfull 0 tbhits 0 time 5 pv b2e2 b7e7 b0c2
  info depth 8 seldepth 8 multipv 1 score cp 34 nodes 2972 nps 424571 hashfull 1 tbhits 0 time 7 pv b2e2 h7e7 h0g2 b9c7 b0c2 h9g7
  info depth 9 seldepth 9 multipv 1 score cp 33 nodes 5284 nps 587111 hashfull 3 tbhits 0 time 9 pv h2e2 b7e7 h0g2 b9c7 i0h0 h9g7 b0c2
  > stop
  info depth 10 seldepth 10 multipv 1 score cp 22 nodes 12888 nps 758117 hashfull 7 tbhits 0 time 17 pv h2e2 h9g7 h0g2 i9h9 c3c4 b7e7 i0h0 b9c7
  bestmove b2e2 ponder h9g7
  ```
</details>

<details>
  <summary>Example: go depth</summary>

  ```
  > position startpos
  > go depth 25
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 8 nodes 74 nps 37000 hashfull 0 tbhits 0 time 2 pv b2e2
  info depth 2 seldepth 2 multipv 1 score cp 20 nodes 191 nps 95500 hashfull 0 tbhits 0 time 2 pv h2e2
  info depth 3 seldepth 2 multipv 1 score cp 21 nodes 267 nps 89000 hashfull 0 tbhits 0 time 3 pv b2e2
  info depth 4 seldepth 2 multipv 1 score cp 65 nodes 342 nps 114000 hashfull 0 tbhits 0 time 3 pv b2e2
  info depth 5 seldepth 2 multipv 1 score cp 320 nodes 389 nps 129666 hashfull 0 tbhits 0 time 3 pv b2e2
  info depth 6 seldepth 6 multipv 1 score cp 30 nodes 925 nps 231250 hashfull 0 tbhits 0 time 4 pv h2e2 h7e7 h0g2
  info depth 7 seldepth 5 multipv 1 score cp 35 nodes 1636 nps 327200 hashfull 0 tbhits 0 time 5 pv b2e2 b7e7 b0c2
  info depth 8 seldepth 8 multipv 1 score cp 34 nodes 2972 nps 424571 hashfull 1 tbhits 0 time 7 pv b2e2 h7e7 h0g2 b9c7 b0c2 h9g7
  info depth 9 seldepth 9 multipv 1 score cp 33 nodes 5284 nps 587111 hashfull 3 tbhits 0 time 9 pv h2e2 b7e7 h0g2 b9c7 i0h0 h9g7 b0c2
  info depth 10 seldepth 10 multipv 1 score cp 22 nodes 12888 nps 805500 hashfull 7 tbhits 0 time 16 pv h2e2 h9g7 h0g2 i9h9 c3c4 b7e7 i0h0 b9c7
  info depth 11 seldepth 14 multipv 1 score cp 29 nodes 23685 nps 845892 hashfull 13 tbhits 0 time 28 pv h2e2 h9g7 h0g2 i9h9 i0h0 h7h3 g3g4 h3g3 h0h9 g7h9 e2e6
  info depth 12 seldepth 16 multipv 1 score cp 24 nodes 40104 nps 891200 hashfull 21 tbhits 0 time 45 pv h2e2 h9g7 h0g2 i9h9 i0h0 g6g5 h0h6 c9e7 b0c2 h7i7 h6g6 h9h3 b2a2 h3g3
  info depth 13 seldepth 15 multipv 1 score cp 26 nodes 51293 nps 884362 hashfull 25 tbhits 0 time 58 pv h2e2 h9g7 h0g2 b9c7 i0h0 i9h9 g3g4 c6c5 b0a2 a6a5 h0h6 c9e7 b2d2
  info depth 14 seldepth 19 multipv 1 score cp 28 nodes 63360 nps 880000 hashfull 32 tbhits 0 time 72 pv h2e2 h9g7 h0g2 b9c7 i0h0 i9h9 g3g4 c6c5 b0a2 h7h3 g2f4 b7b3 g4g5 h3g3 h0h9 g7h9
  info depth 15 seldepth 17 multipv 1 score cp 28 nodes 78800 nps 875555 hashfull 38 tbhits 0 time 90 pv h2e2 h9g7 h0g2 i9h9 i0h0 b9c7 g3g4 c6c5 b0a2 h7h3 g2f4 b7b3 g4g5 h3g3 h0h9 g7h9
  info depth 16 seldepth 20 multipv 1 score cp 24 nodes 127092 nps 901361 hashfull 63 tbhits 0 time 141 pv b2e2 b7e7 b0c2 b9c7 a0b0 a9a8 h0g2 a8f8 c3c4 f8f3
  info depth 17 seldepth 16 multipv 1 score cp 43 nodes 159456 nps 911177 hashfull 79 tbhits 0 time 175 pv b2e2 b9c7 b0c2 a9b9 a0b0 c6c5 b0b6 g6g5 b6c6 h9g7 h0g2 b7b2 h2i2
  info depth 18 seldepth 23 multipv 1 score cp 29 nodes 323086 nps 939203 hashfull 151 tbhits 0 time 344 pv b2e2 b9c7 b0c2 a9b9 a0b0 c6c5 g3g4 g9e7 h0g2 h7h3 c3c4 c5c4 b0b6
  info depth 19 seldepth 23 multipv 1 score cp 19 nodes 487252 nps 957273 hashfull 226 tbhits 0 time 509 pv b2e2 b7e7 b0c2 b9c7 a0b0 a9a8 h2i2 h7g7 h0g2 h9i7 i0h0 a8f8 c3c4 i9h9 h0h9 i7h9 b0b6 f8f3 b6c6 f3g3 c2e1
  info depth 20 seldepth 25 multipv 1 score cp 27 nodes 790761 nps 958498 hashfull 363 tbhits 0 time 825 pv b2e2 b9c7 b0c2 a9b9 a0b0 h9g7 g3g4 c6c5 h0g2 i9i8 b0b6 b7a7 b6c6 b9b4 h2i2 b4g4
  info depth 21 seldepth 24 multipv 1 score cp 23 nodes 910539 nps 961498 hashfull 405 tbhits 0 time 947 pv b2e2 b9c7 b0c2 a9b9 a0b0 h9g7 g3g4 c6c5 h0g2 b7b3 h2h4 g9e7 c3c4 g6g5 g4g5 c5c4 g5g6 c4c3 g6g7 i9g9 g7h7 g9g2
  info depth 22 seldepth 28 multipv 1 score cp 19 nodes 1348750 nps 965461 hashfull 553 tbhits 0 time 1397 pv b2e2 b9c7 b0c2 a9b9 a0b0 c6c5 h0g2 b7b3 g3g4 g9e7 c2a1 b3b4 h2h4 b4h4 b0b9 c7b9
  info depth 23 seldepth 26 multipv 1 score cp 26 nodes 1641335 nps 960968 hashfull 639 tbhits 0 time 1708 pv b2e2 b9c7 b0c2 a9b9 a0b0 h9g7 g3g4 c6c5 h0g2 i9i8 h2i2 h7h3 i0h0 h3g3 b0b4 b7a7 b4f4 g3c3 c0a2 c9e7
  info depth 24 seldepth 28 multipv 1 score cp 27 nodes 2126771 nps 954993 hashfull 756 tbhits 0 time 2227 pv b2e2 b9c7 b0c2 a9b9 a0b0 h9g7 g3g4 c6c5 b0b6 c7d5 b6b4 c5c4 b4c4 b7d7 h0g2 h7h5 h2i2 g9e7 i0h0
  info depth 25 seldepth 26 multipv 1 score cp 20 nodes 2694626 nps 959283 hashfull 841 tbhits 0 time 2809 pv b2e2 b9c7 b0c2 a9b9 a0b0 h9g7 g3g4 c6c5 h0g2 i9i8 h2i2 h7h3 i0h0 h3g3 b0b4 i8f8 e3e4 c9e7 c3c4 c5c4 b4c4 c7d5
  bestmove b2e2 ponder b9c7
  ```
</details>

<details>
  <summary>Example: go mate</summary>

  ```
  > position fen 3k5/9/4P4/9/9/9/9/9/9/4K4 w
  > go mate 1
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 158 nodes 5 nps 2500 hashfull 0 tbhits 0 time 2 pv e7d7
  info depth 2 seldepth 2 multipv 1 score cp 158 nodes 10 nps 5000 hashfull 0 tbhits 0 time 2 pv e7d7
  info depth 3 seldepth 2 multipv 1 score cp 158 nodes 21 nps 10500 hashfull 0 tbhits 0 time 2 pv e7d7
  info depth 4 seldepth 2 multipv 1 score cp 158 nodes 28 nps 9333 hashfull 0 tbhits 0 time 3 pv e7d7
  info depth 5 seldepth 2 multipv 1 score mate 1 nodes 34 nps 11333 hashfull 0 tbhits 0 time 3 pv e7d7
  bestmove e7d7
  ```
</details>

<details>
  <summary>Example: MultiPV</summary>

  ```
  > setoption name MultiPV value 2
  > position startpos
  > go depth 5
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 20 nodes 101 nps 50500 hashfull 0 tbhits 0 time 2 pv b2e2
  info depth 1 seldepth 1 multipv 2 score cp 8 nodes 101 nps 50500 hashfull 0 tbhits 0 time 2 pv h2e2
  info depth 2 seldepth 2 multipv 1 score cp 20 nodes 199 nps 99500 hashfull 0 tbhits 0 time 2 pv b2e2 b9c7
  info depth 2 seldepth 2 multipv 2 score cp 17 nodes 199 nps 99500 hashfull 0 tbhits 0 time 2 pv h2e2 h9g7
  info depth 3 seldepth 3 multipv 1 score cp 20 nodes 321 nps 160500 hashfull 0 tbhits 0 time 2 pv b2e2 b9c7 b0c2
  info depth 3 seldepth 3 multipv 2 score cp 17 nodes 321 nps 160500 hashfull 0 tbhits 0 time 2 pv h2e2 h9g7 h0g2
  info depth 4 seldepth 4 multipv 1 score cp 20 nodes 464 nps 154666 hashfull 0 tbhits 0 time 3 pv b2e2 b9c7 b0c2 a9b9
  info depth 4 seldepth 4 multipv 2 score cp 17 nodes 464 nps 154666 hashfull 0 tbhits 0 time 3 pv h2e2 h9g7 h0g2 i9h9
  info depth 5 seldepth 5 multipv 1 score cp 20 nodes 623 nps 207666 hashfull 0 tbhits 0 time 3 pv b2e2 b9c7 b0c2 a9b9 a0b0
  info depth 5 seldepth 5 multipv 2 score cp 17 nodes 623 nps 207666 hashfull 0 tbhits 0 time 3 pv h2e2 h9g7 h0g2 i9h9 i0h0
  bestmove b2e2 ponder b9c7
  ```
</details>

<details>
  <summary>Example: UCI_ShowWDL</summary>

  ```
  > setoption name UCI_ShowWDL value true
  > position startpos
  > go depth 5
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 8 wdl 36 951 13 nodes 74 nps 74000 hashfull 0 tbhits 0 time 1 pv b2e2
  info depth 2 seldepth 2 multipv 1 score cp 20 wdl 66 927 7 nodes 191 nps 95500 hashfull 0 tbhits 0 time 2 pv h2e2
  info depth 3 seldepth 2 multipv 1 score cp 21 wdl 67 926 7 nodes 267 nps 133500 hashfull 0 tbhits 0 time 2 pv b2e2
  info depth 4 seldepth 2 multipv 1 score cp 65 wdl 187 811 2 nodes 342 nps 171000 hashfull 0 tbhits 0 time 2 pv b2e2
  info depth 5 seldepth 2 multipv 1 score cp 320 wdl 726 274 0 nodes 389 nps 129666 hashfull 0 tbhits 0 time 3 pv b2e2
  bestmove b2e2
  ```
</details>

Parameters:

  * `searchmoves <move1> .... <movei>`  
    Restrict search to these moves only.  
    Example: After `position startpos` and `go infinite searchmoves h2e2 h0g2` the engine will only search the two moves h2e2 and h0g2 in the initial position.

  * `ponder`  
    Start searching in pondering mode. It won't exit the search in ponder mode, even if it's mate!  
    This means that the last move sent in in the position string is the ponder move.  
    The engine can do what it wants to do, but after a `ponderhit` command it will execute the suggested move to ponder on.  
    This means that the ponder move sent by the GUI can be interpreted as a recommendation about which move to ponder.  
    However, if the engine decides to ponder on a different move, it won't display any mainlines as they are likely to be misinterpreted by the GUI because the GUI expects the engine to ponder on the suggested move.

  * `wtime <x>`  
    White has x ms left on the clock.

  * `btime <x>`  
    Black has x ms left on the clock.

  * `winc <x>`  
    White increment per move in ms if x > 0.

  * `binc <x>`  
    Black increment per move in ms if x > 0.

  * `movestogo <x>`  
    There are x moves to the next time control  
    _Note: this will only be sent if x > 0, if you don't get this and get the wtime and btime it's sudden death._

  * `depth <x>`  
    Search x plies only.

  * `nodes <x>`  
    Search x nodes only.

  * `mate <x>`  
    Search for a mate in x moves.

  * `movetime <x>`  
    Search exactly x ms.

  * `infinite`  
    Search until the `stop` command. Stockfish won't exit the search without being told so in this mode!

  * `perft <x>`  
    A debugging function to walk the move generation tree of strictly legal moves to count all the leaf nodes of a certain depth.

### `stop`

Stop calculating as soon as possible

<details>
  <summary>Example</summary>

  ```
  > position startpos
  > go infinite
  info string NNUE evaluation using nn-ad9b42354671.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 18 nodes 20 nps 4000 hashfull 0 tbhits 0 time 5 pv e2e4
  info depth 2 seldepth 2 multipv 1 score cp 46 nodes 66 nps 11000 hashfull 0 tbhits 0 time 6 pv d2d4
  info depth 3 seldepth 2 multipv 1 score cp 51 nodes 120 nps 20000 hashfull 0 tbhits 0 time 6 pv e2e4
  info depth 4 seldepth 2 multipv 1 score cp 58 nodes 144 nps 18000 hashfull 0 tbhits 0 time 8 pv d2d4
  info depth 5 seldepth 2 multipv 1 score cp 58 nodes 174 nps 15818 hashfull 0 tbhits 0 time 11 pv d2d4 a7a6
  info depth 6 seldepth 7 multipv 1 score cp 34 nodes 1303 nps 81437 hashfull 0 tbhits 0 time 16 pv e2e4 c7c5 g1f3 b8c6 c2c3
  info depth 7 seldepth 6 multipv 1 score cp 29 nodes 3126 nps 120230 hashfull 1 tbhits 0 time 26 pv d2d4 g8f6 e2e3 d7d5 c2c4 d5c4
  info depth 8 seldepth 7 multipv 1 score cp 26 nodes 5791 nps 152394 hashfull 4 tbhits 0 time 38 pv g1f3 g8f6 d2d4 d7d5 e2e3
  info depth 9 seldepth 9 multipv 1 score cp 31 nodes 8541 nps 174306 hashfull 5 tbhits 0 time 49 pv g1f3 c7c5 e2e4 e7e6 d2d4 c5d4 f3d4
  info depth 10 seldepth 13 multipv 1 score cp 25 nodes 20978 nps 209780 hashfull 10 tbhits 0 time 100 pv e2e4 c7c5 g1f3 b8c6 f1c4 e7e6 e1g1 g8f6
  info depth 11 seldepth 13 multipv 1 score cp 32 nodes 29040 nps 220000 hashfull 14 tbhits 0 time 132 pv e2e4 c7c5 c2c3 g8f6 e4e5 f6d5 d2d4
  info depth 12 seldepth 14 multipv 1 score cp 38 nodes 41207 nps 242394 hashfull 18 tbhits 0 time 170 pv e2e4 e7e6 d2d4 d7d5 b1c3 d5e4 c3e4
  > stop
  info depth 13 seldepth 14 multipv 1 score cp 38 nodes 45531 nps 247451 hashfull 21 tbhits 0 time 184 pv e2e4 e7e6 d2d4 d7d5 b1c3 d5e4 c3e4
  bestmove e2e4 ponder e7e6
  ```
</details>

### `ponderhit`

The user has played the expected move.  
This will be sent if the engine was told to ponder on the same move the user has played.  
The engine will continue searching but switch from pondering to normal search.

<details>
  <summary>Example</summary>

  ```
  > setoption name Ponder value true
  > position startpos moves h2e2
  > go movetime 1000
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp -9 nodes 124 nps 62000 hashfull 0 tbhits 0 time 2 pv h9g7
  info depth 2 seldepth 2 multipv 1 score cp 0 nodes 203 nps 67666 hashfull 0 tbhits 0 time 3 pv b9c7
  info depth 3 seldepth 2 multipv 1 score cp 0 nodes 253 nps 84333 hashfull 0 tbhits 0 time 3 pv b9c7
  info depth 4 seldepth 2 multipv 1 score cp 0 nodes 298 nps 99333 hashfull 0 tbhits 0 time 3 pv b9c7
  info depth 5 seldepth 2 multipv 1 score cp 11 nodes 346 nps 115333 hashfull 0 tbhits 0 time 3 pv b9c7
  info depth 6 seldepth 4 multipv 1 score cp -9 nodes 1060 nps 265000 hashfull 0 tbhits 0 time 4 pv h9g7 h0g2 g6g5 i0h0
  info depth 7 seldepth 7 multipv 1 score cp -23 nodes 2652 nps 442000 hashfull 1 tbhits 0 time 6 pv h9g7 h0g2 g6g5 c3c4
  info depth 8 seldepth 7 multipv 1 score cp -32 nodes 4771 nps 596375 hashfull 2 tbhits 0 time 8 pv h9g7 h0g2 g6g5 i0h0 i9h9 b0c2
  info depth 9 seldepth 8 multipv 1 score cp -23 nodes 7079 nps 643545 hashfull 3 tbhits 0 time 11 pv h9g7 h0g2 i9h9 i0h0 c6c5 b0c2 b9c7
  info depth 10 seldepth 11 multipv 1 score cp -23 nodes 16758 nps 761727 hashfull 9 tbhits 0 time 22 pv b7e7 h0g2 b9c7 i0h0 h9g7 b2c2 i9h9 h0h6
  info depth 11 seldepth 14 multipv 1 score cp -25 nodes 30146 nps 814756 hashfull 13 tbhits 0 time 37 pv h9g7 h0g2 i9h9 i0h0 h7h3 g3g4 b7e7 b2b6 b9c7 b0c2
  info depth 12 seldepth 12 multipv 1 score cp -30 nodes 37352 nps 848909 hashfull 18 tbhits 0 time 44 pv h9g7 h0g2 i9h9 i0h0 h7h3 g3g4 b7e7 b0c2 b9c7 a0b0 c6c5
  info depth 13 seldepth 13 multipv 1 score cp -23 nodes 42708 nps 837411 hashfull 19 tbhits 0 time 51 pv h9g7 h0g2 i9h9 i0h0 g6g5 h0h4 b9c7 b0c2 h7i7 h4h9 g7h9 c3c4
  info depth 14 seldepth 14 multipv 1 score cp -21 nodes 51232 nps 868338 hashfull 22 tbhits 0 time 59 pv h9g7 h0g2 i9h9 i0h0 g6g5 c3c4 c9e7 h0h4 b9c7 g3g4 g5g4 h4g4
  info depth 15 seldepth 15 multipv 1 score cp -26 nodes 79299 nps 881100 hashfull 38 tbhits 0 time 90 pv h9g7 h0g2 i9h9 i0h0 g6g5 c3c4 c9e7 b0c2 h7h3 b2a2 b7b3 a0b0 b3c3
  info depth 16 seldepth 18 multipv 1 score cp -23 nodes 88252 nps 882520 hashfull 41 tbhits 0 time 100 pv h9g7 h0g2 i9h9 i0h0 g6g5 h0h4 c9e7 b0c2 h7i7 h4h9 g7h9 b2a2 b9c7 a0b0 a9b9
  info depth 17 seldepth 18 multipv 1 score cp -23 nodes 106522 nps 895142 hashfull 44 tbhits 0 time 119 pv h9g7 h0g2 i9h9 i0h0 g6g5 c3c4 b7b3 g3g4 g5g4 h0h6 g7f5 h6h5 f5d4
  info depth 18 seldepth 18 multipv 1 score cp -18 nodes 139004 nps 902623 hashfull 60 tbhits 0 time 154 pv h9g7 h0g2 i9h9 i0h0 g6g5 b0c2 h7h3 b2a2 b7e7 a0b0 b9c7 b0b6 a9b9 b6c6
  info depth 19 seldepth 21 multipv 1 score cp -24 nodes 286049 nps 931755 hashfull 122 tbhits 0 time 307 pv h9g7 h0g2 i9h9 i0h0 g6g5 h0h6 c6c5 b2c2 b9c7 h6g6 b7a7 b0a2 a9b9 a0b0 b9b0 a2b0 h7i7 e3e4
  info depth 20 seldepth 27 multipv 1 score cp -21 nodes 414461 nps 952783 hashfull 173 tbhits 0 time 435 pv h9g7 h0g2 i9h9 i0h0 g6g5 h0h6 c6c5 h6g6 b9c7 b2c2 a9b9 b0a2 h7h8 g6g5 c9a7 a0b0 h8g8
  info depth 21 seldepth 26 multipv 1 score cp -21 nodes 530263 nps 948592 hashfull 226 tbhits 0 time 559 pv h9g7 h0g2 i9h9 i0h0 g6g5 h0h6 c6c5 b2c2 c9e7 b0a2 b9d8 h6h4 d9e8 a0b0 h7i7 h4d4 b7d7 c3c4 c5c4
  info depth 22 seldepth 26 multipv 1 score cp -25 lowerbound nodes 969625 nps 968656 hashfull 385 tbhits 0 time 1001 pv h9g7
  bestmove h9g7 ponder h0g2
  ```
  Pikafish plays `1. ... h9g7` and expects `2. h0g2`
  ```
  > position startpos moves h2e2 h9g7 h0g2
  > go ponder movetime 1000
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp -8 nodes 47 nps 23500 hashfull 0 tbhits 0 time 2 pv i9h9
  info depth 2 seldepth 2 multipv 1 score cp -12 nodes 102 nps 51000 hashfull 0 tbhits 0 time 2 pv i9h9 b0c2
  info depth 3 seldepth 3 multipv 1 score cp -15 nodes 151 nps 75500 hashfull 0 tbhits 0 time 2 pv i9h9 b0c2 g6g5
  info depth 4 seldepth 4 multipv 1 score cp -23 nodes 321 nps 107000 hashfull 0 tbhits 0 time 3 pv i9h9 g3g4 c6c5 i0h0
  info depth 5 seldepth 5 multipv 1 score cp -24 nodes 415 nps 138333 hashfull 0 tbhits 0 time 3 pv i9h9 g3g4 b9c7 c3c4 h7i7 b0c2
  info depth 6 seldepth 6 multipv 1 score cp -24 nodes 546 nps 136500 hashfull 0 tbhits 0 time 4 pv i9h9 g3g4 b9c7 c3c4 h7i7
  info depth 7 seldepth 8 multipv 1 score cp -15 nodes 855 nps 213750 hashfull 0 tbhits 0 time 4 pv i9h9 g3g4 c6c5 i0h0 b9c7 b0a2
  info depth 8 seldepth 9 multipv 1 score cp -17 nodes 1194 nps 238800 hashfull 0 tbhits 0 time 5 pv i9h9 g3g4 c6c5 i0h0 b9c7 b0a2 a9a8 a0a1 a8d8 a1c1
  info depth 9 seldepth 9 multipv 1 score cp -17 nodes 1531 nps 306200 hashfull 0 tbhits 0 time 5 pv i9h9 g3g4 c6c5 i0h0 b9c7 b0a2 a9a8 a0a1 a8d8 a1c1
  info depth 10 seldepth 10 multipv 1 score cp -17 nodes 2043 nps 340500 hashfull 0 tbhits 0 time 6 pv i9h9 g3g4 c6c5 i0h0 b9c7 b0a2 a9a8 a0a1 a8d8 a1c1
  info depth 11 seldepth 12 multipv 1 score cp -16 nodes 3037 nps 433857 hashfull 0 tbhits 0 time 7 pv i9h9 g3g4 c6c5 b0a2 b9c7 i0h0 h7h3 g2f4 b7b3 e2e1 g9e7 a0a1
  info depth 12 seldepth 15 multipv 1 score cp -15 nodes 11609 nps 773933 hashfull 3 tbhits 0 time 15 pv i9h9 b2d2 b9c7 b0c2 a9b9 a0b0 c6c5 i0h0 g6g5 h0h6 g9e7
  info depth 13 seldepth 17 multipv 1 score cp -16 nodes 20497 nps 788346 hashfull 4 tbhits 0 time 26 pv i9h9 b2d2 b9c7 b0c2 a9b9 a0b0 c6c5 i0h0 g6g5 h0h4 h7i7 h4h9 g7h9
  info depth 14 seldepth 18 multipv 1 score cp -15 nodes 30936 nps 736571 hashfull 8 tbhits 0 time 42 pv i9h9 b2d2 b9c7 b0c2 a9b9 a0b0 b7b3 c3c4 g6g5 c2d4 b9b4
  info depth 15 seldepth 12 multipv 1 score cp -15 nodes 33116 nps 752636 hashfull 9 tbhits 0 time 44 pv i9h9 b2d2 b9c7 b0c2 a9b9 a0b0 b7b3 c3c4 g6g5 c2d4 b9b4
  info depth 16 seldepth 20 multipv 1 score cp -16 nodes 77547 nps 842902 hashfull 34 tbhits 0 time 92 pv i9h9 g3g4 h7i7 b0c2 c6c5 b2a2 b9c7 a0b0 a9b9 b0b6 b7a7 b6b9 c7b9 a2a6 b9c7 a6g6
  info depth 17 seldepth 25 multipv 1 score cp -40 nodes 319127 nps 961225 hashfull 156 tbhits 0 time 332 pv i9h9 i0h0 b9c7 c3c4 g6g5 h0h6 b7b6 b0c2 c6c5 h6h4 c5c4 h4c4 b6b8 c2d4 a9a7 d4c6 b8c8 a0a1 a7b7 c6b4 b7a7 c4h4 c8c0 d0e1
  info depth 18 seldepth 25 multipv 1 score cp -26 nodes 414450 nps 959375 hashfull 197 tbhits 0 time 432 pv i9h9 i0h0 b9c7 c3c4 g6g5 b0c2 h7h3 b2b4 c9e7 g3g4 c6c5 c4c5 g5g4 c5c6 c7e8 g2i1 h3h6 c2d4 g4g3 e2e6
  info depth 19 seldepth 24 multipv 1 score cp -22 nodes 525372 nps 956961 hashfull 245 tbhits 0 time 549 pv i9h9 i0h0 b9c7 c3c4 g6g5 h0h6 g7f5 b0c2 c9e7 h6h4 b7b3 h4f4 b3g3 g0i2 f5g7 a0b0 a9b9 b2b7
  info depth 20 seldepth 24 multipv 1 score cp -23 nodes 709594 nps 964122 hashfull 315 tbhits 0 time 736 pv i9h9 i0h0 b9c7 c3c4 g6g5 h0h6 g7f5 b0c2 g9e7 a0a1 a9a8 a1f1 f5g3 f1f7
  info depth 21 seldepth 25 multipv 1 score cp -19 nodes 835844 nps 970782 hashfull 369 tbhits 0 time 861 pv i9h9 i0h0 b9c7 c3c4 g6g5 h0h6 g7f5 b0c2 g9e7 h6h4 b7b3 e3e4 f5g3 g2e3 h7h5 e4e5 e6e5 e3d5 b3i3 d5c7
  info depth 22 seldepth 34 multipv 1 score cp -24 nodes 1487777 nps 985935 hashfull 588 tbhits 0 time 1509 pv i9h9 i0h0 b9c7 c3c4 g6g5 h0h6 g7f5 b0c2 g9e7 h6h4 b7b3 e3e4 f5g3 g2e3 h7h5 e4e5 e6e5 a0a1 b3c3 e3d5 a9b9 d5c3 b9b3
  ```
  The opponent plays the expected `2. h0g2`
  ```
  > ponderhit
  info depth 23 seldepth 27 multipv 1 score cp -23 nodes 1632161 nps 988589 hashfull 624 tbhits 0 time 1651 pv i9h9 i0h0 b9c7 c3c4 g6g5 h0h6 g7f5 b0c2 g9e7 h6h4 b7b3 e3e4 f5g3 a3a4 b3c3 e4e5 e6e5 a0a3 c3c0 d0e1
  bestmove i9h9 ponder i0h0
  ```
  Pikafish plays `2. ... i9h9` and expects `3. i0h0`
  ```
  > position startpos moves h2e2 h9g7 h0g2 i9h9 i0h0
  > go ponder movetime 1000
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp -31 nodes 54 nps 27000 hashfull 0 tbhits 0 time 2 pv h7h3
  info depth 2 seldepth 2 multipv 1 score cp -31 nodes 106 nps 53000 hashfull 0 tbhits 0 time 2 pv h7h3 g3g4
  info depth 3 seldepth 4 multipv 1 score cp -29 nodes 203 nps 67666 hashfull 0 tbhits 0 time 3 pv c6c5 h0h4 b9c7 c3c4
  info depth 4 seldepth 4 multipv 1 score cp -29 nodes 259 nps 86333 hashfull 0 tbhits 0 time 3 pv c6c5 h0h4 b9c7 c3c4
  ...
  ```
</details>

---

## Non-standard commands

### `bench`

This runs a standard search benchmark on a pre-selected assortment of positions. It prints the total combined nodes searched, as well as time taken. This command serves two primary purposes:

* it can be used as a basic nodes-per-second speed benchmark

* the total number of nodes searched can be used as a "signature" or "fingerprint" of the exact search algorithm version in the binary

The main utility of the nodecount signature is to ensure that, when testing possible new patches on Fishtest, the author and workers are working on the exact same code. It also can be used to verify which version or release you have locally. Each functional commit in the Pikafish commit history includes a standardized nodecount signature. (For example, the nodecount signature of [Pikafish 2023-03-05](https://github.com/official-stockfish/Stockfish/commit/876afdd3b610eebc402b478327d0838a4495b3a2) is 1146720.)

There are several parameters which can be used to tweak exactly what sort of benchmark is run:

Usage: `bench [ttSize] [threads] [limit] [fenFile] [limitType]`

The standardized nodecount signature of a version is obtained using all default parameters.

_Note: All parameters are optional._

| Parameter   |  Type  |  Default  | Values                                           | Meaning                          |
|-------------|:------:|:---------:|--------------------------------------------------|----------------------------------|
| `ttSize`    | number |    `16`   |                                                  | Hash value                       |
| `threads`   | number |    `1`    |                                                  | Number of threads                |
| `limit`     | number |    `13`   |                                                  | The limit of `limitType`         |
| `fenFile`   | string | `default` | `default`, `current` or `[file path]`            | The positions used for the bench |
| `limitType` | string |  `depth`  | `depth`, `perft`, `nodes`, `movetime` or `eval`. | The type of limit                |

<details>
  <summary>Example</summary>

  ```
  > position startpos
  > bench 16 1 1 current depth
  Position: 1/1 (rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1)
  info string NNUE evaluation using pikafish.nnue enabled
  info depth 1 seldepth 1 multipv 1 score cp 8 nodes 74 nps 74000 hashfull 0 tbhits 0 time 1 pv b2e2
  bestmove b2e2

  ===========================
  Total time (ms) : 4
  Nodes searched  : 75
  Nodes/second    : 18750
  ```
</details>

> [!NOTE]
> * **String parameters are case-sensitive**. In case of invalid values of string parameters, the error is not given, and the behavior is undefined (the program does not fall back to a default value).
> * The `[file path]` may contain **one or more positions**, each on a separate line.

### `d`

Display the current position, with ASCII art and FEN.

<details>
  <summary>Example</summary>

  ```
  > d

   +---+---+---+---+---+---+---+---+---+
   | r | n | b | a | k | a | b | n | r | 9
   +---+---+---+---+---+---+---+---+---+
   |   |   |   |   |   |   |   |   |   | 8
   +---+---+---+---+---+---+---+---+---+
   |   | c |   |   |   |   |   | c |   | 7
   +---+---+---+---+---+---+---+---+---+
   | p |   | p |   | p |   | p |   | p | 6
   +---+---+---+---+---+---+---+---+---+
   |   |   |   |   |   |   |   |   |   | 5
   +---+---+---+---+---+---+---+---+---+
   |   |   |   |   |   |   |   |   |   | 4
   +---+---+---+---+---+---+---+---+---+
   | P |   | P |   | P |   | P |   | P | 3
   +---+---+---+---+---+---+---+---+---+
   |   | C |   |   |   |   |   | C |   | 2
   +---+---+---+---+---+---+---+---+---+
   |   |   |   |   |   |   |   |   |   | 1
   +---+---+---+---+---+---+---+---+---+
   | R | N | B | A | K | A | B | N | R | 0
   +---+---+---+---+---+---+---+---+---+
     a   b   c   d   e   f   g   h   i
  
  Fen: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1
  Key: FDA3193C470C785C
  Checkers:
  ```
</details>

### `eval`

Display the static evaluation of the current position.

<details>
  <summary>Example</summary>

  ```
  > eval
  info string NNUE evaluation using pikafish.nnue enabled
  
  
   NNUE derived piece values:
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |   r   |   n   |   b   |   a   |   k   |   a   |   b   |   n   |   r   |
  | -2.49 | -1.05 | -0.34 | -0.31 |       | -0.33 | -0.41 | -1.03 | -2.41 |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |       |       |       |       |       |       |       |       |       |
  |       |       |       |       |       |       |       |       |       |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |       |   c   |       |       |       |       |       |   c   |       |
  |       | -1.48 |       |       |       |       |       | -1.43 |       |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |   p   |       |   p   |       |   p   |       |   p   |       |   p   |
  | +0.07 |       | -0.07 |       | -0.38 |       | -0.12 |       | -0.00 |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |       |       |       |       |       |       |       |       |       |
  |       |       |       |       |       |       |       |       |       |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |       |       |       |       |       |       |       |       |       |
  |       |       |       |       |       |       |       |       |       |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |   P   |       |   P   |       |   P   |       |   P   |       |   P   |
  | -0.05 |       | +0.07 |       | +0.25 |       | +0.11 |       | +0.02 |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |       |   C   |       |       |       |       |       |   C   |       |
  |       | +1.39 |       |       |       |       |       | +1.36 |       |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |       |       |       |       |       |       |       |       |       |
  |       |       |       |       |       |       |       |       |       |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  |   R   |   N   |   B   |   A   |   K   |   A   |   B   |   N   |   R   |
  | +2.61 | +1.00 | +0.37 | +0.32 |       | +0.34 | +0.43 | +1.02 | +2.53 |
  +-------+-------+-------+-------+-------+-------+-------+-------+-------+
  
   NNUE network contributions (White to move)
  +------------+------------+------------+------------+
  |   Bucket   |  Material  | Positional |   Total    |
  |            |   (PSQT)   |  (Layers)  |            |
  +------------+------------+------------+------------+
  |  0         |     0.00   |  +  0.24   |  +  0.24   |
  |  1         |     0.00   |  -  0.30   |  -  0.30   |
  |  2         |     0.00   |  +  0.35   |  +  0.35   |
  |  3         |     0.00   |  +  0.20   |  +  0.20   |
  |  4         |     0.00   |  +  0.07   |  +  0.07   |
  |  5         |     0.00   |  +  0.09   |  +  0.09   |
  |  6         |     0.00   |  +  0.07   |  +  0.07   |
  |  7         |     0.00   |  +  0.12   |  +  0.12   | <-- this bucket is used
  +------------+------------+------------+------------+
  
  NNUE evaluation        +0.12 (white side)
  Final evaluation       +0.20 (white side) [with scaled NNUE, optimism, ...]
  ```
</details>

### `compiler`

Give information about the compiler and environment used for building a binary.

### `export_net [filename]`

Exports the currently loaded network to a file.
If the currently loaded network is the embedded network and the filename is not specified then the network is saved to the file matching the name of the embedded network, as defined in `evaluate.h`.
If the currently loaded network is not the embedded network (some net set through the UCI `setoption`) then the filename parameter is required and the network is saved into that file.

### `flip`

Flips the side to move.
