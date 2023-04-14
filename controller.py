import os

import requests
from requests.auth import HTTPBasicAuth

import utils
from view import View


class Controller:
  def __init__(self, view:View) -> None:
    # LCU API related stuff
    self.__BASE_URL = None
    self.__auth = None
    self.__PORT = None
    self.__PASSWORD = None

    self.summoner_name = ''
    self.saved_user_file = None



    self.__view = view

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
    while not os.path.exists(f'{self.saved_user_file["GAME_FOLDER"]}\\lockfile'):
      self.__view.error_window("LEAGUE CLIENT NOT OPEN")
      self.saved_user_file = utils.read_json_from_file("userdata.json")
    

    with open(f'{self.saved_user_file["GAME_FOLDER"]}\\lockfile', 'r') as lockfile:
      content = lockfile.read()
    
    content = content.split(':')
    self.PORT = content[2]
    self.PASSWORD = content[3]


  def __connect(self):
    self.__view.summoner_name.set(self.get_current_summoner_name())

  def connect_to_LCU(self):
    """Connect to the LCU API after checking the required info is available (path to the game files)
    """
    # self.saved_user_file = self.assure_game_folder()
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

  def get_current_summoner_name(self):
    res = requests.get(f"https://127.0.0.1:{self.__PORT}/lol-summoner/v1/current-summoner", auth=self.__auth, verify="riotgames.pem")
    return res.json()["displayName"]

  

