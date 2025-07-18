
'''
Mine Sweeper -- minesweeper.py
Copyright(c) 2024 Liu One  All rights reserved.
Click to mark a block as a mine.
Double click to open a block.

扫雷游戏主体程序。
单击标记格子为雷，双击打开格子。
'''

import random
import functools
import pathlib

import tkinter as tk
from tkinter.messagebox import showinfo, showwarning, askyesnocancel
from tkinter.messagebox import WARNING
from tkinter.filedialog import asksaveasfile
from tkinter.constants import *

from utility import sequence_copy, ask_settings
from minehelper import MineHelper, HandleHelper


class Application(tk.Frame):
    '''
    扫雷主体。参数详见Application.__init__()。
    所有以GUI_开头的方法都是图形用户界面的直接操作，其它一般是底层原理实现。
    '''

    colors = [  # 格子周围雷的数量决定格子的前景色
        None, 'Blue', 'Green',
        'Red', 'DarkBlue', 'DarkRed',
        'Purple', 'Gray', 'DarkGray']
    filetypes = [("Mine Sweeper's Mine Board", '*.mboard')]
    around_blocks = [  # 一个格子周围格子的相对位置
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def __init__(self, master, filename=None):
        '''
        初始化游戏。
        filename=None :: mboard文件名，给出则打开文件，没有给出则忽略，并自主询问信息。
        '''
        super().__init__(master)

        self.GUI_load_image()                           # 加载图片
        self.recent_grids = [sequence_copy(self.grid)]  # 历史记录，用于撤销操作
        self.first_click = True                         # 是否初次点击
        self.have_won = False                           # 是否胜利
        if filename is None:  # 未传入mboard文件
            self.block_grid = []
            self.new_game()   # 自主询问信息
        else:                 # 传入mboard文件
            self.width, self.height, self.mine_sum, self.grid \
                = self.open_board(filename)            # 打开文件
            self.block_grid = self.GUI_grid_buttons()  # 按钮矩阵
            self.GUI_update_cells()

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

    def new_game(self, event=None):
        '''自主询问游戏配置信息，然后开始新游戏。'''
        self.width, self.height, difficulty_rate, filename \
            = ask_settings(self.master)  # 自主询问信息
        if filename is not None:
            self.width, self.height, self.mine_sum, self.grid \
                = self.open_board(filename)        # 打开文件
        else:
            self.mine_sum = int(difficulty_rate * self.width * self.height)
        # 重置按钮矩阵
        if self.block_grid:
            for line in self.block_grid:
                for button in line:
                    button.destroy()               # 销毁旧按钮
        self.block_grid = self.GUI_grid_buttons()  # 创建新按钮
        if filename is not None:
            self.GUI_update_cells()  # 更新格子
        self.first_click = True

    def save_board(self, event=None):
        '''保存棋盘。'''
        file = asksaveasfile(
            filetypes=self.filetypes,
            initialfile='untitled',
            parent=self.master)
        if file is not None:
            file.write('{} {} {}\n'.format(
                self.width, self.height, self.mine_sum))
            for line in self.grid:
                for block_mine, block_state in line:
                    file.write('{}.{} '.format(block_mine, block_state))
                file.write('\n')
            file.close()

    def show_help(self, event=None):
        '''显示位于minehelper.py中的帮助文档。'''
        MineHelper(self.master)

    def handle_helper(self):
        '''显示用户操作帮助文档，位于minehelper.py。'''
        HandleHelper(
            self.master, title='Handle Helper', width=280, height=120)

    def open_board(self, filename):
        '''打开棋盘，返回元组(宽, 高, 雷数, 格子矩阵)。'''
        file = open(filename)
        line = file.readline()
        width, height, mine_sum = [int(elem) for elem in line.split()]
        grid = []
        while line:
            line = file.readline()[:-1].split()
            if line:
                grid.append([
                    [int(num) for num in elem.split('.')]
                    for elem in line])
        return width, height, mine_sum, grid

    def initial_grid(self, cells=None):
        '''
        初始化游戏格子。
        width x height的格子矩阵，每个格子包括两个数。
        第一个数是格子周围雷的数量，若格子是雷，则是-1。
        第二个数是格子的状态，-1未打开，0已打开，1标记为雷，2标错。
        cells :: 不能被设为雷的格子，用于初次点击。
        '''
        # 生成width x height的格子矩阵
        grid = [[
            [0, -1] for j in range(self.width)]
            for i in range(self.height)]
        mine_blocks = random.sample(  # 在矩阵中随机挑选格子
            [(i, j) for j in range(self.width)
                for i in range(self.height)
                if cells is not None and (i, j) not in cells],
            self.mine_sum)
        for i, j in mine_blocks:  # 将挑选的格子设置为雷
            grid[i][j][0] = -1
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in mine_blocks:  # 计算未挑选的格子周围雷的数量
                    grid[i][j][0] = sum([
                        (i + di, j + dj) in mine_blocks
                        for di, dj in self.around_blocks])
        return grid

    def pos_valid(self, i, j):
        '''判断坐标(i, j)是否合法，返回布尔值。'''
        return 0 <= i and i < self.height and 0 <= j and j < self.width

    def get_around_blocks(self, i, j):
        '''
        返回格子(i, j)周围的情况。
        return :: 元组(周围格子数, 周围雷数, 周围已打开格子数, 周围已标记为雷格子数)。
        '''
        block_count, opened_block, marked_block = 0, 0, 0
        for di, dj in self.around_blocks:
            if self.pos_valid(i + di, j + dj):
                block_count += 1
                if self.grid[i + di][j + dj][1] == 0:
                    opened_block += 1
                elif self.grid[i + di][j + dj][1] == 1:
                    marked_block += 1
        return block_count, self.grid[i][j][0], opened_block, marked_block

    def open_block(self, i, j):
        '''
        打开格子。
        return :: 1: 是雷，正常打开
                  0: 不是雷，正常打开
                 -1: 坐标非法，无法打开
                 -2: 已打开，无法再次打开
                 -3: 已踩雷，无法打开
        '''
        if not self.pos_valid(i, j):  # 坐标非法
            return -1
        elif self.grid[i][j][1] == 0:            # 已打开
            return -2
        elif self.grid[i][j][1] == 2:            # 已失败
            return -3                          # 打开失败，退出
        self.grid[i][j][1] = 0        # 设置为已打开
        if self.grid[i][j][0] == -1:  # 是雷
            return 1
        return 0  # 不是雷

    def mark_mine(self, i, j, mark=False):
        '''
        标记或取消标记格子为雷。
        mark=False :: 参见self.GUI_mark_mine()。
        '''
        if not self.pos_valid(i, j) or self.first_click:
            return                                    # 坐标非法
        if self.grid[i][j][1] not in (0, 2):
            self.grid[i][j][1] = -self.grid[i][j][1]  # 标记或取消标记雷
            if mark:
                self.grid[i][j][1] = 1
        return self.grid[i][j][1]                     # 返回当前状态

    def check_end(self):
        '''检查玩家是否正确打开和标记所有格子，即是否胜利。'''
        for line in self.grid:
            for block_mine, block_state in line:
                if (block_state == 1
                        and block_mine != -1  # 标记错的
                    or block_state == -1      # 未打开的
                    or block_state == 0       # 打开的雷（失败）
                        and block_mine == -1):
                    return False
        return True

    def GUI_load_image(self):
        '''加载所需图标。'''
        folder = 'images/'
        self.flag_image = tk.PhotoImage(file=folder + 'flag.gif')      # 旗子
        self.mine_image = tk.PhotoImage(file=folder + 'mine.gif')      # 雷
        self.empty_image = tk.PhotoImage(file=folder + 'empty.gif')    # 空白
        self.opened_image = tk.PhotoImage(file=folder + 'opened.gif')  # 黄色
        self.wrong_image = tk.PhotoImage(file=folder + 'wrong.gif')  # 错误的标记
        self.click_image = tk.PhotoImage(file=folder + 'click.gif')  # 点击位置

    def GUI_grid_buttons(self):
        '''布局按钮，返回按钮矩阵。'''
        block_grid = [
            [None for j in range(self.width)]
            for i in range(self.height)]  # 按钮矩阵
        for i in range(self.height):
            for j in range(self.width):  # 设置按钮并添加到按钮矩阵
                button = tk.Button(
                    self, image=self.empty_image, compound=CENTER,
                    width=30, height=30,
                    command=functools.partial(
                        self.GUI_mark_mine, i, j))  # 单击标记为雷
                button.bind(                        # 双击打开
                    '<Double-Button-1>',
                    functools.partial(self.GUI_open_block, i, j, True))
                button.grid(row=i, column=j)
                block_grid[i][j] = button  # 保存至block_grid
        return block_grid

    def GUI_update_cells(self, update_all=False):
        '''
        根据self.grid更新格子。
        update_all=False :: 若为True则在原基础上将关闭的格子亦更新，但效率较低。
        '''
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j][1] == 0:    # 打开
                    self.grid[i][j][1] = -1    # 先设置为未打开，再打开
                    self.GUI_open_block(i, j, istop=False)
                elif self.grid[i][j][1] == 1:  # 标记
                    self.grid[i][j][1] = -1    # 先设置为未打开，再打开
                    self.GUI_mark_mine(i, j)
                elif self.grid[i][j][1] == 2:  # 标错
                    self.block_grid[i][j].configure(image=self.wrong_image)
                if update_all and self.grid[i][j][1] == -1:
                    self.block_grid[i][j].configure(  # 更新关闭的格子
                        image=self.empty_image, text='')

    def GUI_auto_open_one_block(self, i, j):
        '''
        自动打开已开格子(i, j)周围的可开格子，
        在self.GUI_auto_open_block()中调用。
        '''
        flag = False  # 此轮是否打开了格子
        block_count, mine_count, opened_block, marked_block \
            = self.get_around_blocks(i, j)
        if opened_block + mine_count != block_count \
                and mine_count == marked_block:
            for di, dj in self.around_blocks:  # 打开周边格子
                if self.pos_valid(i + di, j + dj) \
                        and self.grid[i + di][j + dj][1] != 1:
                    flag |= self.GUI_open_block(
                        i + di, j + dj, istop=True,
                        auto_open_block=False) == 0
        return flag

    def GUI_auto_open_block(self):
        '''
        自动打开格子，格子多时可能效率较低。
        判断方法为：若某已开格子周围已标记为雷格子数与雷数相等，则打开剩余格子，
        程序假设用户的标记不出错。
        '''
        flag = False  # 是否还可以打开
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j][1] == 0:  # 格子已打开
                    flag |= self.GUI_auto_open_one_block(i, j)
        if flag:
            self.GUI_auto_open_block()

    def GUI_open_block(
            self, i, j, istop=False, auto_open_block=False, event=None):
        '''
        打开格子(i, j)并更新。
        istop :: 是否是顶层函数。避免在打开所有格子时过多的调用。
        auto_open_block :: 是否自动打开格子。
        '''
        if self.first_click:  # 初次点击判断落点后生成格子
            self.grid = self.initial_grid(cells=[  # 新棋盘
                (i + di, j + dj)     # 初次点击点及其周围不能有雷
                for di, dj in [(0, 0)] + self.around_blocks])
            self.first_click = False
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
            else:                # 周围没有雷
                for di, dj in self.around_blocks:  # 打开周围的格子
                    self.GUI_open_block(i + di, j + dj)
            if istop and not self.have_won and self.check_end():  # 判断是否成功
                showinfo('Succeed', 'Winner!', parent=self.master)
                self.have_won = True
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
                        self.GUI_open_block(gi, gj)  # 打开所有格子
                self.update()
                # 重新尝试同一棋盘、尝试新棋盘、或什么也不做
                result = askyesnocancel(
                    'Failed!',
                    'You have stepped on a mine! Retry?'
                    ' Yes to retry the same mine board,'
                    ' No to create a new game'
                    ' and Cancel to close this window.',
                    icon=WARNING, parent=self.master)
                if result is not None:
                    (self.retry if result else self.new_game)()
        if istop:  # 自动标记雷并记录历史
            self.GUI_auto_mark_mine()
            if auto_open_block:
                self.GUI_auto_open_block()
            self.recent_grids.append(sequence_copy(self.grid))
        return state

    def GUI_auto_mark_mine(self):
        '''
        扫描并自动标记格子为雷。
        判断方法为：若某已开格子周围未开未标记格子数与雷数相等，
        则标记周围未开未标记格子为雷。
        '''
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j][1] == 0:  # 格子已打开
                    block_count, mine_count, opened_block, _ \
                        = self.get_around_blocks(i, j)
                    if opened_block + mine_count == block_count:
                        for di, dj in self.around_blocks:  # 标记周边格子
                            self.GUI_mark_mine(i + di, j + dj, mark=True)

    def GUI_mark_mine(self, i, j, mark=False):
        '''
        标记或取消标记格子(i, j)为雷并更新屏幕。
        mark=False :: 若为True，则必须标记为雷，而非取消。
        '''
        flag = self.mark_mine(i, j, mark)     # 标记为雷
        if flag is not None and flag != 0:    # 是未打开的格子
            self.block_grid[i][j].configure(  # 将格子更新为旗子的图片
                image=(self.flag_image if flag > 0 else self.empty_image))
        if flag is not None and not self.have_won \
                and self.check_end():  # 判断是否成功
            showinfo('Succeed', 'Winner!', parent=self.master)
            self.have_won = True

    def GUI_undo(self, event=None):
        '''撤销打开格子的操作，其间标记雷的操作将同时撤销。'''
        if len(self.recent_grids) > 1:
            self.recent_grids.pop()
            self.grid = sequence_copy(self.recent_grids[-1])
            self.GUI_update_cells(update_all=True)
