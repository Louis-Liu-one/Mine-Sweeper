
'''
Mine Sweeper
Copyright(c) 2024 Liu One  All rights reserved.
Click to mark a block as a mine.
Double click to open a block.

经典扫雷游戏。版权所有，侵权必究。
单击标记格子为雷，双击打开格子。

扫雷基本技巧：

约定：
    板块：若已知某集合内有n个雷，则该集合称为一个板块，n称为板块的雷数。
    作用域：一个格子周围8个格子中所有未打开且未标记为雷的格子所组成的板块。
    格子的雷数：一个格子的作用域的雷数。
    表示格子时，先行后列，从0开始，若有名字，需用小写，如a(1,1)。
    表示板块用大写，如A，其雷数在前面加!，如!A。
图例：
    2  已打开，且与示范作用有关的格子
    X  已打开，且与示范作用无关的格子
    F  未打开，已标记为雷的格子
    -  未打开，且一定非雷的格子
    !  未打开，且一定是雷的格子
    ?  未打开，且与示范作用无关的格子

1. 当一个格子的作用域大小等于格子的雷数时，作用域内所有格子都是雷。
        ! X X
        X 2 X
        X X !

        ! ! X
        X 3 !
        X X X

2. 当一个格子的雷数为0时，其作用域中没有雷。
        F - F
        X 2 X
        X X X

3. 若一个板块A包含在另一个板块B中时，!(B-A)=!B-!A。
        - - -
        ? 1 ?
        X 1 X
        X X X
    a(2,1)的作用域A={(1,0),(1,2)}包含于b(1,1)的作用域
    B={(0,0),(0,1),(0,2),(1,0),(1,2)}中，!A=1，!B=1，因此
    !(B-A)=!{(0,0),(0,1),(0,2)}=!B-!A=0，没有一个是雷。

4. 1--2定理
    若!A=1，!B=2，B-A的大小为1，B交A的大小为2，则!(B-A)=1。
        F X ?
        X 2 ?
        X 2 ?
        X X !
    !(A(1,1))=1，!(B(2,1))=2，其它条件均符合，则B-A={(3,2)}中必然有一个
    雷，即(3,2)必然是雷。
    运用三号法则可知，(0,2)必然不是雷。
    原理：B={B1,B2,B3}，A={B1,B2,A1}。由于!B=2，可知这两个雷有三种情况：
         B1&B2、B2&B3、B1&B3。由于!A=1，则B1&B2可能排除，因此B3，即B-A必然是雷。
'''

import sys
import tkinter as tk

from utility import ask_settings
from minesweeper import Application


def setup_menu(root, app):
    '''初始化游戏菜单。'''
    menu = tk.Menu(root)
    operations_menu = tk.Menu(menu)
    operations_menu.add_command(
        label='Retry', command=app.retry, accelerator='Command+R')
    operations_menu.add_command(
        label='New Game', command=app.new_game, accelerator='Command+N')
    operations_menu.add_command(
        label='Save Board', command=app.save_board, accelerator='Command+S')
    operations_menu.add_command(
        label='Undo', command=app.GUI_undo, accelerator='Command+Z')
    menu.add_cascade(label='Operations', menu=operations_menu)  # 操作
    help_menu = tk.Menu(menu)
    help_menu.add_command(label='Show Help', command=app.show_help)
    help_menu.add_command(label='Handle Helper', command=app.handle_helper)
    menu.add_cascade(label='Help', menu=help_menu)  # 帮助
    root.configure(menu=menu)


def bind_keys(root, app):
    '''绑定快捷键。'''
    root.bind('<Command-n>', app.new_game)
    root.bind('<Command-r>', app.retry)
    root.bind('<Command-s>', app.save_board)
    root.bind('<Command-z>', app.GUI_undo)


def main():
    '''主程序。'''
    root = tk.Tk()
    root.title('Mine Sweeper')
    # 判断是否传入mboard文件
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    app = Application(root, filename)
    app.pack()
    setup_menu(root, app)
    bind_keys(root, app)
    root.mainloop()


if __name__ == '__main__':
    main()
