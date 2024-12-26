from abc import ABC, abstractmethod
import random

from modules.base_classes.base_account import BaseAccount
from modules.utils.token import Token
from modules.utils.Logger import logger
from modules.config import SETTINGS

class BaseDex(ABC):
    name = None
    supported_tokens = []
    supported_liq_tokens = []
    lpts = []
    contract_address_lp = None
    def __init__(self) -> None:
        new_supported_tokens = []
        new_supported_liq_tokens = []
        selected_tokens = SETTINGS["SwapsTokens"]
        for token in self.supported_tokens:
            if token in selected_tokens or ("WETH" in selected_tokens and token == "ETH"):
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens
        selected_tokens = SETTINGS["LiqTokens"]
        for token in self.supported_liq_tokens:
            if token in selected_tokens or ("WETH" in selected_tokens and token == "ETH"):
                new_supported_liq_tokens.append(token)
        self.supported_liq_tokens = new_supported_liq_tokens

    @abstractmethod
    def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseAccount, full: bool = False):
        pass

    @abstractmethod
    def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseAccount):
        pass

    @abstractmethod
    def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseAccount):
        pass

    def get_pair_for_token(self, token: str):
        for i in range(20):
            pair = random.choice(self.supported_tokens)
            if token != pair:
                return pair
        logger.error("Can't find pair for token")
        return -5
    
    def get_liq_pair_for_token(self, token: str):
        for i in range(20):
            pair = random.choice(self.supported_liq_tokens)
            if token != pair:
                return pair
        logger.error("Can't find pair for token")
        return -5
    
class BaseLend(ABC):
    contract_address = None
    name = None
    supported_tokens = []
    supported_tokens_for_borrow = []
    lend_tokens = []

    def __init__(self) -> None:
        new_supported_tokens = []
        selected_tokens = SETTINGS["Lend Tokens"]
        for token in self.supported_tokens:
            if token in selected_tokens or ("WETH" in selected_tokens and token == "ETH"):
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

        new_supported_tokens_for_borrow = []
        for token in self.supported_tokens_for_borrow:
            if token in selected_tokens or ("WETH" in selected_tokens and token == "ETH"):
                new_supported_tokens_for_borrow.append(token)
        self.supported_tokens_for_borrow = new_supported_tokens_for_borrow

    @abstractmethod
    def create_txn_for_adding_token(self, token: Token, amount: float, sender: BaseAccount):
        pass

    @abstractmethod
    def create_txn_for_removing_token(self, token: Token, sender: BaseAccount):
        pass


