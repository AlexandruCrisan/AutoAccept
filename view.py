import cProfile
import multiprocessing
import os
import pstats
import tkinter as tk
from threading import Thread
from tkinter.simpledialog import askstring

from PIL import Image

import utils
from const import *


class View(tk.Frame):
  def __init__(self, parent) -> None:
    super().__init__(parent)
    self.__parent = parent
    self.__controller = None
    
    # Remember the photos 
    self.spells_photos = []
    self.champion_photos = []
    self.pick_champion_photos = [tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}tbd.png"), tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}tbd.png"), tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}tbd.png")]
    self.pick_spells_photos = [tk.PhotoImage(file=(f"{SUMMONER_SPELLS_DIR}/tbd.png")), tk.PhotoImage(file=(f"{SUMMONER_SPELLS_DIR}/tbd.png"))]

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

    # 3 buttons frame
    self.selected_champs_frame = tk.Frame(master=self.main_frame, bg=self.main_frame["bg"])
    self.selected_champs_frame.pack(side=tk.LEFT)

    # self.tbd_image = tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}tbd.png")

    # First pick button
    self.__is_looking_for_first_pick = False
    self.first_pick = tk.Button(master=self.selected_champs_frame, activebackground=self.selected_champs_frame["bg"], text="Pick1  ", fg=TEXT_COLOR_PRIMARY, font=FONT_SECONDARY, bg=self.selected_champs_frame["bg"], compound="right", image=self.pick_champion_photos[0], borderwidth=0, command=self.__first_pick_clicked)
    self.first_pick.pack(side=tk.TOP, padx=10, pady=10)

    # Second pick button
    self.__is_looking_for_second_pick = False
    self.second_pick = tk.Button(master=self.selected_champs_frame, activebackground=self.selected_champs_frame["bg"], text="Pick2  ", fg=TEXT_COLOR_PRIMARY, font=FONT_SECONDARY, bg=self.selected_champs_frame["bg"], compound="right", image=self.pick_champion_photos[0], borderwidth=0, command=self.__second_pick_clicked)
    self.second_pick.pack(side=tk.TOP, padx=10, pady=10)

    # Ban pick button
    self.__is_looking_for_ban_pick = False
    self.ban_pick = tk.Button(master=self.selected_champs_frame, activebackground=self.selected_champs_frame["bg"], text="Ban  ",fg=TEXT_COLOR_PRIMARY, font=FONT_SECONDARY, bg=self.selected_champs_frame["bg"], compound="right", image=self.pick_champion_photos[0], borderwidth=0, command=self.__ban_pick_clicked)
    self.ban_pick.pack(side=tk.TOP, padx=10, pady=10)

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

    # Main Frame for spell selection
    self.spell_main_frame = tk.Frame(master=parent, bg=parent['bg'])
    self.spell_main_frame.pack(side=tk.BOTTOM, pady=10)

    # Frame for user selection
    self.user_selection_frame = tk.Frame(master=self.spell_main_frame, bg=self.spell_main_frame["bg"])
    self.user_selection_frame.pack(side=tk.TOP)

    # Frame for available options
    self.available_options_frame = tk.Frame(master=self.spell_main_frame, bg=self.spell_main_frame["bg"])
    self.available_options_frame.pack(side=tk.BOTTOM, pady=20)

    # Available options buttons
    # self.available_options_buttons = self.__initialise_spell_buttons()

    # User selection buttons
    self.__is_looking_for_d_spell = False
    self.__is_looking_for_f_spell = False
    
    self.selected_spell_d = tk.Button(master=self.user_selection_frame, text="D", activeforeground=TEXT_COLOR_PRIMARY, fg=TEXT_COLOR_PRIMARY, bg=self.spell_main_frame['bg'], font=FONT_PRIMARY,compound="center", borderwidth=0, bd=0, highlightthickness=0, image=self.pick_spells_photos[0], command=self.__d_spell_clicked)
    self.selected_spell_f = tk.Button(master=self.user_selection_frame, text="F", activeforeground='blue', fg='black',bg=self.spell_main_frame['bg'], font=('Helvetica', 25, 'bold'),compound="center", borderwidth=0, bd=0, highlightthickness=0, image=self.pick_spells_photos[0], command=self.__f_spell_clicked)

    self.selected_spell_d.pack(side="left")
    self.selected_spell_f.pack(side="left", padx=40)
    

    

    self.__initialise_spell_buttons()

    self.__assignment_threads = list()

    self.start_thread = Thread()

    self.__setup_champion_buttons()

  def __f_spell_clicked(self):
    self.__is_looking_for_f_spell = not self.__is_looking_for_f_spell
    self.selected_spell_f.config(bg="red" if self.__is_looking_for_f_spell is True else self.spell_main_frame["bg"])
    if self.__is_looking_for_f_spell is True:
      self.__is_looking_for_d_spell = False
      self.selected_spell_d.config(bg=self.spell_main_frame["bg"])   
 
 
  def __d_spell_clicked(self):
    self.__is_looking_for_d_spell = not self.__is_looking_for_d_spell
    self.selected_spell_d.config(bg="red" if self.__is_looking_for_d_spell is True else self.spell_main_frame["bg"])

    if self.__is_looking_for_d_spell is True:
      self.__is_looking_for_f_spell = False
      self.selected_spell_f.config(bg=self.spell_main_frame["bg"])

  def __spell_button_clicked(self, spell):
    if self.__is_looking_for_f_spell is True:
      self.__is_looking_for_f_spell = False
      self.selected_spell_f.config(bg=self.spell_main_frame["bg"])
      self.pick_spells_photos[1]=tk.PhotoImage(file=f"{SUMMONER_SPELLS_DIR}/{spell}.png")
      self.__update_picture(self.selected_spell_f, self.pick_spells_photos[1])

    elif self.__is_looking_for_d_spell is True:
      self.__is_looking_for_d_spell = False
      self.selected_spell_d.config(bg=self.spell_main_frame["bg"])
      self.pick_spells_photos[0]=tk.PhotoImage(file=f"{SUMMONER_SPELLS_DIR}/{spell}.png")
      self.__update_picture(self.selected_spell_d, self.pick_spells_photos[0])

  
  def __initialise_spell_buttons(self):
    for filename in os.listdir(SUMMONER_SPELLS_DIR):
      if filename != 'tbd.png':
        f = os.path.join(SUMMONER_SPELLS_DIR, filename)
        self.spells_photos.append(tk.PhotoImage(file=f))
        btn = tk.Button(master=self.available_options_frame, highlightthickness=0, text=filename.split('.')[0], image=self.spells_photos[-1], borderwidth=0)
        btn.pack(side="left", padx=5)
        btn.config(command=lambda button=btn: self.__spell_button_clicked(button.cget('text')))

  def __first_pick_clicked(self):
    self.__is_looking_for_first_pick = not self.__is_looking_for_first_pick

    self.first_pick.config(bg="red" if self.__is_looking_for_first_pick is True else self.selected_champs_frame["bg"])
    
    if self.__is_looking_for_first_pick is True:
      self.__is_looking_for_second_pick = False
      self.__is_looking_for_ban_pick = False
      self.second_pick.config(bg=self.selected_champs_frame["bg"])
      self.ban_pick.config(bg=self.selected_champs_frame["bg"])

  def __second_pick_clicked(self):
    self.__is_looking_for_second_pick = not self.__is_looking_for_second_pick
    self.second_pick.config(bg="red" if self.__is_looking_for_second_pick is True else self.selected_champs_frame["bg"])
    
    if self.__is_looking_for_second_pick is True:
      self.__is_looking_for_first_pick = False
      self.__is_looking_for_ban_pick = False
      self.first_pick.config(bg=self.selected_champs_frame["bg"])
      self.ban_pick.config(bg=self.selected_champs_frame["bg"])

  def __ban_pick_clicked(self):
    self.__is_looking_for_ban_pick = not self.__is_looking_for_ban_pick
    self.ban_pick.config(bg="red" if self.__is_looking_for_ban_pick is True else self.selected_champs_frame["bg"])
    
    if self.__is_looking_for_ban_pick is True:
      self.__is_looking_for_first_pick = False
      self.__is_looking_for_second_pick = False
      self.first_pick.config(bg=self.selected_champs_frame["bg"])
      self.second_pick.config(bg=self.selected_champs_frame["bg"])

  def __update_picture(self, btn, image):
    btn.config(image=image)

  def __set_controller_pick_ban(self, value, pick_index=-1):
    if pick_index == -1:
      self.__controller.ban = self.__controller.get_champion_id(value)
      return
    self.__controller.picks[pick_index] = self.__controller.get_champion_id(value)


  def __champion_select_button_clicked(self, btn):
    if self.__is_looking_for_first_pick is True:
      self.pick_photos[0]=tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}{btn}.png")
      self.__update_picture(self.first_pick, self.pick_photos[0])
      self.__assignment_threads.append(Thread(target=self.__set_controller_pick_ban, args=(btn,0,)))
      self.__assignment_threads[-1].start()
      return
      
    if self.__is_looking_for_second_pick is True:
      self.pick_photos[1]=tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}{btn}.png")
      self.__update_picture(self.second_pick, self.pick_photos[1])
      self.__assignment_threads.append(Thread(target=self.__set_controller_pick_ban, args=(btn,1,)))
      self.__assignment_threads[-1].start()
      return

    if self.__is_looking_for_ban_pick is True:
      self.pick_photos[2]=tk.PhotoImage(file=f"{CHAMPION_ICONS_DIR}{btn}.png")
      self.__update_picture(self.ban_pick, self.pick_photos[2])
      self.__assignment_threads.append(Thread(target=self.__set_controller_pick_ban, args=(btn,)))
      self.__assignment_threads[-1].start()
      return

  def __text_changed_in_entry(self, e):
    typed = self.search_bar.get()
    print(f"TYPED: {typed}")
    # with cProfile.Profile() as pr:
    data = self.__get_champion_images_from_dir(typed)

    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()
  
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
      self.champion_photos.append(tk.PhotoImage(file=f))
      btn = tk.Button(master=self.frame2, text=f.split('/')[2].split('.')[0], image=self.champion_photos[-1], borderwidth=0)
      btn.config(command=lambda button=btn: self.__champion_select_button_clicked(button.cget('text')))
      if column == NUMBER_OF_COLUMNS:
        row += 1
        column = 0
      btn.grid(row=row, column=column)
      buttons[row][column] = btn
      column += 1

    self.frame2.update()
    self.canvas_container.configure(yscrollcommand=self.myscrollbar.set, scrollregion=f"0 0 0 {self.frame2.winfo_height()}" )

  def __setup_champion_buttons(self):
    files = []
    for filename in os.listdir(CHAMPION_ICONS_DIR):
      f = os.path.join(CHAMPION_ICONS_DIR, filename)

      # checking if it is a file
      if os.path.isfile(f):
        if filename != "tbd.PNG":
          files.append(f)

    self.__load_champions_by_list(files=files)
  
  def __start_process_button_pressed(self):
    self.__is_toggle_start_process = not self.__is_toggle_start_process
    new_color = BG_COLOR_CHAMP_SELECT_BUTTON_TRUE if self.__is_toggle_start_process else BG_COLOR_CHAMP_SELECT_BUTTON_FALSE
    new_text = STOP_PROCESS_BUTTON_TEXT if self.__is_toggle_start_process else START_PROCESS_BUTTON_TEXT
    self.start_process_button.configure(bg=new_color, text=new_text)

    for (index, t) in enumerate(self.__assignment_threads):
      if t.is_alive() is True:
        print(f"T{index} ALIVE")
        t.join()

    self.__assignment_threads.clear()
    # Controller implementation

    if self.start_thread.is_alive():
      self.__controller.kill_thread = True
      return
    self.start_thread = Thread(target=self.__controller.start_process)
    self.start_thread.start()


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

      dx, dy = 0, 0
      x = self.__parent.winfo_x()
      y = self.__parent.winfo_y()
      w = top.winfo_width()
      h = top.winfo_height()  
      top.geometry("%dx%d+%d+%d" % (w, h, x + dx, y + dy))

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
