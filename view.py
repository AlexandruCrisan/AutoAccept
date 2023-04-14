import tkinter as tk
from tkinter.simpledialog import askstring

import utils
from const import *


class View(tk.Frame):
  def __init__(self, parent) -> None:
    super().__init__(parent)
    self.__parent = parent
    self.__controller = None
    
    # Account Username
    self.summoner_name = tk.StringVar(value='Waiting for Name')
    self.display_username = tk.Label(master=parent, font=FONT_PRIMARY, fg=TEXT_COLOR_PRIMARY, bg=parent["bg"], textvariable=self.summoner_name).pack(anchor=tk.NE, padx=PADDING_X_MIN)

    # Level percentage
    self.level_percentage = tk.StringVar(value='20% => 200lvl')
    self.display_level = tk.Label(master=parent, font=FONT_SECONDARY, fg=TEXT_COLOR_SECONDARY, bg=parent["bg"], textvariable=self.level_percentage).pack(anchor=tk.E, padx=PADDING_X_MIN)


  def set_controller(self, value):
    self.__controller = value
    self.__controller.connect_to_LCU()

  def prompt_game_folder(self):
    return askstring(title=POPUP_WINDOW_NAME, prompt="SCRIE CEVA", parent=self.__parent)
  
  def error_window(self, text: str):
    try:    
      top = tk.Toplevel(self.__parent)
      top.geometry("250x100")
      top.title("ERROR")
      top.configure(bg="#8c0611")
      tk.Label(master=top, bg = top["bg"], text=text, fg=TEXT_COLOR_PRIMARY, font=ERROR_FONT).pack(expand=1)
      tk.Button(master=top, text="Change path", command=lambda: self.__change_path_button_pressed(top)).pack(side="left")
      tk.Button(master=top, text="Quit", command=self.__quit).pack(side="right", padx=10)
      top.grab_set()
      top.wait_window()
    except Exception:
      quit()
    

  def __quit(self):
    self.__parent.destroy()

  def __change_path_button_pressed(self, top):
    top.destroy()
    utils.save_json_to_file("userdata.json", {'GAME_FOLDER': ''})
    self.__controller.assure_game_folder(True)
    print("CHANGE PRESSED")
