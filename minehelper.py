'''
Mine Sweeper -- minehelper.py
Copyright(c) 2024 Liu One  All rights reserved.

扫雷的帮助文档，详情参见MineHelper。
'''

from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *


class Helper(tk.Toplevel):
    '''帮助文档的父类。子类通过覆盖self.setup_messages()定义。'''
    colors = [  # 预定义的颜色
        None, 'Blue', 'Green',
        'Red', 'DarkBlue', 'DarkRed',
        'Purple', 'Gray', 'DarkGray']

    def __init__(
            self, master,
            width=400, height=600, title='Mine Sweeper Helper'):
        '''扫雷的帮助文档。width为文档显示区的帮助。'''
        super().__init__(master)

        self.title(title)
        self.resizable(width=False, height=False)
        self.configure(menu=tk.Menu(self))
        self.width = width
        self.small_width = width // 10
        self.height = height

        self.setup_canvas()
        self.setup_images()
        self.setup_messages()

    def setup_canvas(self):
        '''初始化画布。tk.Frame无法绑定滚动条，需要用画布绑定。'''
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        scrollbar = tk.Scrollbar(
            self, orient=VERTICAL, command=self.canvas.yview)
        self.main_frame = tk.Frame(self.canvas, width=self.small_width)
        self.main_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.create_window(0, 0, anchor=NW, window=self.main_frame)
        self.canvas.grid(sticky=NSEW, row=0, column=0)
        scrollbar.grid(sticky=NS, row=0, column=1)

    def setup_images(self):
        '''载入图片。'''
        folder = 'images/'
        self.flag = tk.PhotoImage(file=folder + 'flag.gif')
        self.mine = tk.PhotoImage(file=folder + 'mine.gif')
        self.empty = tk.PhotoImage(file=folder + 'empty.gif')
        self.opened = tk.PhotoImage(file=folder + 'opened.gif')
        self.wrong = tk.PhotoImage(file=folder + 'wrong.gif')
        self.click = tk.PhotoImage(file=folder + 'click.gif')

    def grid_messages(self, *messages):
        '''布置长串信息。可传入多个信息，将分成多个段落。'''
        for message in messages:
            tk.Message(
                self.main_frame, font=('Futura', 15),
                text=message, width=self.width).grid(sticky=W)

    def grid_cells(self, cells):
        '''
        布置演示用的扫雷格子。
        cells :: 由tuple(图片，文字)，(文字)，或(图片)组成的二维列表。
        '''
        frame = tk.Frame(self.main_frame, width=self.small_width)
        for i in range(len(cells)):
            for j in range(len(cells[0])):
                color = 'Black'
                if isinstance(cells[i][j], tuple):
                    image, text = cells[i][j]
                    if text.isdecimal():
                        color = self.colors[int(text)]
                elif isinstance(cells[i][j], tk.PhotoImage):
                    image = cells[i][j]
                    text = ''
                else:
                    image = self.empty
                    text = cells[i][j]
                tk.Button(
                    frame, text=text, font=('Futura', 25, 'bold'),
                    foreground=color, image=image, compound=CENTER,
                    width=30, height=30).grid(row=i, column=j)
        return frame

    def grid_legend(self, *legends):
        '''
        图例的布置。
        *legends :: 形如tuple(图片,图片上的文本,颜色,描述)构成的参数列表。
        '''
        frame = tk.Frame(self.main_frame, width=self.small_width)
        tk.Label(
            frame, text='Legends',
            font=('Futura', 20)).grid(columnspan=2, sticky=W)
        row = 1
        for image, imagetext, color, text in legends:
            tk.Button(
                frame, text=imagetext, font=('Futura', 25, 'bold'),
                foreground=color, image=image, compound=CENTER,
                width=30, height=30).grid(row=row, column=0)
            tk.Label(
                frame, text=text,
                font=('Futura', 15)).grid(row=row, column=1, sticky=W)
            row += 1
        return frame

    def on_frame_configure(self, event):
        '''保证canvas随frame变化而变化。'''
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))


