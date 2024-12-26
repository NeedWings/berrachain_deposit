import json
from time import sleep
from random import shuffle, choice, randint
import multiprocessing
from multiprocessing import Event

from termcolor import colored
import inquirer
from inquirer.themes import load_theme_from_dict as loadth
from loguru import logger
from web3 import Web3

from modules.utils.starter import Starter
from modules.utils.utils import change_proxies_ip, get_random_value_int
from modules.tasks_handlers.main_router import MainRouter
from modules.utils.account import Account, ethAccount
from modules.config import autosoft, subs_text, SETTINGS_PATH, SETTINGS, RPC_LIST


def get_action() -> str:
    theme = {
        "Question": {
            "brackets_color": "bright_yellow"
        },
        "List": {
            "selection_color": "bright_blue"
        }
    }

    question = [
        inquirer.List(
        "action",
        message=colored("Choose soft work task", 'light_yellow'),
        choices=[
            "Deposit"
        ],
    )
    ]
    action = inquirer.prompt(question, theme=loadth(theme))['action']
    return action

def gas_locker(gas_lock, ender):
    while True:
        w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST["ethereum"])))
        if ender.is_set():
            return  
        f = open(f"{SETTINGS_PATH}settings.json", "r")
        SETTINGS = json.loads(f.read())
        f.close()
        max_gas = Web3.to_wei(SETTINGS["MaxEthGwei"], 'gwei')
        try:
            gas_price = w3.eth.gas_price
            if gas_price > max_gas:
                h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                gas_lock.set()
            else:
                gas_lock.clear()
            
        except Exception as error:
            pass
        sleep(randint(10, 20))


def main():
    starter = Starter()
    print(autosoft)
    print("\n")
    action = get_action()
    if 0:
        pass
    else:
        gas_lock = Event()
        ender = Event()

        with open(f"{SETTINGS_PATH}private_keys.txt", "r") as f:
            keys = f.read().split("\n")
            counter = len(keys)
        print(f"Soft found {counter} keys to work")
        accounts = []
        shuffle(keys)
        if SETTINGS["mobileProxy"] != "":
            mobile_proxy = "http://" + SETTINGS["mobileProxy"]
            proxy = {
                "http": mobile_proxy,
                "https": mobile_proxy
            }
            logger.info(f"Will use mobile proxy: {mobile_proxy}")
            for account in keys:
                change_proxies_ip(proxy, SETTINGS["ChangeUrl"])
                try:
                    MainRouter(Account(account, mobile_proxy), task_number=1).start()
                except Exception as e:
                    logger.error(f"got error: {e}")
                sleep(get_random_value_int(SETTINGS["Thread Runner Sleep"]))
        elif SETTINGS["UseProxies"]:
            with open(f"{SETTINGS_PATH}proxies.txt", "r") as f:
                proxies_raw = f.read().split("\n")
            proxies = {}
            for proxy in proxies_raw:
                if proxy == "":
                    continue
                print(f'{proxy.split("@")[2]} connected to {"http://" + proxy.split("@")[0] + "@" + proxy.split("@")[1]}')
                proxies[proxy.split("@")[2].lower()] = "http://" + proxy.split("@")[0] + "@" + proxy.split("@")[1]
            for key in keys:
                accounts.append(Account(key, proxy=proxies[str(ethAccount.from_key(key).address).lower()]))
            
        else:
            for key in keys:
                accounts.append(Account(key))
        try:
            th = starter.start(action, gas_lock, accounts, ender)
            gas_locker(gas_lock, ender)
        except KeyboardInterrupt:
            th.kill()
            
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
    input("Soft successfully end work. Press Enter to exit")


