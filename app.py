import ctypes
import tkinter as tk

from const import *
from controller import Controller
from view import View


class App(tk.Tk):
  def __init__(self):
    super().__init__()
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    self.title('AutoAccepter')
    self.geometry("1280x720")
    # self.call('tk', 'scaling', 2.0)
    self.resizable(False,False)
    self.configure(bg=ROOT_WINDOW_BACKGROUND_COLOR)
    # self.eval('tk::PlaceWindow . center')
    self.protocol("WM_DELETE_WINDOW", self.__on_closing)

    self.__view = View(self)
    # self.wait_visibility()
    self.__controller = Controller(self.__view)
    self.__view.set_controller(self.__controller)

  def __on_closing(self):
    self.__controller.kill_thread = True
    self.destroy()
    
    