class MineHelper(Helper):
    '''扫雷帮助文档。'''

    def setup_messages(self):
        '''文档内容。'''
        flag = self.flag      # 省略self.，增强可读性
        mine = self.mine
        empty = self.empty
        opened = self.opened

        tk.Label(
            self.main_frame, text='Mine Sweeper Helper',
            font=('Futura', 25, 'bold')).grid(sticky=W)
        ttk.Separator(self.main_frame, orient=HORIZONTAL).grid(sticky=EW)

        self.grid_legend(
            (opened, '4', self.colors[4], 'Opened cell'),
            (flag, '', None, 'Marked cell'),
            (empty, '#', None, 'Cell which can be opened'),
            (empty, '!', None, 'Cell which must be a mine'),).grid(sticky=W)
        ttk.Separator(self.main_frame, orient=HORIZONTAL).grid(sticky=EW)

        self.grid_messages(
            "Don't know how to play the game? Here are some tips:",
            "(1) The showed number when you click a cell,"
            " is the number of the mine around the cell you click.")
        self.grid_cells([
                [mine, (opened, '3'), mine],
                [mine, (opened, '4'), (opened, '2')],
                [(opened, '1'), (opened, '2'), mine]]).grid()
        ttk.Separator(self.main_frame, orient=HORIZONTAL).grid(sticky=EW)

        self.grid_messages(
            "(2) If you infer that a cell is a mine,"
            " you can mark it by clicking.", "Besides, if you"
            " infer that a cell is not a mine"
            " you can open it by double clicking.")
        self.grid_cells([
                [opened, (opened, '1'), flag],
                [(opened, '1'), (opened, '2'), (opened, '2')],
                [(opened, '1'), flag, (opened, '1')]]).grid()
        ttk.Separator(self.main_frame, orient=HORIZONTAL).grid(sticky=EW)

        self.grid_messages(
            "But how to infer?",
            "(3) If (8 - n) cells around an n-cell are opened,"
            " then the other n cells around the n-cell are all mines.")
        self.grid_cells([
                [opened, (opened, '1'), '!'],
                [(opened, '1'), (opened, '2'), (opened, '2')],
                [(opened, '1'), '!', (opened, '1')]]).grid()

        self.grid_messages(
            "For example, if 5 cells around a 3-cell are opened,"
            " then the other 3 cells around the 3-cell are all mines.")
        self.grid_cells([
                [(opened, '1'), (opened, '2'), '!'],
                ['!', (opened, '3'), (opened, '2')],
                [(opened, '2'), '!', (opened, '1')]]).grid()
        ttk.Separator(self.main_frame, orient=HORIZONTAL).grid(sticky=EW)

        self.grid_messages(
            "(4) Similarly, if n cells around an n-cell have been marked"
            " as a mine, then all the other (8 - n) cells around the n-cell"
            " can be opened. For example, n = 3:")
        self.grid_cells([
                ['#', '#', flag],
                [flag, (opened, '3'), '#'],
                ['#', flag, '#']]).grid()

        self.grid_messages(
            "The (4) Law is the reverse of the (3) Law.")
        self.grid_cells([
                ['#', flag, flag],
                [flag, (opened, '5'), flag],
                ['#', flag, '#']]).grid()
        ttk.Separator(self.main_frame, orient=HORIZONTAL).grid(sticky=EW)

        self.grid_messages(
            "The above are 4 basic laws to play Mine Sweeper."
            " You can explore more laws to become an expert!")


class HandleHelper(Helper):

    def setup_messages(self):
        self.grid_messages("First, click to mark a cell as a mine.")
        self.grid_messages("Second, double-click to open a cell.")
        self.grid_messages("Third, click the green sign first.")
        self.grid_messages("Finally, play and have fun!")


if __name__ == '__main__':
    root = tk.Tk()
    MineHelper(root)
    root.mainloop()
