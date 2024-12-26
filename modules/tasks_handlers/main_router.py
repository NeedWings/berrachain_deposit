from time import sleep
from random import choice
from threading import Event

from modules.tasks_handlers.own_tasks_router import OwnTasks
from modules.other.berrachain import Berrachain
from modules.utils.account import Account
from modules.config import SETTINGS


class MainRouter:
    
    def __init__(self, account: Account, task_number) -> None:
        self.account = account
        self.account.setup_w3(self.account.proxy)
        self.task_number = task_number

    def start(self):
        if self.task_number == 1:
            berra = Berrachain(self.account)
            berra.deposit()
        elif self.task_number == 0:
            own_tasks_router = OwnTasks(self.account)
            own_tasks_router.main(self)