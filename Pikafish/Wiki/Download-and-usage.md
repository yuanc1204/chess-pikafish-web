## Download Pikafish

> [!NOTE]
> Pikafish is a [**command line program**](Pikafish-FAQ#executing-pikafish-opens-a-cmd-window). You may want to use it in your own UCI-compatible [xiangqi GUI](#download-a-xiangqi-gui).  
> Developers should communicate with Pikafish via the [UCI protocol](https://github.com/official-pikafish/Pikafish/wiki/UCI-&-Commands#standard-commands).

### Get started

1. First [download](#official-downloads) Pikafish. Pikafish itself is *completely free* with all its options.
2. Next, [download a GUI](#download-a-xiangqi-gui) (Graphical User Interface) as it is needed to conveniently use Pikafish. There are multiple free and commercial GUIs available. Different GUI's have more or less advanced features, for example, an opening explorer or automatic game analysis.
3. Now Pikafish must be made available to the GUI. [Install in a Xiangqi GUI](#install-in-a-xiangqi-gui) explains how this can be done for some of them. If a different GUI is used, please read the GUI's manual.
4. Ultimately, change the default [settings](#change-settings) of Pikafish to get the [best possible analysis](Pikafish-FAQ#optimal-settings).

---
### Official downloads

#### Latest release

https://pikafish.org/

Binaries are also available on GitHub: https://github.com/official-pikafish/Pikafish/releases/latest

#### Latest development build

1. Navigate to our [actions](https://github.com/official-pikafish/Pikafish/actions/workflows/pikafish.yml)
2. Choose the latest run
3. Scroll to the bottom
3. Download your preferred binary

> [!NOTE]
> We **only** recommend downloading from the [official GitHub releases](https://github.com/official-pikafish/Pikafish/releases).  
> Websites such as [棋中论坛](<http://www.qqzze.com/>) are third parties, so we cannot guarantee the safety, reliability, and availability of those binaries because we are not responsible for them.

### Choose a binary

In order of preference:
1. x86-64-vnni512
2. x86-64-avx512
   * AMD: Zen 4 and newer (e.g. Ryzen 9 7950X).
3. x86-64-avx512f
4. x86-64-avxvnni
5. x86-64-bmi2
   * Intel: 4th Gen and newer (e.g. i7 4770K, i5 13600K).
   * AMD: Zen 3 (e.g. Ryzen 5 5600X).
6. x86-64-avx2
   * AMD: Zen, Zen+, and Zen 2 (e.g. Ryzen 5 1600, Ryzen 5 3600).
7. x86-64-sse41-popcnt

---

## Download a Xiangqi GUI

A xiangqi graphical user interface allows you to interact with the engine in a user-friendly way. Popular GUIs are:

### Free

#### Computer

| **[SharkChess](http://www.sharkchess.com/)** <br>[How to install Pikafish](#sharkchess)<br>[Change settings](#sharkchess-1) | **[XBoard](https://www.gnu.org/software/xboard/#download)** ([source code](https://ftp.gnu.org/gnu/xboard/)) <br>[How to install Pikafish](#xboard)<br>[Change settings](#xboard-1) |
|:---|:---|
| [![][sharkchess]][sharkchess] | [![][xboard]][xboard] |

### Online

> [!NOTE]
> If you don't want to download a GUI, you can also use some of the available online interfaces. Keep in mind that you might not get the latest version of Pikafish, settings might be limited and speed will be slower.

| **[XiangqiAI](https://xiangqiai.com)**<br>[Change settings](#xiangqiai) |
|:---|
| [![][xiangqiai]][xiangqiai] |

---

## Install in a Xiangqi GUI

### SharkChess

1. Engines > Engines Settings

    <img src="https://github.com/user-attachments/assets/29fd347f-0c45-459a-9c87-87fbe55a8ea3" width="300">

2. Switch to Engines Management tab and click the add button

    <img src="https://github.com/user-attachments/assets/4424f644-facc-45d3-a59b-050d37f815fc" width="300">

3. Select and open the Pikafish executable

    <img src="https://github.com/user-attachments/assets/3b0fbb50-1240-4d05-adce-20bb52c789cc" width="300">

### XBoard
1. Install `uci2wb`

    For Ubuntu distributions:
    `sudo apt install uci2wb`
    For other distros, clone and build uci2wb:
    ```
    git clone 'http://hgm.nubati.net/git/uci2wb.git'
    cd uci2wb
    make uci2wb
    make prefix=/usr install
    ```

2. Configure Pikafish as Xboard engine

    `Engine > Load New 1st Engine...`

    ![2023-07-15-12:49:50-screenshot](https://github.com/official-pikafish/Pikafish/assets/49029378/65eb5062-7958-425c-b02c-d0026a8cd42d)

> [!IMPORTANT]
> - Engine Command is `uci2wb pikafish`
> - Make sure the first three boxes are _unchecked_

---

## Change settings

> [!NOTE]
> Please check our [FAQ guide](Pikafish-FAQ#optimal-settings) to set the optimal settings.

### SharkChess

* Click the configure button

    ![image](https://github.com/user-attachments/assets/14ce3d20-736a-49d2-ab23-e746c7be11ae)

### Xboard

* Engine > Engine #1 Settings...

    ![2023-07-15-13:00:16-screenshot](https://github.com/official-pikafish/Pikafish/assets/49029378/c08aad04-1cf0-4c03-8537-d12dc4f4572e)

> [!IMPORTANT]
> Make sure `EvalFile` field is configured and pointed to the correct Pikafish NNUE file. If you don't configure this field or the path to the file is wrong then the engine will die.

### XiangqiAI

* Click the setting button

    ![2023-07-15-13:00:16-screenshot](https://github.com/user-attachments/assets/94b1e18f-7883-4ad5-bafc-a4c9fffdd6e8)

* Engine Settings

    ![image](https://github.com/user-attachments/assets/cfb14ed7-9cd6-4c30-9730-f3f3190bfbf8)

[sharkchess]: https://www-x-sharkchess-x-com.img.addlink.cn/wp-content/uploads/2018/09/shark.jpg
[xboard]: https://www.gnu.org/software/xboard/graphics/xboard-4.4.0-XQ.png
[xiangqiai]: https://github.com/user-attachments/assets/33a18c00-bad5-46e1-87f9-57dae0b40991
