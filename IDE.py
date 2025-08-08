from tkinter import *
from tkinter.filedialog import asksaveasfilename,askopenfilename
import subprocess

class TextLineNumbers(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''Redraw the line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum, fill="#606366")
            i = self.textwidget.index("%s+1line" % i)

class CustomText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        # create a proxy for the text widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.call("interp", "alias", self._w, "_proxy", self._orig)

    def _proxy(self, *args):
        # let the actual widget perform the command
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "delete") or
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result

class IDE:
    def __init__(self, root):
        self.root = root
        self.file_path = ''
        self.root.title('IDE')
        self.root.configure(bg="#263238")

        self.menu_bar=Menu(self.root, bg="#263238", fg="white")

        self.run_bar=Menu(self.menu_bar,tearoff=0, bg="#263238", fg="white")
        self.run_bar.add_command(label='Run',command=self.run)
        self.menu_bar.add_cascade(label='Run',menu=self.run_bar)

        self.file_menu=Menu(self.menu_bar,tearoff=0, bg="#263238", fg="white")
        self.file_menu.add_command(label='Open',command=self.open_file)
        self.file_menu.add_command(label='Save',command=self.save_as)
        self.file_menu.add_command(label='Save As',command=self.save_as)
        self.file_menu.add_command(label='Exit',command=self.root.destroy)
        self.menu_bar.add_cascade(label='File',menu=self.file_menu)

        self.root.config(menu=self.menu_bar)

        self.paned_window = PanedWindow(self.root, orient=VERTICAL, bg="#263238")
        self.paned_window.pack(fill=BOTH, expand=1)

        self.editor_frame = Frame(self.paned_window, bg="#263238")
        self.paned_window.add(self.editor_frame, weight=2)

        self.linenumbers = TextLineNumbers(self.editor_frame, width=30, bg="#37474F")
        self.linenumbers.pack(side="left", fill="y")

        self.editor=CustomText(self.editor_frame, bg="#263238", fg="white", insertbackground="white", font=("Courier New", 12))
        self.editor.pack(side="left", fill="both", expand=True)

        self.linenumbers.attach(self.editor)

        self.editor.bind("<<Change>>", self.on_change)
        self.editor.bind("<Configure>", self.on_change)

        self.code_output=Text(self.paned_window, height=10, bg="#263238", fg="white", font=("Courier New", 12))
        self.paned_window.add(self.code_output, weight=1)

    def set_file_path(self, path):
        self.file_path=path

    def on_change(self, event):
        self.linenumbers.redraw()

    def open_file(self):
        path=askopenfilename(filetypes=[('Python Files','*.py')])
        with open(path,'r') as file:
            code=file.read()
            self.editor.delete('1.0',END)
            self.editor.insert('1.0',code)
            self.set_file_path(path)

    def save_as(self):
        if self.file_path=='':
            path=asksaveasfilename(filetypes=[('Python Files','*.py')])
        else:
            path=self.file_path
        with open(path,'w') as file:
            code=self.editor.get('1.0',END)
            file.write(code)
            self.set_file_path(path)

    def run(self):
        if self.file_path=='':
            save_prompt=Toplevel()
            text=Label(save_prompt,text='Please save your code')
            text.pack()
            return
        command=f'python {self.file_path}'
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output,error=process.communicate()
        self.code_output.insert('1.0',output)
        self.code_output.insert('1.0',error)


if __name__ == "__main__":
    compiler=Tk()
    ide = IDE(compiler)
    compiler.mainloop()
