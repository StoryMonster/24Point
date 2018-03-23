import time

class Logger:
    def __init__(self, log_file, allow_log):
        self.log_file = log_file
        self.log_enabled = allow_log
        if self.log_enabled:
            with open(self.log_file, 'w'): pass

    def log_msg(self, msg):
        if not self.log_enabled:
            return
        with open(self.log_file, 'a') as f:
            current_time = time.localtime()
            time_str = str(current_time.tm_hour) + ':' + str(current_time.tm_min) + ':' + str(current_time.tm_sec)
            f.write('[debug] ' + time_str + ' ' + msg + '\n')

def warn_msg(msg):
    print '\033[31;40m' + '[warning] ' + msg + '\033[0m'

def error_msg(msg):
    print '\033[31;40m' + '[error] ' + msg + '\033[0m'

def normal_msg(msg):
    print msg

def success_msg(msg):
    print '\033[32;40m' + msg + '\033[0m'
