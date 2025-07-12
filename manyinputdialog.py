
'''
Mine Sweeper -- manyinputdialog.py
Copyright(c) 2024 Liu One  All rights reserved.

本模块提供了多参数对话框，可一次询问多个值。详情请参见ManyInputDialog。
'''

from functools import partial
from os.path import exists
import tkinter as tk
from tkinter.constants import *
from tkinter.messagebox import showwarning
from tkinter.filedialog import askopenfilename


class ManyInputDialog(tk.Toplevel):
    '''
    多参数对话框。
    用例：
    dialog = ManyInputDialog(
        root, 'This is the title', 'This is the prompt:',
        ('integer', int, {'minvalue': 3, 'initialvalue': 5}),
        ('float', float, {'maxvalue': 1, 'initialvalue': 0.2}),
        ('string', str, {'initialvalue': 'This is my string'}),
        ('radiobutton', list, {'choices': ['Yes', 'No', "Don't know"]}),
        ('checkbutton', list, {'choices': ['A', 'B', 'C'], 'radio': False}),
        ('file chooser', 'file', {'filetypes': [('Python Files', '*.py')]}))
    print(dialog.outputs)
    详情请参见ManyInputDialog.__init__()。
    '''
    default_vals = {
        int: 0,
        float: 0.0,
        str: '',
        list: [],
        'file': "Haven't chosen",
    }
    default_paras = {
        'required': True,
        'minvalue': -float('inf'),
        'maxvalue': float('inf'),
        'choices': [],
        'radio': True,
        'filetypes': [('All files', '*')],
    }

    def __init__(self, master, title, prompt, *inputs):
        '''
        初始化多参数对话框。
          title :: 窗口标题。
         prompt :: 对话框中最上方的提示词，可以为空。
        *inputs :: 形如[('a', int, {'minvalue': 3}),
                   ('b', float, {'initialvalue': 10})]的参数列表。第一个值是参数的
                   提示；第二个值是需要的类型，支持int、float、str、list、'file'；第
                   三个值是可选参数，支持required、minvalue、maxvalue、
                   initialvalue、choices、radio、filetypes。

                       required: 是否是必选项，默认为True；
                       minvalue: 最小值，默认为-inf，若期望类型为int/float，则会检查；
                       maxvalue: 最大值，默认为inf，若期望类型为int/float，则会检查；
                   initialvalue: 初始值，int: 0，float: 0.0，str: ''，
                                 list: 第一个选项；
                        choices: 期望类型为list时的选项，如
                                 ['choice-1', 'choice-2']，可迭代，默认为[]；
                          radio: 是否为单选，默认为True；
                      filetypes: 可以选择的文件的类型，默认为所有文件。
        返回的值通过dialog.outputs访问。
        '''
        super().__init__(master)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.resizable(width=False, height=False)
        self.configure(menu=tk.Menu(self))

        self.title(title)
        count = 0
        if prompt:  # 若提示语为空，则不空行
            tk.Label(self, text=prompt).grid(columnspan=2, sticky=W)
            count = 1  # 控制行数的变量
        self.outputs = []    # 类返回，也就是得到正确结果之时访问此属性
        self.inputvars = []  # 询问时用到的tkinter变量

        for inputprompt, inputtype, paras in inputs:
            for para, default in self.default_paras.items():
                if para not in paras:        # 设置默认值
                    paras[para] = self.default_paras[para]
            if 'initialvalue' not in paras:  # 设置初始值
                paras['initialvalue'] = self.default_vals[inputtype]
            if inputtype != list:  # 不是list
                var = (            # 根据期望类型选择类
                    tk.IntVar if inputtype == int else
                    tk.DoubleVar if inputtype == float else
                    tk.StringVar)(self)
            # 期望类型是list时，var为一个元组
            elif paras['radio']:  # 单选，只需要一个变量
                var = (tk.IntVar(self),)
            else:                 # 多选，需要多个变量
                var = tuple(
                    tk.IntVar(self) for i in range(len(paras['choices'])))
            if inputtype != list:
                var.set(paras['initialvalue'])
            elif paras['radio']:
                var[0].set(paras['initialvalue'])
            else:
                for index in paras['initialvalue']:
                    var[index].set(1)
            self.inputvars.append((var, inputtype, paras))

            tk.Label(
                self, text=inputprompt).grid(row=count, sticky=NE)
            if inputtype not in (list, 'file'):  # 输入框
                tk.Entry(  # 将每个输入框绑定到变量，因此只需要存变量就好了
                    self, textvariable=var, width=20).grid(
                    row=count, column=1)
            elif inputtype == list:              # 选项框
                frame = tk.Frame(self, width=20)
                num = 0
                for choice in paras['choices']:
                    if paras['radio']:  # 单选
                        button = tk.Radiobutton(
                            frame, text=choice,
                            variable=var[0], value=num)
                    else:               # 多选
                        button = tk.Checkbutton(
                            frame, text=choice,
                            variable=var[num], onvalue=1, offvalue=0)
                    num += 1
                    button.grid(sticky=W)
                frame.grid(row=count, column=1)
            elif inputtype == 'file':            # 文件选择
                frame = tk.Frame(self, width=20)
                tk.Message(                      # 文件名
                    frame, width=200,
                    textvariable=var).grid()
                tk.Button(                       # 选择文件的按钮
                    frame, text='Choose file',
                    command=partial(
                        self.get_filename, var, paras['filetypes'])).grid()
                frame.grid(row=count, column=1)
            count += 1

        tk.Button(  # OK按钮
            self, text='OK', width=8, default=ACTIVE,
            command=self.ok).grid(row=count, column=1, sticky=E)
        self.bind('<Return>', self.ok)
        self.mainloop()

    def get_filename(self, var, filetypes):
        '''获取文件名并设置变量。filetypes为可以选择的文件的类型。'''
        var.set(askopenfilename(parent=self, filetypes=filetypes))

    def ok(self, event=None):
        '''
        返回结果的按钮，点击OK调用。结果通过列表dialog.outputs访问。
        列表dialog.outputs中包含的值有：
              int: 用户输入的整数
            float: 用户输入的浮点数
              str: 用户输入的字符串
             list: 用户选择的选项的下标，例如[0,2]
        '''
        for var, inputtype, paras in self.inputvars:
            try:
                # 输入，可能出错
                if inputtype != list:
                    self.outputs.append(var.get())  # 添加到结果列表
                    if (inputtype in (int, float)   # 若是数字，则检查最大最小值
                            and (
                                var.get() < paras['minvalue']
                                or var.get() > paras['maxvalue'])):
                        raise tk.TclError        # 检查最大最小值是否满足
                    elif (inputtype == 'file'
                            and paras['required']
                            and not exists(var.get())):
                        raise tk.TclError        # 在必选时检查文件是否存在
                    elif inputtype == 'file' and not exists(var.get()):
                        self.outputs[-1] = None  # 非必选时返回None
                # 选项，不可能出错
                elif paras['radio']:  # 单选，返回已选的选项的下标
                    self.outputs.append([var[0].get()])
                else:        # 多选，返回已选的选项的下标
                    self.outputs.append([
                        i for i in range(len(var)) if var[i].get() == 1])
            except tk.TclError:        # 打开失败说明tkinter变量的值非法
                showwarning('Failed to OK', 'There are invalid values.')
                self.outputs = []  # 重置
                return
        self.destroy()  # 关闭窗口，停止主循环
        self.quit()


if __name__ == '__main__':
    root = tk.Tk()
    dialog = ManyInputDialog(
        root, 'This is the title', 'This is the prompt:',
        ('Integer', int, {'minvalue': 3, 'initialvalue': 5}),
        ('Float', float, {'maxvalue': 1, 'initialvalue': 0.2}),
        ('String', str, {'initialvalue': 'This is my string'}),
        ('Radio Buttons', list, {'choices': ['Yes', 'No', "Don't know"]}),
        ('Check Buttons', list, {'choices': ['A', 'B', 'C'], 'radio': False}),
        ('File Chooser', 'file', {'filetypes': [('Python Files', '*.py')]}))
    print(dialog.outputs)
    root.mainloop()
