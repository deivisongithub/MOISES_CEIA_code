import os

KEY_ORCHES = "74240dc9-407d-44c7-83c4-4b8a489755d9"

# Set the directory path
directory = input('input directory: ')    #'D:\Deivison\music_vocal'
output_path = input('output directory: ') #'D:\Deivison\music_vocal_output'

# Get all the files in the directory
files = os.listdir(directory)

# Filter the files to only include those with a .m4a extension

mp4_files = [f for f in files if f.endswith('.m4a')] # <- in case of another extension, change here.

print(mp4_files)

import dropbox
import requests
import json
from pathlib import Path
import yaml

DROPBOX_PATH = "dropbox.yaml" # credenciais em .yaml de um dropbox para fazer uploads os inputs
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


def generate(FILE_NAME, LINK, KEY_ORCHES):

    # POST
    print("Url_orches")
    url_orches = "https://developer-api.moises.ai/api/job"

    headers_orches = {
        "Authorization": KEY_ORCHES,
        "Content-Type": "application/json"
    }
    payload_orches = {
        "name": FILE_NAME,
        "workflow": "remover_instrumental_123", #remover_instrumental_123 é meu workflow na API da moises
        "params": {"inputUrl": LINK}
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


from urllib import request

for i in mp4_files:
    filename = os.path.splitext(i)[0]
    print(filename)
    
    url, path = dropbox_generator(directory+"/"+i)
    print(url)
    
    json_file = generate(filename, url, KEY_ORCHES)
    print(json_file)
    
    delete_dropbox(path)
    
    #downloading and storing isolated voice
    
    file_url = json_file['Output 1']
    file = output_path + '/' + filename + '.wav'
    request.urlretrieve(file_url , file )

