import cProfile

import requests

from app import App

if __name__ == '__main__':

  # r = requests.patch(f"https://ddragon.leagueoflegends.com/cdn/13.7.1/data/en_US/champion/Aatrox.json")
  # print(f"{type(r.status_code)} =>  {r.status_code}")

  app = App()
  app.mainloop()
  
  
