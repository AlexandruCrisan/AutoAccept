import tkinter as tk

from controller import Controller
from view import View


class App(tk.Tk):
  def __init__(self):
    super().__init__()

    self.title('AutoAccepter')
    self.geometry("1280x720")
    self.resizable(False,False)
    self.configure(bg='#39206b')

    self.__view = View(self)
    # self.wait_visibility()
    self.__controller = Controller(self.__view)
    self.__view.set_controller(self.__controller)
    
    

