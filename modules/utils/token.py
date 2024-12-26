from random import choice
from time import sleep

from web3 import Web3

from modules.config import RPC_LIST, ABI, NATIVE_TOKENS_SYMBOLS, NATIVE_WRAPPED_CONTRACTS, SETTINGS, ERC_721_ABI
from modules.utils.Logger import logger
from modules.utils.utils import sleeping_sync, get_random_value, get_random_value_int, req
from modules.utils.txn_data_handler import TxnDataHandler
from modules.base_classes.base_account import BaseAccount


class Token():
    def __init__(self, symbol, contract_address, decimals, net, stable = False) -> None:
        self.net_name = net
        self.decimals = decimals
        self.symbol = symbol
        self.contract_address = contract_address
        self.stable = stable


    def transfer(self, amount: int, to: str, sender: BaseAccount):
        w3 = sender.get_w3(self.net_name)
        contract = w3.eth.contract(self.contract_address, abi=ABI)
        txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
        while True:
            try:
                logger.info(f"[{sender.address}] going to transfer {amount/10**self.decimals} {self.symbol} to {to}")
                txn = contract.functions.transfer(to, amount).build_transaction(
                                    txn_data_handler.get_txn_data()
                                )
                sender.send_txn(txn, self.net_name)
                sleeping_sync(sender.address)
                return
            except Exception as e:
                logger.error(f"[{sender.address}] can't transfer {self.symbol}: {e}")
                sleeping_sync(sender.address, True)

                
    def balance_of(self, address, w3 = None, of_wrapped = False):
        if w3:
            self.w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))
        contract = w3.eth.contract(self.contract_address, abi=ABI)
        while True:
            try:
                balance = contract.functions.balanceOf(address).call()
                human_balance = balance/10**self.decimals
                return balance, human_balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                sleeping_sync(address, True)
    
    def get_approve_txn(self, sender: BaseAccount, spender, amount, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))
        contract = w3.eth.contract(self.contract_address, abi=ABI)
        for i in range(5):
            try:
                logger.info(f"[{sender.address}] going to approve {self.symbol}")
                txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
                txn = contract.functions.approve(spender, amount).build_transaction(
                                    txn_data_handler.get_txn_data()
                                )
                
                sender.send_txn(txn, self.net_name)
                t = get_random_value_int(SETTINGS["Approve Sleep"])
                logger.info(f"[{sender.get_address()}] sleeping {t} s")
                sleep(t)
                return None
            except Exception as e:
                logger.error(f"[{sender.address}] can't get approve txn: {e}")
                sleeping_sync(sender.address, True)
    
    def get_price(self):
        if self.stable:
            return 1
        elif self.symbol == "WSTETH":
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=wrapped-steth")
                if type(response) is dict:
                    return response["wrapped-steth"]["usd"]
                else:
                    print(f'Cant get response from binance, tring again...')
                    sleep(5)
        elif self.symbol == "ECP":
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=echodex-community-portion")
                if type(response) is dict:
                    return response["echodex-community-portion"]["usd"]
                else:
                    print(f'Cant get response from binance, tring again...')
                    sleep(5)
        elif self.symbol == "WRSETH":
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=wrapped-rseth")
                if type(response) is dict:
                    return response["wrapped-rseth"]["usd"]
                else:
                    print(f'Cant get response from binance, tring again...')
                    sleep(5)
        else:
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.binance.com/api/v3/ticker/price")
                if type(response) is list:
                    return __find__(self.symbol, response)
                else:
                    print(f'Cant get response from binance, tring again...')
                    sleep(5)

    def get_usd_value(self, amount):
        return self.get_price()*amount
    
    def get_total_supply(self, address, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))
        
        contract = w3.eth.contract(self.contract_address, abi=ABI)

        while True:
            try:
                return contract.functions.totalSupply().call()
            except Exception as e:
                logger.error(f"[{address}] can't get total supply of {self.symbol}: {e}")
                sleeping_sync(address, True)

        

