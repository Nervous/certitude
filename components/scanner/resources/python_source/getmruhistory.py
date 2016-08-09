#!/usr/bin/python

# Importing all Windows classes because pyinstaller doesn't support dynamic imports
import os
from utils.utils import get_os_version, get_os_name
from registry.windowsXPUserReg import WindowsXPUserReg
from registry.windowsVistaUserReg import WindowsVistaUserReg
from registry.windows7UserReg import Windows7UserReg
from registry.windows8UserReg import Windows8UserReg
from registry.windows8_1UserReg import Windows8_1UserReg
from registry.windows2003ServerUserReg import Windows2003ServerUserReg
from registry.windows2003ServerR2UserReg import Windows2003ServerR2UserReg
from registry.windows2008ServerUserReg import Windows2008ServerUserReg
from registry.windows2008ServerR2UserReg import Windows2008ServerR2UserReg
from registry.windows2012ServerUserReg import Windows2012ServerUserReg
from registry.windows2012ServerR2UserReg import Windows2012ServerR2UserReg

def getMRUHistory():
    os_version = get_os_version()
    params = {}
    params['system_root'] = os.environ["SYSTEMROOT"]
    class_name = get_os_name(os_version) + "UserReg"
    module_name = "registry." + class_name
    class_name = class_name[0].upper() + class_name[1:]
    mod = __import__(module_name, fromlist=[class_name], globals=globals())
    instance_registry = getattr(mod, class_name)(params)
    instance_registry.list_MRU_history()


def main():
	getMRUHistory()

if __name__=='__main__':
    main()

