import json
import traceback
from threading import Thread
from multiprocessing import Event
import multiprocessing

import os
import sys

from modules.config import SETTINGS_PATH, SETTINGS
from modules.utils.account import Account
from modules.utils.utils import get_random_value_int
from modules.tasks_handlers.main_router import MainRouter
from modules.tasks_handlers.own_tasks_router import OwnTasks


if sys.platform.startswith('win'):

    import multiprocessing.popen_spawn_win32 as forking
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    class Process(multiprocessing.Process):
        if sys.platform.startswith('win'):
            _Popen = _Popen
else:
    class Process(multiprocessing.Process):
        pass




class Starter:
    
    task_numbers = {
        "Deposit": 1,
    }

    running_threads: Process = None

    def run_tasks(self, own_tasks, mode, selected_accounts, gas_lock, ender):
        thread_runner_sleep = SETTINGS["Thread Runner Sleep"]
        tasks = []
        delay = 0
        for i in range(len(selected_accounts)):
            main_router = MainRouter(selected_accounts[i], 0)
            own_tasks_router = OwnTasks(selected_accounts[i])
            tasks.append(Thread(target=own_tasks_router.main, args=[main_router, own_tasks.copy(), mode, delay, gas_lock]))
            delay += get_random_value_int(thread_runner_sleep)

        for i in tasks:
            i.start()

        for i in tasks:
            i.join()

        ender.set()
        

    def start(self, module, gas_lock, accounts, ender):
        is_own_tasks = module == "Own Tasks"
        if is_own_tasks:
            own_tasks = SETTINGS["own tasks"]
            mode = SETTINGS["own tasks mode"]
            return self.run_own_tasks(own_tasks, mode, gas_lock, ender, accounts)
        else:
            tasks = [self.task_numbers[module]]
            return self.run_own_tasks(tasks, "standart", gas_lock, ender, accounts)
    
    def run_own_tasks(self, own_tasks, mode, gas_lock, ender, accounts):


            
        p = Process(target=self.run_tasks, args=(own_tasks, mode, accounts, gas_lock, ender))
        p.start()
        self.running_threads = p
        return p






        