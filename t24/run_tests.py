import os
import sys
from tempfile import TemporaryFile
from subprocess import Popen, call, STDOUT

try:
    import SeleniumLibrary
except ImportError:
    print 'Importing SeleniumLibrary module failed.'
    sys.exit(1)


    
ROOT = os.path.dirname(os.path.abspath(__file__))


def run_tests(args):
    start_selenium_server()
    print '*****Server Started*****'
    call(['pybot'] + args)
    print '*****Server about to stop*****'
    stop_selenium_server()

def start_selenium_server():
    logfile = open(os.path.join(ROOT, 'selenium_log.txt'), 'w')
    SeleniumLibrary.start_selenium_server(logfile)

def stop_selenium_server():
    SeleniumLibrary.shut_down_selenium_server()

def print_help():
    print __doc__

def print_usage():
    print 'Usage: run_tests.py [options] datasource'
    print '   or: run_tests.py selenium start|stop'
    print '   or: run_tests.py help'


if __name__ == '__main__':
    action = {'selenium-start': start_selenium_server,
              'selenium-stop': stop_selenium_server,
              'help': print_help,
              '': print_usage}.get('-'.join(sys.argv[1:]))
    if action:
        action()
    else:
        run_tests(sys.argv[1:])

