import os

KEY_ORCHES = "74240dc9-407d-44c7-83c4-4b8a489755d9"

# Set the directory path

voice_path = input('voice directory: ') #'D:\Deivison\music_vocal_output'
background_path = input('background directory: ') #'D:\Deivison\music_vocal_output_background'
output_path = input('output directory: ')

import dropbox
import requests
import json
from pathlib import Path
import yaml

DROPBOX_PATH = "dropbox.yaml" # caminho para as credenciais em .yaml de um dropbox para fazer uploads os inputs
class UploadData:
    def __init__(self, access_token):
        self.dbx = dropbox.Dropbox(oauth2_access_token=access_token["acess_token"], app_key =access_token["app_key"], app_secret = access_token["app_secret"], oauth2_refresh_token = access_token["refresh_token"])
    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        print("Uploading file...")
        with open(file_from, 'rb') as f:
            self.dbx.files_upload(f.read(), file_to)
    def return_link(self, file_to):
        """
            return dropbox link
        """
        print("Generate Link...")
        response =  self.dbx.files_get_temporary_link(file_to)
        
        
        return str(response.link), str(response.metadata.path_display)
    
    def remove(self, path):
        return self.dbx.files_delete_v2(path)
        
def config_dropbox():
    # Abre o arquivo YAML
    with open(DROPBOX_PATH, 'r') as stream:
        try:
            # Carrega o conteúdo do arquivo como um dicionário Python
            data = yaml.safe_load(stream)
            return data
        except yaml.YAMLError as exc:
            print(exc)
            return None
    
def dropbox_generator(file_from):
    try:
        access_token = config_dropbox()
        transferData = UploadData(access_token)
        name_to =Path(file_from).name
        file_to = f'/song/{name_to}'  # The full path to upload the file to, including the file name
        # API v2
        transferData.upload_file(file_from, file_to)
        # Return link
        url , path = transferData.return_link(file_to)
        # Return link
        return url,path
    except Exception as err:
        print("Erro Dropbox", err)
        print(err)
        return "erro"
    
def delete_dropbox(path):
    print("Deleting...")
    try:
        access_token = config_dropbox()
        up = UploadData(access_token)
        return up.remove(path)
    except Exception as err:
        print("Erro Dropbox", err)
        print(err)
        return "erro"


def generate(FILE_NAME, LINK,LINK2, KEY_ORCHES):

    # POST
    print("Url_orches")
    url_orches = "https://developer-api.moises.ai/api/job"

    headers_orches = {
        "Authorization": KEY_ORCHES,
        "Content-Type": "application/json"
    }
    payload_orches = {
        "name": FILE_NAME,
        "workflow": "mixer_instrumental_voice", #"mixer_instrumental_voice" é meu workflow na API da moises
        "params": {"inputUrl": LINK,
                   "inputUrl2": LINK2
                   }
    }
    print("We are going..")
    print(headers_orches)
    print(payload_orches)
    while(True):
        print('Loading Post...')
        try:
            response_orches = requests.request(
                "POST", url_orches, json=payload_orches, headers=headers_orches)
            print(response_orches.status_code)
            if response_orches.status_code == 200:
                id_orches = response_orches.json()["id"]
                print('Post Loaded. IDs:', id_orches)
                break
        except:
            time.sleep(10)
            continue

    # GET
    url_orches = f"https://developer-api.moises.ai/api/job/{id_orches}"

    headers_orches = {"Authorization": KEY_ORCHES}

    while(True):
        response_orches = requests.request(
            "GET", url_orches, headers=headers_orches).json()

        print("Loading...", end="\r")
        try:
            if (response_orches['status'] == "SUCCEEDED"):
                result = response_orches['result']
                # results = response_orches['result']['key']
                print("Result Loaded")
                final_json = result

                print('Orchestrator Done!')
                #with open(f"{output_path}/{FILE_NAME}_vocal.json", 'w') as file:
                #    json.dump(final_json, file)
                return final_json

        except:
            time.sleep(10)
            continue

import time
import requests


def OrchestratorProcessing(LINK, LINK2):
    FILE_NAME = "testemixer"
    KEY = "74240dc9-407d-44c7-83c4-4b8a489755d9"

    url = "https://developer-api.moises.ai/api/job"

    headers = {
        "Authorization": KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "name": FILE_NAME,
        "workflow": "mixer_instrumental_voice",
        "params": {"inputUrl": LINK,
                   "inputUrl2": LINK2
                   }
    }

    while(True):
        try:
            response_orches_get = requests.request(
                "POST", url, json=payload, headers=headers)
            if response_orches_get.status_code == 200:
                id = response_orches_get.json()["id"]
                break
        except:
            time.sleep(1)
            continue

    url_get = f"https://developer-api.moises.ai/api/job/{id}"
    headers_get = {"Authorization": KEY}

    while(True):
        response_orches_get = requests.request(
            "GET", url_get, headers=headers_get).json()
        try:
            print(response_orches_get)
            if response_orches_get['status'] == "SUCCEEDED":
                response = response_orches_get['result']['Output 1']

                return response
        except:
            time.sleep(1)
            continue

from urllib import request

filename = os.path.splitext(voice_path)[0]
filename = filename.split('/')[-1]
print(filename)

url, path = dropbox_generator(voice_path)
print(url)

url2, path2 = dropbox_generator(background_path)
print(url2)

json_file = OrchestratorProcessing(url, url2)
print(json_file)

delete_dropbox(path)
delete_dropbox(path2)

#downloading and storing isolated voice

file_url = json_file

file = output_path + '/' + filename + '.wav'

request.urlretrieve(file_url , file )