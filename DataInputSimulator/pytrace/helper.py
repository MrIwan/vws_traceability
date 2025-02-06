import requests
import json
import base64
import time
import re

from typing import List

from basyx.aas import model
import basyx.aas.adapter.json

import basyx

from .global_variables import server_url

# urls 
basyx_submodell_url = server_url + ':8081/submodels'
basyx_shells_url = server_url + ':8081/shells'

def encode_string_to_base64(input_string: str) -> str:
    """
    Encodiert einen String zu base64.

    Args:
        input_string (str): Der zu encodierende String.

    Returns:
        str: Der base64-encodierte String.
    """
    input_bytes = input_string.encode('utf-8')
    encoded_bytes = base64.b64encode(input_bytes)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


def aas_to_json(aas) -> dict:
    # aas.update()
    aas_json_str = json.dumps(aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    return json.loads(aas_json_str)


def json_to_aas(json_dict) -> model.AssetAdministrationShell:
    json_dict = json.dumps(json_dict)
    aas = json.loads(json_dict, cls=basyx.aas.adapter.json.AASFromJsonDecoder)
    return aas


def send_http_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return the response content as JSON
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    

def get_all_shells() -> List[dict]:
    return send_http_request(basyx_shells_url)['result']

def get_sm(url):
    sm_json = send_http_request(f'{basyx_submodell_url}/{encode_string_to_base64(url)}?level=deep&extent=withoutBlobValue')
    return json_to_aas(sm_json)

def get_product_types() -> List[dict]:
    ret: List[dict] = []

    # Regulärer Ausdruck der ein Match zu allen Material Typen seien soll
    pattern = r"http:\/\/coroplast\.com\/mat\/[a-zA-Z0-9]+\/aas"
    
    for aas in get_all_shells():
        if re.fullmatch(pattern, aas['id']):
            ret.append(
                aas
            )

    return ret

    
def send_http_post_request(vws_dict: dict, url: str = basyx_shells_url, headers: dict = {"Content-Type": "application/json"}):
    """
    Sends an HTTP POST request to the specified URL with the given data and headers.

    Args:
        vws_dict (dict): The data to be sent in the body of the POST request, formatted as a dictionary.
        url (str, optional): The URL to which the POST request is sent. Defaults to basyx_shells_url.
        headers (dict, optional): The headers to include in the request. Defaults to {"Content-Type": "application/json"}.

    Returns:
        dict or None: The JSON response from the server if the request is successful, 
                       or None if an error occurs during the request.
    
    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.
    """
    try:
        response = requests.post(url, headers=headers, data=json.dumps(vws_dict))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    
def send_http_put_request(vws_dict: dict, url: str, headers: dict = {"Content-Type": "application/json", "accept": "application/json"}):
    """
    Sendet eine HTTP PUT-Anfrage mit den gegebenen Daten und Headern an die angegebene URL.

    :param vws_dict: Das Dictionary, das in der PUT-Anfrage gesendet werden soll.
    :param url: Die URL, an die die PUT-Anfrage gesendet werden soll.
    :param headers: Die Header der PUT-Anfrage.
    """
    try:
        response = requests.put(url, headers=headers, data=json.dumps(vws_dict))
        response.raise_for_status()  # Überprüft, ob die Anfrage erfolgreich war
        if response.content:  # Überprüft, ob die Antwort Inhalt hat
            return response.json()
        else:
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def post_sm(sm: model.Submodel, update: bool = False) -> bool:
    sm_dict = aas_to_json(sm)
    url = basyx_submodell_url
    if update:
        url = f'{url}/{encode_string_to_base64(sm.id)}'
        send_http_put_request(sm_dict, url)
    else:
        send_http_post_request(sm_dict, url)


def post_aas(aas: model.AssetAdministrationShell) -> bool:
    aas_dict = aas_to_json(aas)
    send_http_post_request(aas_dict, 'http://localhost:8081/shells')

def post_aas_with_sms(aas: model.AssetAdministrationShell, obj_store: model.DictObjectStore) -> bool:
    # Über die Submodelle iterieren und deren Inhalt anzeigen
    for sm in aas.submodel:
        sm_dict = aas_to_json(sm.resolve(obj_store))
        send_http_post_request(sm_dict, 'http://localhost:8081/submodels')

    aas_dict = aas_to_json(aas)
    send_http_post_request(aas_dict,'http://localhost:8081/shells')

def create_model_reference_from_global_id(global_id: str) -> model.ModelReference:
    key = model.Key(
        type_=model.KeyTypes.ASSET_ADMINISTRATION_SHELL, value=global_id
    )
    return model.ModelReference(key=(key,), type_=model.ModelReference)


def create_chargen_id() -> str:
    return str(time.time()).replace('.', '_')