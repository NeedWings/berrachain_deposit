from eth_abi import encode

from modules.utils.account import Account
from modules.utils.utils import req_post, get_random_value, get_random_value_int
from modules.config import SETTINGS
from modules.utils.Logger import logger
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.token_stor import eth

class Berrachain:

    def __init__(self, account: Account):
        self.account = account
        self.proxies = account.proxies

    def register(self):
        resp  = req_post("https://points.stakestone.io/bera/gWithCode", json={"address": self.account.address.lower(), "refCode":SETTINGS["RefCode"]}, proxies=self.proxies)
    
    def deposit(self):
        mode = SETTINGS["deposit mode"]
        eth_balance = self.account.get_balance(eth)[1]
        if mode == "percent":
            deposit_amount = eth_balance * get_random_value(SETTINGS["deposit amount"])
        elif mode == "eth":
            deposit_amount = get_random_value(SETTINGS["deposit amount"])
        else:
            logger.error(f"[{self.account.address}] selected wrong deposit mode: {mode}. can only use eth or percent")
            return
        deposit_amount = max(deposit_amount, eth_balance-0.001)

        logger.info(f"[{self.account.address}] will deposit {deposit_amount} ETH")
        self.register()
        w3 = self.account.get_w3("ethereum")
        txn_data_handler = TxnDataHandler(self.account, "ethereum", w3=w3)

        txn = txn_data_handler.get_txn_data(int(deposit_amount*1e18))

        txn["to"] = "0x2aCA0C7ED4d5EB4a2116A3bc060A2F264a343357"
        txn["data"] = "0x2d2da806" + encode(["address"], [self.account.address]).hex()

        self.account.send_txn(txn, "ethereum")