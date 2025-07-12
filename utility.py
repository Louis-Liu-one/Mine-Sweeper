'''
Mine Sweeper -- utility.py
Copyright(c) 2024 Liu One  All rights reserved.

程序所需的实用工具。
'''

from manyinputdialog import ManyInputDialog


def sequence_copy(sequence):
    '''嵌套列表的深度拷贝，基于递归。'''
    if isinstance(sequence, list):
        return [sequence_copy(elem) for elem in sequence]
    return sequence


def ask_settings(root):
    '''向用户询问游戏配置。'''
    root.withdraw()  # 隐藏
    dialog = ManyInputDialog(  # 询问格子数量、难度
        root, 'Game Settings', '',
        ('Width [1, 50]', int, {
            'initialvalue': 15, 'minvalue': 1, 'maxvalue': 50}),
        ('Height [1, 50]', int, {
            'initialvalue': 15, 'minvalue': 1, 'maxvalue': 50}),
        ('Difficulty Rate', float,
            {'initialvalue': .25, 'minvalue': 0, 'maxvalue': 1}),
        ('MBoard File', 'file',
            {'filetypes': [("Mine Sweeper's Mine Board", '*.mboard')],
             'required': False}))
    root.deiconify()  # 显示
    return dialog.outputs
