#!/usr/bin/python

# Importing all Windows classes because pyinstaller doesn't support
# dynamic imports
import os
from utils.utils import get_os_version, get_os_name
from health.windowsXPStateMachine import WindowsXPStateMachine
from health.windowsVistaStateMachine import WindowsVistaStateMachine
from health.windows7StateMachine import Windows7StateMachine
from health.windows8StateMachine import Windows8StateMachine
from health.windows8_1StateMachine import Windows8_1StateMachine
from health.windows2003ServerStateMachine import Windows2003ServerStateMachine
from health.windows2003ServerR2StateMachine import Windows2003ServerR2StateMachine
from health.windows2008ServerStateMachine import Windows2008ServerStateMachine
from health.windows2008ServerR2StateMachine import Windows2008ServerR2StateMachine
from health.windows2012ServerStateMachine import Windows2012ServerStateMachine
from health.windows2012ServerR2StateMachine import Windows2012ServerR2StateMachine

def getprocess():
    os_version = get_os_version()
    params = {}
    params['system_root'] = os.environ["SYSTEMROOT"]
    class_name = get_os_name(os_version) + "StateMachine"
    module_name = "health." + class_name
    class_name = class_name[0].upper() + class_name[1:]
    mod = __import__(module_name, fromlist=[class_name], globals=globals())
    instance_health = getattr(mod, class_name)(params)
    instance_health.list_running_proccess()


def main():
	getprocess()

if __name__=='__main__':
    main()

