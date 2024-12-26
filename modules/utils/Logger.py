import datetime

from loguru import logger as console_log

from modules.config import SETTINGS_PATH

global_log = {}
indexes = []
date_and_time = str(datetime.datetime.now()).replace(":", ".")

def write_global_log():
    log = ""

    for key in global_log:
        buff = f"{key}:\n"

        for data in global_log[key]:
            buff += f"{data}\n" 
            
        log += buff + "\n"
    with open(f"{SETTINGS_PATH}logs/log_{date_and_time}.txt", "w") as f:
        f.write(log)

class logger():
    @staticmethod
    def info(message: str):
        try:
            addr = message.split("]")[0][1::]

            if addr not in indexes:
                indexes.append(addr)

            console_log.info(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[INFO] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}"]
            else:
                global_log[addr].append(f"[INFO] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

            write_global_log()
        except:
            pass
    
    @staticmethod
    def error(message: str):
        try:
            addr = message.split("]")[0][1::]

            if addr not in indexes:
                indexes.append(addr)

            msg = ""
            for i in range(1, len(message.split("]"))):
                msg += message.split("]")[i]
                if i < len(message.split("]"))-1:
                    msg += "]"

            console_log.error(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {msg}")

            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[ERROR] [{indexes.index(addr)+1}/{len(indexes)}] {msg}"]
            else:
                global_log[addr].append(f"[ERROR] [{indexes.index(addr)+1}/{len(indexes)}] {msg}")

            write_global_log()
        except:
            pass
    
    @staticmethod
    def success(message: str):
        try:
            addr = message.split("]")[0][1::]

            if addr not in indexes:
                indexes.append(addr)

            console_log.success(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[SUCCESS] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}"]
            else:
                global_log[addr].append(f"[SUCCESS] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

            write_global_log()
        except:
            pass
