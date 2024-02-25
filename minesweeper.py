
'''
Mine Sweeper -- minesweeper.py 1.1
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
    2 已打开，且有关的格子
    X 已打开，且无关的格子
    F 未打开，已标记为雷的格子
    - 未打开，且一定不是雷的格子
    ! 未打开，且一定是雷的格子
    ? 未打开，且无关的格子

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
    a(2,1)的作用域A={(1,0),(1,2)}包含于b(1,1)的作用域B={(0,0),(0,1),(0,2),(1,0),(1,2)}中，
    !A=1，!B=1，因此!(B-A)=!{(0,0),(0,1),(0,2)}=!B-!A=0，没有一个是雷。

4. 1--2定理
    若!A=1，!B=2，B-A的大小为1，B交A的大小为2，则!(B-A)=1。
        F X ?
        X 2 ?
        X 2 ?
        X X !
    !(A(1,1))=1，!(B(2,1))=2，其它条件均符合，则B-A={(3,2)}中必然有一个雷，即(3,2)必然是雷。
    运用三号法则可知，(0,2)必然不是雷。
    原理：B={B1,B2,B3}，A={B1,B2,A1}。由于!B=2，可知这两个雷有三种情况：B1&B2、B2&B3、B1&B3。
         由于!A=1，则B1&B2可能排除，因此B3，即B-A必然是雷。
'''

from sys import argv
from random import sample
from functools import partial
from pathlib import Path

import tkinter as tk
from tkinter.messagebox import showinfo, showwarning, askyesnocancel
from tkinter.messagebox import WARNING
from tkinter.filedialog import asksaveasfile
from tkinter.constants import *

from manyinputdialog import ManyInputDialog
from minehelper import MineHelper, HandleHelper


