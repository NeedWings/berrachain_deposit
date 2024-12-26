from abc import ABC, abstractmethod
from web3 import Web3

class BaseAccount(ABC):
    w3 = {}
    proxies = None
    proxy: str
    active: bool
    private_key: str
    address: str

    def __str__(self) -> str:
        return f"private key: {self.private_key}\naddress: {self.address}\nis_active: {self.active}\nproxy: {self.proxies}\t{self.proxy}\nw3: {self.w3}"

    def is_active(self):
        return self.active

    @abstractmethod
    def set_proxy(self, proxy):
        pass

    @abstractmethod
    def setup_w3(self, proxy=None):
        pass

    def get_w3(self, net_name) -> Web3:
        return self.w3[net_name]

    def get_address(self):
        return self.address
    
    @abstractmethod
    def get_balance(self, token):
        pass
    
    @abstractmethod
    def wait_for_better_eth_gwei(self):
        pass

    @abstractmethod
    def send_without_wait(self, txn, net):
        pass
        
    @abstractmethod
    def send_txn(self, txn, net):
        pass
    
    @abstractmethod
    def wait_until_txn_finished(self, hash, net, max_time = 500):
        pass