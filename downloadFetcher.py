# downloadFetcher.py -- Downloads selected binary artifacts from
# AppDynamics site.
#
# This requires script caller export APPD_NAME and APPD_PASSWORD
# environment variables with access rights to pull down the
# relevant artifacts from AppD's download website.
#
# This is a basic "proof of concept" script that performs only
# light error checking; not all edge cases were considered.
# The overall process is divided into 5 steps:
#
# 1. retrieve username/password from environment variables
# 2. request oauth token from AppD website
# 3. retrieve list of current binary artifacts from AppD website
# 4. loop through artifact list looking for desired artifacts
# 5. download & save to local disk desired artifacts
#

import hashlib
import json
import requests
import os


# STEP 1. retrieve username/password from environment variables

username = os.getenv('APPD_NAME')
password = os.getenv('APPD_PASSWORD')
# TODO: validate username/password look basically valid (not empty)


# STEP 2. request oauth token from AppD website

oauth_url = "https://identity.msrv.saas.appdynamics.com/v2.0/oauth/token"
oauth_data = {
    "username": username, 
    "password": password, 
    "scopes": ["download"]
    }
oauth_response = requests.post(oauth_url, json=oauth_data)
status = oauth_response.status_code
# TODO: Validate 200 status_code; else, abort with error message
tokens = json.loads(oauth_response.text)
print(status, tokens)
creds = {"Authorization": "Bearer " + tokens['access_token']}
print("Token status code:", status)


# STEP 3. retrieve list of current binary artifacts from AppD website
manifest_url = "https://download.appdynamics.com/download/downloadfilelatest/"
manifest_response = requests.get(manifest_url)
# TODO: Validate 200 status_code; else, abort with error message
#print(manifest_response.text)
manifest_data = json.loads(manifest_response.text)


# STEP 4. loop through artifact list looking for desired artifacts
for artifact in manifest_data:
    filetype = artifact['filetype']
    os = artifact['os']
    bit = artifact['bit']
    title = artifact['title']
    description = artifact['description']
    download_path = artifact['download_path']
    filename = artifact['filename']
    version = artifact['version']
    sha256_checksum = artifact['sha256_checksum']


# STEP 5. download & save to local disk desired artifacts
    java_agents = {"java-jdk8", "ibm-jvm", "sun-jvm"}
    if filetype in java_agents:
        print(os, bit, version, filename, sha256_checksum, download_path)
        download_response = requests.get(download_path, headers=creds, stream=True)
        f = open('/tmp/' + filename, 'wb')
        sha256_hash = hashlib.sha256()
        for chunk in download_response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                sha256_hash.update(chunk)
        f.close()
        print("Actual sha256:", sha256_hash.hexdigest())


# vim: expandtab autoindent ts=4