class Application(tk.Frame):
    '''扫雷主体。参数详见Application.__init__()。'''

    colors = [  # 格子周围雷的数量决定格子的前景色
        None, 'Blue', 'Green',
        'Red', 'DarkBlue', 'DarkRed',
        'Purple', 'Gray', 'DarkGray']
    filetypes = [("Mine Sweeper's Mine Board", '*.mboard')]

    def __init__(self, master, width, height, mine_sum, filename=None):
        '''
        初始化游戏。
        width :: 横向格子数
        height :: 纵向格子数
        mine_sum :: 雷的数量
        filename=None :: 文件名，给出则打开文件，忽略前3项；没有给出则忽略。
        '''
        super().__init__(master)

        self.gui_load_image()
        if filename is not None:
            self.width, self.height, self.mine_sum, self.grid \
                = self.open_board(filename)        # 打开文件
        else:
            self.width, self.height = width, height
            self.mine_sum = mine_sum
            self.grid = self.initial_grid()        # 格子矩阵

        self.block_grid = self.gui_grid_buttons()  # 存储按钮的矩阵
        self.gui_setup_cells()

    def retry(self):
        '''重新尝试同一棋盘。'''
        flag = True
        for i in range(self.height):
            for j in range(self.width):
                self.grid[i][j][1] = -1               # 关闭格子
                self.block_grid[i][j].configure(      # 重置按钮
                    text='', image=self.empty_image)
                if flag and self.grid[i][j][0] == 0:  # 为用户指出合适的首次点击点
                    self.block_grid[i][j].configure(
                        image=self.click_image)
                    flag = False

    def new_game(self):
        '''重设棋盘，开启新游戏。'''
        self.grid = self.initial_grid()  # 新棋盘
        for line in self.block_grid:
            for button in line:
                button.destroy()                  # 销毁旧按钮
        self.block_grid = self.gui_grid_buttons()  # 创建新按钮

    def save_board(self):
        '''保存棋盘。'''
        file = asksaveasfile(
            filetypes=self.filetypes,
            initialfile='untitled',
            parent=self.master)
        if file is not None:
            file.write('{} {} {}\n'.format(
                len(self.grid[0]), len(self.grid), self.mine_sum))
            for line in self.grid:
                for block_mine, block_state in line:
                    file.write('{}.{} '.format(block_mine, block_state))
                file.write('\n')
            file.close()

    def show_help(self):
        '''显示位于minehelper.py中的帮助文档。'''
        MineHelper(self.master)

    def handle_helper(self):
        '''显示用户操作帮助文档，位于minehelper.py。'''
        HandleHelper(
            self.master, title='Handle Helper', width=280, height=120)

    def open_board(self, filename):
        '''打开棋盘，返回宽、高、雷数、格子矩阵。'''
        file = open(filename)
        line = file.readline()
        width, height, mine_sum = [int(elem) for elem in line.split()]
        grid = []
        while line:
            line = file.readline()[:-1].split()
            if line != '':
                grid.append([
                    [int(num) for num in elem.split('.')] for elem in line])
        return width, height, mine_sum, grid

    def initial_grid(self):
        '''
        初始化游戏格子。
        width x height的格子矩阵，每个格子包括两个数。
        第一个数是格子周围雷的数量，若格子是雷，则是-1。
        第二个数是格子的状态，-1未打开，0已打开，1标记为雷，2标错。
        '''
        # 生成width x height的格子矩阵
        grid = [[
            [0, -1] for j in range(self.width)]
            for i in range(self.height)]
        mine_blocks = sample(  # 在矩阵中随机挑选格子
            [(i, j) for j in range(self.width)
                for i in range(self.height)],
            self.mine_sum)
        for i, j in mine_blocks:  # 将挑选的格子设置为雷
            grid[i][j][0] = -1
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in mine_blocks:  # 计算未挑选的格子周围雷的数量
                    grid[i][j][0] = sum([(i - 1, j) in mine_blocks,
                                         (i + 1, j) in mine_blocks,
                                         (i, j - 1) in mine_blocks,
                                         (i, j + 1) in mine_blocks,
                                         (i - 1, j - 1) in mine_blocks,
                                         (i - 1, j + 1) in mine_blocks,
                                         (i + 1, j - 1) in mine_blocks,
                                         (i + 1, j + 1) in mine_blocks])
        return grid

    def open_block(self, i, j):
        '''
        打开格子。
        return :: 1: 是雷，正常打开
                  0: 不是雷，正常打开
                 -1: 坐标非法，无法打开
                 -2: 已打开，无法再次打开
                 -3: 已踩雷，无法打开
        '''
        if (i >= self.height or i < 0          # 纵坐标非法
                or j >= self.width or j < 0):  # 横坐标非法
            return -1
        elif self.grid[i][j][1] == 0:            # 已打开
            return -2
        elif self.grid[i][j][1] == 2:            # 已失败
            return -3                          # 打开失败，退出
        self.grid[i][j][1] = 0        # 设置为已打开
        if self.grid[i][j][0] == -1:  # 是雷
            return 1
        return 0  # 不是雷

    def mark_mine(self, i, j):
        '''标记或取消标记格子为雷。'''
        self.grid[i][j][1] = -self.grid[i][j][1]  # 设置为旗子
        return self.grid[i][j][1]                 # 标记或取消

    def check_end(self):
        '''检查玩家是否正确打开和标记所有格子。'''
        for line in self.grid:
            for block_mine, block_state in line:
                if ((block_state == 1          # 标记错的
                        and block_mine != -1)
                    or block_state == -1       # 未打开的
                    or (block_state == 0       # 打开的雷（失败）
                        and block_mine == -1)):
                    return False
        return True

    def gui_load_image(self):
        '''加载所需图片。'''
        folder = str(Path(__file__).parent.resolve()) + '/'
        self.flag_image = tk.PhotoImage(file=folder + 'flag.gif')      # 旗子
        self.mine_image = tk.PhotoImage(file=folder + 'mine.gif')      # 雷
        self.empty_image = tk.PhotoImage(file=folder + 'empty.gif')    # 空白
        self.opened_image = tk.PhotoImage(file=folder + 'opened.gif')  # 黄色
        self.wrong_image = tk.PhotoImage(file=folder + 'wrong.gif')    # 错误的标记
        self.click_image = tk.PhotoImage(file=folder + 'click.gif')    # 游戏开始时需要点击的格子

    def gui_grid_buttons(self):
        '''布局按钮。'''
        block_grid = [
            [None for j in range(self.width)]
            for i in range(self.height)]  # 按钮矩阵
        flag = True
        for i in range(self.height):
            for j in range(self.width):  # 设置按钮并添加到按钮矩阵
                button = tk.Button(
                    self, image=self.empty_image, compound=CENTER,
                    width=30, height=30, command=partial(  # 单击标记为雷
                        self.gui_mark_mine, i, j))
                button.bind(                               # 双击打开
                    '<Double-Button-1>',
                    partial(
                        self.gui_open_block,
                        i, j, True))
                button.grid(row=i, column=j)
                block_grid[i][j] = button
                if flag and self.grid[i][j][0] == 0:  # 为用户指出合适的首次点击点
                    button.configure(image=self.click_image)
                    flag = False
        return block_grid

    def gui_setup_cells(self):
        '''根据文件中的信息打开/标记格子。'''
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j][1] == 0:    # 打开
                    self.grid[i][j][1] = -1
                    self.gui_open_block(i, j)
                elif self.grid[i][j][1] == 1:  # 标记
                    self.grid[i][j][1] = -1
                    self.gui_mark_mine(i, j)
                elif self.grid[i][j][1] == 2:  # 标错
                    self.block_grid[i][j].configure(image=self.wrong_image)

    def gui_open_block(self, i, j, istop=False, event=None):
        '''
        打开格子并更新屏幕。
        istop :: 是否是顶层函数。避免在打开所有格子时过多的调用。
        '''
        state = self.open_block(i, j)  # 打开格子
        if state == -3:   # 格子标错
            self.block_grid[i][j].configure(image=self.wrong_image)
        elif state == 0:  # 不是雷
            mine_num = self.grid[i][j][0]     # 获取格子周围雷的数量
            self.block_grid[i][j].configure(  # 将格子更新为黄色
                image=self.opened_image, font=('Futura', 25, 'bold'), text='')
            if mine_num != 0:                     # 周围有雷
                self.block_grid[i][j].configure(  # 显示雷的数量
                    text=str(mine_num), foreground=self.colors[mine_num])
            else:  # 周围没有雷
                # 打开周围的格子
                self.gui_open_block(i + 1, j)
                self.gui_open_block(i - 1, j)
                self.gui_open_block(i, j + 1)
                self.gui_open_block(i, j - 1)
                self.gui_open_block(i + 1, j + 1)
                self.gui_open_block(i + 1, j - 1)
                self.gui_open_block(i - 1, j + 1)
                self.gui_open_block(i - 1, j - 1)
            if istop and self.check_end():  # 判断是否成功
                showinfo('Succeed', 'You are so clever!', parent=self.master)
        elif state == 1:  # 是雷，失败
            # 将格子更新为雷的图片
            self.block_grid[i][j].configure(image=self.mine_image)
            if istop:  # 是顶层函数
                for gi in range(self.height):
                    for gj in range(self.width):
                        # 检查标错的格子
                        if (self.grid[gi][gj][1] == 1
                                and self.grid[gi][gj][0] != -1):
                            # 将标错的格子设为红色
                            self.block_grid[gi][gj].configure(
                                image=self.wrong_image)
                            self.grid[gi][gj][1] = 2
                for gi in range(self.height):
                    for gj in range(self.width):
                        # 下面的调用不是顶层函数
                        self.gui_open_block(gi, gj)  # 打开所有格子
                self.update()
                # 重新尝试同一棋盘、尝试新棋盘、或什么也不做
                result = askyesnocancel('Failed!', (
                    'You have stepped on the mine! Retry?'
                    ' Yes to retry the same mine board,'
                    ' No to create a new game'
                    ' and Cancel to close this window.'),
                    icon=WARNING, parent=self.master)
                if result is not None:
                    (self.retry if result else self.new_game)()

    def gui_mark_mine(self, i, j):
        '''标记为雷并更新屏幕。'''
        flag = self.mark_mine(i, j)           # 标记为雷
        if flag != 0:                         # 是未打开的格子
            self.block_grid[i][j].configure(  # 将格子更新为旗子的图片
                image=(self.flag_image if flag > 0 else self.empty_image))
        if self.check_end():                  # 判断是否成功
            showinfo('Succeed', 'You are so clever!', parent=self.master)


