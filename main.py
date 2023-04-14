import json
import time

import requests
from requests.auth import HTTPBasicAuth

from app import App
from controller import Controller
from view import View

# res = requests.get(f"https://127.0.0.1:{PORT}/lol-champ-select/v1/session", auth=auth, verify="riotgames.pem")
# res = json.loads(res.text)

# with open('data.json', 'w') as outfile:
#   json.dump(res, outfile, indent=4, sort_keys=True)

# print(f"Active account : {get_current_summonerid()}")

# def look_for_match_found():
#   while True:
#     res = requests.get(f"https://127.0.0.1:{PORT}/lol-matchmaking/v1/ready-check", auth=auth, verify="riotgames.pem")
#     res = json.loads(res.text)

#     if res["state"] == "InProgress":
#       requests.post(f"https://127.0.0.1:{PORT}/lol-matchmaking/v1/ready-check/accept", auth=auth, verify="riotgames.pem")
#       print("ACCEPT")
#     else: print("Not Found")
  
#     time.sleep(1)

#  22  122  78
# C:\\Riot Games\\League of Legends

# res = requests.patch(f"https://127.0.0.1:{PORT}/lol-champ-select/v1/session/actions/1", data={"championId":22}, auth=auth, verify="riotgames.pem")
# res = json.loads(res.text)

# with open('data.json', 'w') as outfile:
#   json.dump(res, outfile, indent=4, sort_keys=True)

def pick_champion():
  pass

if __name__ == '__main__':
  app = App()
  app.mainloop()
  print("ok")

