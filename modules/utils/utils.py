import random
import time
import string
from threading import Event
import json

import requests
from web3 import Web3

from modules.utils.Logger import logger, console_log
from modules.config import SETTINGS_PATH, SETTINGS

def get_random_value_int(param):
    return random.randint(int(param[0]), int(param[1]))

def get_random_value(param):
    return random.uniform(float(param[0]), float(param[1]))

def change_proxies_ip(proxies: dict, change_url: str):
    def __get_current_ip__():
        while True:
            try:
                return requests.get("https://api.ipify.org?format=json", proxies=proxies).json()["ip"]
            except Exception as error:
                console_log.error(f'Failed to get ip: {error}')
                time.sleep(5)
    old_ip = __get_current_ip__()
    console_log.info(f'Old ip address: {old_ip}')
    while old_ip == __get_current_ip__():
        try:
            response = requests.post(change_url).json()
            console_log.info(f'Change ip response: {response}')
        except Exception as error:
            console_log.error(f'Failed to change ip: {error}')
        
        time.sleep(5)
    
    console_log.info(f'New ip address: {__get_current_ip__()}')


def sleeping_sync(address, error = False):
    task_sleep = SETTINGS["Task Sleep"]
    error_sleeping = SETTINGS["Error Sleep"]
    if error:
        rand_time = get_random_value_int(error_sleeping)
    else:
        rand_time = get_random_value_int(task_sleep)
    logger.info(f'[{address}] sleeping {rand_time} s')
    time.sleep(rand_time)

def get_pair_for_address_from_file(filename: str, address: str):
    address = address.lower()
    with open(f"{SETTINGS_PATH}{filename}", "r") as f:
        buff = f.read().lower().split("\n")
    pairs_raw = []
    for i in buff:
        if ";" in i:
            pairs_raw.append(i)

    for pair in pairs_raw:
        if pair.split(";")[0] == address:
            return Web3.to_checksum_address(pair.split(";")[1])
    return None


def req_post(url: str, return_on_fail=False, **kwargs):
    while True:
        try:
            resp = requests.post(url, **kwargs)
            if resp.status_code == 200:
                return resp.json()
            else:
                console_log.error("Bad status code, will try again")
                pass
        except Exception as error:
            console_log.error(f"Requests error: {error}")
        if return_on_fail:
            return None
        time.sleep(get_random_value(SETTINGS["Error Sleep"]))


def req(url: str, return_on_fail=False, **kwargs):
    while True:
        try:
            resp = requests.get(url, **kwargs)
            if resp.status_code == 200:
                return resp.json()
            else:
            
                console_log.error("Bad status code, will try again")
                pass
        except Exception as error:
            console_log.error(f"Requests error: {error}")
        if return_on_fail:
            return None
        time.sleep(get_random_value(SETTINGS["Error Sleep"]))

def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase + "1234567890"
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def decimal_to_int(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def base36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
 
    base36 = ''
    sign = ''
 
    if number < 0:
        sign = '-'
        number = -number
 
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36


def encode_packed(types: list, values: list):
    result = ''
    assert len(types) == len(values)
    for i in range(len(values)):
        _type = types[i]
        value = values[i]
        if _type in ["uint256", "uint8", "uint32", "uint64", "uint128"]:
            assert isinstance(value, int)
            result += hex(value)[2::].rjust(len(hex(value)[2::]) + len(hex(value)[2::])%2, "0")
        elif _type == "address":
            assert isinstance(value, str)
            result += value.lower()[2::]
        elif _type == "string":
            assert isinstance(value, str)
            result += value.encode().hex()
        elif _type == "bytes":
            assert isinstance(value, bytes) 
            result += value.hex()
        else:
            raise Exception(f"bad type: {_type}")
    return bytes.fromhex(result)