def setup_menu(root, app):
    '''初始化游戏菜单。'''
    menu = tk.Menu(root)
    operations_menu = tk.Menu(menu)
    operations_menu.add_command(label='Retry', command=app.retry)
    operations_menu.add_command(label='New Game', command=app.new_game)
    operations_menu.add_command(label='Save Board', command=app.save_board)
    menu.add_cascade(label='Operations', menu=operations_menu)  # 操作
    help_menu = tk.Menu(menu)
    help_menu.add_command(label='Show Help', command=app.show_help)
    help_menu.add_command(label='Handle Helper', command=app.handle_helper)
    menu.add_cascade(label='Help', menu=help_menu)  # 帮助
    root.configure(menu=menu)


def main():
    '''主程序。'''
    root = tk.Tk()
    root.title('Mine Sweeper')
    root.resizable(width=False, height=False)

    if len(argv) == 1:   # 未传入mboard文件
        root.withdraw()  # 隐藏
        dialog = ManyInputDialog(  # 询问格子数量、难度
            root, 'Game Parameters', '',
            ('Width', int, {
                'initialvalue': 15, 'minvalue': 1, 'maxvalue': 50}),
            ('Height', int, {
                'initialvalue': 15, 'minvalue': 1, 'maxvalue': 50}),
            ('Difficulties', float,
                {'initialvalue': .25, 'minvalue': 0, 'maxvalue': 1}),
            ('MBoard File', 'file',
                {'filetypes': [("Mine Sweeper's Mine Board", '*.mboard')],
                 'required': False}))
        width, height, difficulties, filename = dialog.outputs   # 解包
        root.deiconify()  # 显示
    else:  # 传入mboard文件
        width, height, difficulties, filename = 0, 0, 0, argv[1]

    mine_sum = int(difficulties * width * height)  # 计算雷数
    app = Application(root, width, height, mine_sum, filename)
    app.pack()
    setup_menu(root, app)
    root.mainloop()


if __name__ == '__main__':
    main()
