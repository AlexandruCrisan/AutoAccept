import os
import tkinter as tk
from functools import partial
from tkinter.simpledialog import askstring

import utils
from const import *


class View(tk.Frame):
  def __init__(self, parent) -> None:
    super().__init__(parent)
    self.__parent = parent
    self.__controller = None
    
    # Account username
    self.summoner_name = tk.StringVar(value='Waiting for Name')
    self.display_username = tk.Label(master=parent, font=FONT_PRIMARY, fg=TEXT_COLOR_PRIMARY, bg=parent["bg"], textvariable=self.summoner_name).pack(anchor=tk.NE, padx=PADDING_X_MIN)

    # Level percentage
    self.level_percentage = tk.StringVar(value='20% => 200lvl')
    self.display_level = tk.Label(master=parent, font=FONT_SECONDARY, fg=TEXT_COLOR_SECONDARY, bg=parent["bg"], textvariable=self.level_percentage).pack(anchor=tk.E, padx=PADDING_X_MIN)

    # Champion Select feature toggle button
    self.__is_toggle_champ_select = False
    self.champion_select_feature_button = tk.Button(master=parent,borderwidth=0, bg = BG_COLOR_CHAMP_SELECT_BUTTON_FALSE, text=CHAMPION_SELECT_FEATURE_TEXT ,font=ERROR_FONT, command=self.__champion_select_feature_button_pressed)
    self.champion_select_feature_button.pack(anchor=tk.W, padx=20)

    # Start Process Button
    self.__is_toggle_start_process = False
    self.start_process_button = tk.Button(master=parent,borderwidth=0, bg = BG_COLOR_CHAMP_SELECT_BUTTON_FALSE, text=START_PROCESS_BUTTON_TEXT ,font=ERROR_FONT, command=self.__start_process_button_pressed)
    self.start_process_button.pack(anchor=tk.W, padx=20, pady=50)

    # Main frame for selecting champion feature
    self.main_frame = tk.Frame(master=parent, bg=parent["bg"])
    self.main_frame.pack(side=tk.RIGHT, padx=40)

    # 3 buttons 
    self.selected_champs_frame = tk.Frame(master=self.main_frame, bg=self.main_frame["bg"])
    self.selected_champs_frame.pack(side=tk.LEFT)

    self.tbd_image = tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}tbd.png")

    self.first_pick = tk.Button(master=self.selected_champs_frame, text="Pick1  ", fg=TEXT_COLOR_PRIMARY, font=FONT_SECONDARY, bg=self.selected_champs_frame["bg"], compound="right", image=self.tbd_image, borderwidth=0)
    self.first_pick.pack(side=tk.TOP, padx=10)
    self.second_pick = tk.Button(master=self.selected_champs_frame, text="Pick2  ", fg=TEXT_COLOR_PRIMARY, font=FONT_SECONDARY, bg=self.selected_champs_frame["bg"], compound="right", image=self.tbd_image, borderwidth=0)
    self.second_pick.pack(side=tk.TOP, padx=10)
    self.ban_pick = tk.Button(master=self.selected_champs_frame, text="Ban  ",fg=TEXT_COLOR_PRIMARY, font=FONT_SECONDARY, bg=self.selected_champs_frame["bg"], compound="right", image=self.tbd_image, borderwidth=0)
    self.ban_pick.pack(side=tk.TOP, padx=10)

    # Frame for searchbar, scrollbar and canvas
    self.sub_frame = tk.Frame(master=self.main_frame, bg=parent["bg"])
    self.sub_frame.pack(side=tk.LEFT)

    # Searchbar
    self.search_bar = tk.Entry(master=self.sub_frame, font=TEXT_COLOR_SECONDARY)
    self.search_bar.bind("<KeyRelease>", self.__text_changed_in_entry)
    self.search_bar.grid(row=0, column=0)

    # Frame for canvas
    self.frame_container=tk.Frame(master=self.sub_frame, bg=self.sub_frame["bg"])
    self.frame_container.grid()
    self.frame_container.columnconfigure(0, weight=1)
    self.frame_container.rowconfigure(0, weight=1)

    # Canvas to draw champion buttons on
    self.canvas_container=tk.Canvas(self.frame_container, height=300, width=216)
    self.canvas_container.grid(row=0,column=0)
    self.frame2=tk.Frame(master=self.canvas_container)

    # Scrollbar for grid
    self.myscrollbar=tk.Scrollbar(master=self.frame_container,orient="vertical",command=self.canvas_container.yview) # will be visible if the frame2 is to to big for the canvas
    self.myscrollbar.grid(row=0, column=1, sticky=tk.NS)
    self.canvas_container.create_window((0,0),window=self.frame2,anchor='nw')

    # Remember the photos 
    self.photos = []


    self.__setup_champion_buttons()

  def __champion_select_button_clicked(self, btn):
    print(btn.cget('text'))

  def __text_changed_in_entry(self, e):
    typed = self.search_bar.get()
    print(f"TYPED: {typed}")
    data = self.__get_champion_images_from_dir(typed)

    self.__load_champions_by_list(files=data)

  def __get_champion_images_from_dir(self, filter=None):
    files = []
    for filename in os.listdir(CHAMPION_ICONS_DIR):
      f = os.path.join(CHAMPION_ICONS_DIR, filename)

      # checking if it is a file
      if os.path.isfile(f):
        if filename != "tbd.png":
          if filter == '':
            files.append(f)
          elif filename.lower().startswith(filter.lower()):
              files.append(f)

    return files

  def __clear_frame(self):
    for widget in self.frame2.winfo_children():
      widget.destroy()

  def __load_champions_by_list(self, files):
    self.__clear_frame()
    row, column = 0,0
    buttons = [[0 for _ in range(100)] for _ in range(100)]
    for f in files:
      self.photos.append(tk.PhotoImage(file=f))
      btn = tk.Button(master=self.frame2, text=f.split('/')[2].split('.')[0], image=self.photos[-1], borderwidth=0)
      btn.config(command=lambda button=btn: self.__champion_select_button_clicked(button))
      if column == NUMBER_OF_COLUMNS:
        row += 1
        column = 0
      btn.grid(row=row, column=column)
      buttons[row][column] = btn
      column += 1

    self.frame2.update()
    # first5columns_width = sum([buttons[0][j].winfo_width() for j in range(0, NUMBER_OF_COLUMNS)])
    # print(first5columns_width)
    # self.canvas_container.config(width=first5columns_width)
    self.canvas_container.configure(yscrollcommand=self.myscrollbar.set, scrollregion=f"0 0 0 {self.frame2.winfo_height()}" )

  def __setup_champion_buttons(self):
    files = []
    for filename in os.listdir(CHAMPION_ICONS_DIR):
      f = os.path.join(CHAMPION_ICONS_DIR, filename)

      # checking if it is a file
      if os.path.isfile(f):
        if filename != "tbd.png":
          files.append(f)

    self.__load_champions_by_list(files=files)
  
  def __start_process_button_pressed(self):
    self.__is_toggle_start_process = not self.__is_toggle_start_process
    new_color = BG_COLOR_CHAMP_SELECT_BUTTON_TRUE if self.__is_toggle_start_process else BG_COLOR_CHAMP_SELECT_BUTTON_FALSE
    new_text = STOP_PROCESS_BUTTON_TEXT if self.__is_toggle_start_process else START_PROCESS_BUTTON_TEXT
    self.start_process_button.configure(bg=new_color, text=new_text)

    # Controller implementation
    self.__controller.start_process()


  def __champion_select_feature_button_pressed(self):
    self.__is_toggle_champ_select = not self.__is_toggle_champ_select
    new_color = BG_COLOR_CHAMP_SELECT_BUTTON_TRUE if self.__is_toggle_champ_select else BG_COLOR_CHAMP_SELECT_BUTTON_FALSE
    self.champion_select_feature_button.configure(bg=new_color)
    self.__controller.champion_select_feature_on = self.__is_toggle_champ_select

  def set_controller(self, value):
    self.__controller = value
    self.__controller.connect_to_LCU()

  def prompt_game_folder(self):
    return askstring(title=POPUP_WINDOW_NAME, prompt="League installation path", parent=self.__parent)
  
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
    self.__controller.assure_game_folder()
    print("CHANGE PRESSED")
