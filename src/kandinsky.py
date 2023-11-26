import json
import requests


class API:
    def __init__(self, api_key, secret_key):
        self.URL = "https://api-key.fusionbrain.ai/"
        self.AUTH_HEADERS = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        }

    def getModel(self):
        response = requests.get(self.URL + "key/api/v1/models", headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]["id"]

    def startGeneration(self, prompt, style):
        params = {
            "type": "GENERATE",
            "style": style,
            "numImages": 1,
            "width": 1024,
            "height": 1024,
            "generateParams": {
                "query": f"{prompt}"
            }
        }
        data = {
            "model_id": (None, self.getModel()),
            "params": (None, json.dumps(params), "application/json")
        }
        response = requests.post(self.URL + "key/api/v1/text2image/run", headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        self.request_id = data.get("uuid", None)

    def checkGeneration(self):
        if self.request_id is None:
            return False
        response = requests.get(self.URL + "key/api/v1/text2image/status/" + self.request_id, headers=self.AUTH_HEADERS)
        data = response.json()
        if data["status"] == "DONE":
            self.image = data["images"][0]
            return True
        return False

    def getPhoto(self):
        return self.image


def getStyles():
    data = requests.get("https://cdn.fusionbrain.ai/static/styles/api").json()
    return [elem["titleEn"] for elem in data]


def getStyleByTitle(title):
    data = requests.get("https://cdn.fusionbrain.ai/static/styles/api").json()
    for elem in data:
        if elem["titleEn"] == title:
            return elem["name"]
    return None
