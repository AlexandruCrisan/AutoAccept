import json
import os
import time
from threading import Thread

import requests
from requests.auth import HTTPBasicAuth

import utils
from const import *
from view import View


class Controller:
  def __init__(self, view:View) -> None:
    # LCU API related stuff
    self.__BASE_URL = None
    self.__auth = None
    self.__PORT = None
    self.__PASSWORD = None

    self.saved_user_file = None


    self.champion_select_feature_on = False

    self.picks = [None, None]
    self.__current_pick_index = 0
    self.ban = None

    self.kill_thread = False
    # UI Hook
    self.__view = view

  def __get_current_client_version(self):
    version = requests.get(f"https://ddragon.leagueoflegends.com/api/versions.json").json()
    return version[0]

  def get_champion_id(self, champion_name: str):
    latest = self.__get_current_client_version()

    champion_json = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/champion/{champion_name}.json").json()
    return champion_json["data"][champion_name]["key"]

  def __accept_queue(self):
    requests.post(f"https://127.0.0.1:{self.__PORT}/lol-matchmaking/v1/ready-check/accept", auth=self.__auth, verify="riotgames.pem")

  def __take_action(self, action_id: str, data):
    r = requests.patch(f"https://127.0.0.1:{self.__PORT}/lol-champ-select/v1/session/actions/{action_id}", json=data, auth=self.__auth, verify="riotgames.pem")
    return r

  def __lock_champion(self, action_id: str, data):
    return requests.post(f"https://127.0.0.1:{self.__PORT}/lol-champ-select/v1/session/actions/{action_id}/complete", json=data, auth=self.__auth, verify="riotgames.pem")

  def __champ_select(self):
    res = requests.get(f"https://127.0.0.1:{self.__PORT}/lol-champ-select/v1/session", auth=self.__auth, verify="riotgames.pem")
    res = res.json()

    my_actor_cell_id = [teammate['cellId'] for teammate in res['myTeam'] if teammate['summonerId'] == self.get_current_summoner_id()]
    print(f"My cell ID : {my_actor_cell_id[0]}")


    for action_groups in res["actions"]:
      for action in filter(lambda ac: (ac["actorCellId"] == my_actor_cell_id[0] and ac["isInProgress"] is True), action_groups):
        print(f"Action {action['type']}")
        
        data = {"championId": self.ban if action["type"] == 'ban' else self.picks[self.__current_pick_index]}

        if action["type"] == 'ban':
          code = self.__take_action(action_id=action["id"], data=data)
          print(f"Ban pick {code.status_code}")
          code = self.__lock_champion(action_id=action["id"], data=data)
          print(f"Ban lock {code.status_code}")
        elif action["type"] == 'pick':
          code = self.__take_action(action_id=action["id"], data=data)
          print(f"Pick pick {code.status_code}")
          code = self.__lock_champion(action_id=action["id"], data=data)
          print(f"Pick lock {code.status_code}")
          self.__current_pick_index += 1
      
  def start_process(self):
    print(f"process_started  PICK1: {self.picks[0]}, PICK2: {self.picks[1]}, BAN: {self.ban}")

    while True:
      if self.kill_thread is True:
        self.kill_thread = False
        print("KILLED THREAD")
        return

      res = requests.get(f"https://127.0.0.1:{self.__PORT}/lol-gameflow/v1/gameflow-phase", auth=self.__auth, verify="riotgames.pem")

      if res.status_code != 200:
        continue
      
      current_phase = res.json()
      print(current_phase)

      if current_phase == MATCH_FOUND_PHASE:
        self.__current_pick_index = 0
        self.__accept_queue()
        continue

      if current_phase == CHAMP_SELECT_PHASE:
        # print("CHAMP SELECT")
        self.__champ_select()
        continue


  def assure_game_folder(self):
    data = utils.read_json_from_file("userdata.json")

    while data["GAME_FOLDER"] == '':
      input_path = self.__view.prompt_game_folder()
      try:
        utils.save_json_to_file("userdata.json", {'GAME_FOLDER': input_path})
        data = utils.read_json_from_file("userdata.json")
      except TypeError:
        pass

  def __parse_lockfile(self):
    self.saved_user_file = utils.read_json_from_file("userdata.json")

    # Check if the lockfile exists (if client is running)
    while not os.path.exists(f'{self.saved_user_file["GAME_FOLDER"]}\\lockfile'):
      self.__view.error_window("LEAGUE CLIENT NOT OPEN")
      self.saved_user_file = utils.read_json_from_file("userdata.json")
    
    # Read from lockfile
    with open(f'{self.saved_user_file["GAME_FOLDER"]}\\lockfile', 'r') as lockfile:
      content = lockfile.read()
    
    content = content.split(':')
    self.PORT = content[2]
    self.PASSWORD = content[3]

  def __connect(self):
    self.__view.summoner_name.set(self.get_current_summoner_name())

    current_level_percentage = self.get_current_lvl_percentage()
    self.__view.level_percentage.set(f"{current_level_percentage[0]}% => {current_level_percentage[1] + 1}")

  def connect_to_LCU(self):
    """Connect to the LCU API after checking the required info is available (path to the game files)
    """
    self.assure_game_folder()
    self.__parse_lockfile()

    self.__connect()

    print("ONLINE!")


  @property
  def PORT(self):
    return self.__PORT

  @PORT.setter
  def PORT(self, value):
    self.__PORT = value
    self.__BASE_URL = f"https://127.0.0.1:{self.__PORT}"

  @property
  def PASSWORD(self):
    return self.__PASSWORD
  
  @PASSWORD.setter
  def PASSWORD(self, value):
    self.__PASSWORD = value
    self.__auth = HTTPBasicAuth('riot', self.__PASSWORD)

  def __make_request(self, method, path, data=''):
    session = requests.session()
    fn = getattr(session, method)

    resp = fn(f"{self.__BASE_URL}{path}", verify="riotgames.pem", auth=self.__auth)
    return resp

  def get_current_summoner_id(self):
    res = requests.get(f"https://127.0.0.1:{self.__PORT}/lol-login/v1/session", auth=self.__auth, verify="riotgames.pem")
    return res.json()["summonerId"]

  def get_current_summoner_name(self):
    res = requests.get(f"https://127.0.0.1:{self.__PORT}/lol-summoner/v1/current-summoner", auth=self.__auth, verify="riotgames.pem")
    print(res.json())
    return res.json()["displayName"]

  def get_current_lvl_percentage(self):
    res = requests.get(f"https://127.0.0.1:{self.__PORT}/lol-summoner/v1/current-summoner", auth=self.__auth, verify="riotgames.pem")
    return (res.json()["percentCompleteForNextLevel"], res.json()["summonerLevel"])

  

