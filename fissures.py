import requests
import json
from bs4 import BeautifulSoup

class Fissures:
    def __init__(self):
        self._url = "http://content.warframe.com/dynamic/worldState.php"
        self._response = requests.get(self._url)
        self.json = self._response.json()
