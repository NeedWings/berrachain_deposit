from time import sleep
from random import shuffle, choice

from modules.base_classes.base_account import BaseAccount


class OwnTasks:
    delay = 0
    modes = {
        "standart": 1,
        "invert": -1
    }

    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def main(self, main_router, tasks, mode = None, delay = 0, gas_lock = None):
        if delay != 0:
            part = delay/100
            for _ in range(100):
                sleep(part)
                while gas_lock.is_set():
                    sleep(20)
        
        if isinstance(mode, int):
            mode = 0-mode
        else:
            mode = self.modes[mode]

        if mode == 1:
            shuffle(tasks)
            for task in tasks:
                if type(task) == type([1,2,3]):
                    self.main(main_router, tasks = task, mode = mode, delay=0, gas_lock=gas_lock)
                elif type(task) == type("1,2,3"):
                    to_do = int(choice(task.split(",")))
                    main_router.delay = 0
                    main_router.task_number = to_do
                    main_router.start()
                else:
                    main_router.delay = 0
                    main_router.task_number = task
                    main_router.start()
        elif mode == -1:
            for task in tasks:
                if type(task) == type([1,2,3]):
                    shuffle(task)
                    self.main(main_router, tasks = task, mode=mode)
                elif type(task) == type("1,2,3"):
                    to_do = int(choice(task.split(",")))
                    main_router.delay = 0
                    main_router.task_number = to_do
                    main_router.start()
                else:
                    print(task)
                    main_router.delay = 0
                    main_router.task_number = task
                    main_router.start()