class NativeToken(Token):
    def __init__(self, net) -> None:
        self.net_name = net
        self.decimals = 18
        self.symbol = NATIVE_TOKENS_SYMBOLS[net]
        self.contract_address = NATIVE_WRAPPED_CONTRACTS[net]
        self.abi = [{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": True,"internalType":"address","name":"guy","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"dst","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": True,"internalType":"address","name":"dst","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"},{"payable": True,"stateMutability":"payable","type":"fallback"},{"constant": True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"guy","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[],"name":"deposit","outputs":[],"payable": True,"stateMutability":"payable","type":"function"},{"constant": True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": False,"inputs":[{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable": False,"stateMutability":"nonpayable","type":"function"}]
        self.stable = False

    def balance_of(self, address, w3 = None, of_wrapped = False):
        if w3:
            w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        while True:
            try:
                if not of_wrapped:
                    balance = w3.eth.get_balance(address)
                    human_balance = balance/10**self.decimals
                    return balance, human_balance
                else:
                    balance = contract.functions.balanceOf(address).call()
                    human_balance = balance/10**self.decimals
                    return balance, human_balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                sleeping_sync(address, True)

    def create_unwrap_txn(self, sender, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))

        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
        
        amount = self.balance_of(sender.get_address(), w3=w3, of_wrapped=True)[0]
               
        if amount <= 1:
            return None
        logger.info(f"[{sender.address}] going to unwrap ETH")
        txn = contract.functions.withdraw(
            amount
        ).build_transaction(txn_data_handler.get_txn_data())
        return txn
    
    def create_wrap_txn(self, wei: bool, amount, sender, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))

        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)

        if not wei:
            amount = int(amount*10**self.decimals)

        txn = contract.functions.deposit().build_transaction(txn_data_handler.get_txn_data(amount))

        return txn

    def get_approve_txn(self, address, spender, amount, w3 = None):
        return None
    
    def get_approve_txn_wrapped(self, wei: bool, sender: BaseAccount, spender, amount, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        while True:
            try:
                logger.info(f"[{sender.address}] going to approve W{self.symbol}")
                if not wei:
                    amount = int(amount*10**self.decimals)

                txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
                txn = contract.functions.approve(spender, amount).build_transaction(
                                    txn_data_handler.get_txn_data()
                                )
                
                sender.send_txn(txn, self.net_name)

                t = get_random_value_int(SETTINGS["Approve Sleep"])
                logger.info(f"[{sender.get_address()}] sleeping {t} s")
                sleep(t)

                return None
            except Exception as e:
                logger.error(f"[{sender.address}] can't get approve txn: {e}")

class ERC721Token(Token):
    def __init__(self, symbol, contract_address, net) -> None:
        super().__init__(symbol, contract_address, 1, net, False)

    def get_price(self):
        raise Exception("can't get price of NFT")
    
    def get_usd_value(self, amount):
        raise Exception("can't get usd value of NFT")
    
    def balance_of(self, address, w3=None):
        if w3:
            self.w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))
        contract = w3.eth.contract(self.contract_address, abi=ABI)
        while True:
            try:
                balance = contract.functions.balanceOf(address).call()
                return balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                sleeping_sync(address, True)
    
    def get_approve_txn(self, sender: BaseAccount, spender, token_id, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST[self.net_name])))
        contract = w3.eth.contract(self.contract_address, abi=ERC_721_ABI)
        for i in range(5):
            try:
                logger.info(f"[{sender.address}] going to approve {self.symbol}")
                txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
                txn = contract.functions.approve(spender, token_id).build_transaction(
                                    txn_data_handler.get_txn_data()
                                )
                
                sender.send_txn(txn, self.net_name)
                t = get_random_value_int(SETTINGS["Approve Sleep"])
                logger.info(f"[{sender.get_address()}] sleeping {t} s")
                sleep(t)
                return None
            except Exception as e:
                logger.error(f"[{sender.address}] can't get approve txn: {e}")
                sleeping_sync(sender.address, True)


class AmbientV3Position(Token):
    
    def __init__(self, symbol: str, token1: str, token2: str, bid_tick: int, ask_tick: int, liq_amount: int, is_ambient: bool, opened: bool) -> None:
        self.token1 = token1
        self.token2 = token2
        self.opened = opened
        self.bid_tick = bid_tick
        self.ask_tick = ask_tick
        self.is_ambient = is_ambient
        self.liq_amount = liq_amount
        super().__init__(symbol, "0x123", 0, "scroll", False)

    def balance_of(self, address, w3=None, of_wrapped=False):
        if self.opened:
            return 0xfffffffff, 0xfffffffff
        else:
            return 0, 0
        
    def get_approve_txn(self, sender: BaseAccount, spender, amount, w3=None):
        return None
    
    def get_total_supply(self, address, w3=None):
        return None
    
    def get_usd_value(self, amount):
        return None
    
    def get_price(self):
        return None
    
