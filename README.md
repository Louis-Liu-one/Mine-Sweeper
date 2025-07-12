# Mine Sweeper
A simple Mine Sweeper game made by Liu One.

Copyright © 2024 Liu One  *All rights reserved.*

## How to Play?
* First, single click to mark a cell as a mine.

* Second, double click to open a cell.

* Third, if a green *click* cell appears, click it first.

* Finally, have a good time!

## Some Skills to Play
**LEGEND**
 Sign|Meaning
----:|----
**4**|An opened cell
**F**|A cell which has been marked as a mine
**#**|A cell which can be opened
**!**|A cell which must be a mine

Don't know how to play the game? Here are some tips:

First, the showed number when you click a cell means the number of the mine around the cell you click. If the number is $n$, we call the opened cell an ``$n$-cell''. For example,
!|3|!
-|-|-
!|4|2
1|2|!

Second, if you know a cell is a mine, you can mark it by a single clicking. Besides, if you know a cell is not a mine, you can open it by a double clicking.
0|1|F
-|-|-
1|2|2
1|F|1

But how to know whether a cell is a mine? The following tips can be helpful:

Third, if $8 - n$ cells around an $n$-cell are opened, then the other $n$ cells around the $n$-cell are all mines.
0|1|!
-|-|-
1|2|2
1|!|1

For example, if 5 cells around a 3-cell are opened, then the other 3 cells around the 3-cell are all mines.
1|2|!
-|-|-
!|3|2
2|!|1

Fourth, if $n$ cells around an $n$-cell have been marked as a mine, then all the other $8 - n$ cells around the $n$-cell can be opened. For example, $n = 3$:
#|#|F
-|-|-
F|3|#
#|F|#

This law is the reverse of the Third Law.
#|F|F
-|-|-
F|5|F
#|F|#

These are the 4 basic skills to play the game. You can explore more laws and become an expert!

## File Structure
There are 5 Python files, some GIF images and other files.

### Python Files
* `main.py` The main program. Run this to open the window and play.
* `minesweeper.py` The major file. The core of the game.
* `minehelper.py` The documents above are in this file. Create a window and include the documents.
* `manyinputdialog.py` Dialog which can ask many kinds of inputs, such as int, string, file or choose.
* `utility.py` Some useful functions.

### GIF Images
Such as images of the flag and the mine. These images are in the folder `images/`.

### Other Files
* `makefile` Pack the game as a MacOS application bundle with Nuitka.
* `favicon.icns` The icon of the bundle.

## Finally
I hope you can enjoy yourself!
