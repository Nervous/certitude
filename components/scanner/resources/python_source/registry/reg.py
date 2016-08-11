from __future__ import unicode_literals
import codecs
from utils.utils import convert_windate, dosdate, get_csv_writer, write_list_to_csv
import registry.registry_obj as registry_obj
from win32com.shell import shell
import struct
import StringIO


KEY_VALUE_STR = 0
VALUE_NAME = 1
VALUE_DATA = 2
VALUE_TYPE = 3
VALUE_LAST_WRITE_TIME = 4
VALUE_PATH = 5

KEY_PATH = 1
KEY_LAST_WRITE_TIME = 2


def get_usb_key_info(key_name):
    """
    Extracts information about the USB keys from the registry
    :return: A list of USB key IDs
    """
    # HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\DeviceClasses\{a5dcbf10-6530-11d2-901f-00c04fb951ed}
    str_reg_key_usbinfo = r"SYSTEM\ControlSet001\Control\DeviceClasses\{a5dcbf10-6530-11d2-901f-00c04fb951ed}"

    # here is a sample of a key_name
    # ##?#USBSTOR#Disk&Ven_&Prod_USB_DISK_2.0&Rev_PMAP#07BC13025A3B03A1&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}
    # the logic is : there are 6 "#" so we should split this string on "#" and get the USB id (index 5)
    index_usb_id = 5
    usb_id = key_name.split("#")[index_usb_id]
    # now we want only the left part of the which may contain another separator "&" -> 07BC13025A3B03A1&0
    usb_id = usb_id.split("&")[0]

    # next we look in the registry for such an id
    key_ids = ""
    reg_key_info = registry_obj.get_registry_key(registry_obj.HKEY_LOCAL_MACHINE, str_reg_key_usbinfo)
    if reg_key_info:
        for i in xrange(reg_key_info.get_number_of_sub_keys()):
            subkey = reg_key_info.get_sub_key(i)
            if usb_id in subkey.get_name():
                # example of a key_info_name
                # ##?#USB#VID_26BD&PID_9917#0702313E309E0863#{a5dcbf10-6530-11d2-901f-00c04fb951ed}
                # the pattern is quite similar, a "#" separated string, with 5 as key id and 4 as VID&PID, we need
                # those 2
                index_usb_id = 4
                key_ids = subkey.get_name().split("#")[index_usb_id]
                break
    return key_ids


def csv_user_assist_value_decode_win7_and_after(str_value_datatmp, count_offset):
    """The value in user assist has changed since Win7. It is taken into account here."""
    # 16 bytes data
    str_value_data_session = str_value_datatmp[0:4]
    str_value_data_session = unicode(struct.unpack("<I", str_value_data_session)[0])
    str_value_data_count = str_value_datatmp[4:8]
    str_value_data_count = unicode(struct.unpack("<I", str_value_data_count)[0] + count_offset + 1)
    str_value_data_focus = str_value_datatmp[12:16]
    str_value_data_focus = unicode(struct.unpack("<I", str_value_data_focus)[0])
    str_value_data_timestamp = str_value_datatmp[60:68]
    try:
        timestamp = struct.unpack("<Q", str_value_data_timestamp)[0]
        date_last_exec = convert_windate(timestamp)
    except ValueError:
        date_last_exec = None
    arr_data = [str_value_data_session, str_value_data_count, str_value_data_focus]
    if date_last_exec:
        arr_data.append(date_last_exec)
    else:
        arr_data.append("")
    return arr_data


def csv_user_assist_value_decode_before_win7(str_value_datatmp, count_offset):
    """
    The Count registry key contains values representing the programs
    Each value is separated as :
    first 4 bytes are session
    following 4 bytes are number of times the program has been run
    next 8 bytes are the timestamp of last execution
    each of those values are in big endian which have to be converted in little endian
    :return: An array containing these information
    """

    # 16 bytes data
    str_value_data_session = str_value_datatmp[0:4]
    str_value_data_session = unicode(struct.unpack("<I", str_value_data_session)[0])
    str_value_data_count = str_value_datatmp[4:8]
    str_value_data_count = unicode(struct.unpack("<I", str_value_data_count)[0] + count_offset + 1)
    str_value_data_timestamp = str_value_datatmp[8:16]
    try:
        timestamp = struct.unpack("<Q", str_value_data_timestamp)[0]
        date_last_exec = convert_windate(timestamp)
    except ValueError:
        date_last_exec = None
    arr_data = [str_value_data_session, str_value_data_count]
    if date_last_exec:
        arr_data.append(date_last_exec)
    else:
        arr_data.append("")
    return arr_data

def append_reg_values(hive_list, key):
    for i in xrange(key.get_number_of_values()):
        value = key.get_value(i)
        hive_list.append(("VALUE", value.get_name(), value.get_data(), value.get_type(), key.get_last_written_time(),
                          value.get_path()))


def decode_recent_docs_mru(value):
    """
    Decodes recent docs MRU list
    Returns an array with 1st element being the filename, the second element being the symbolic link name
    """
    value_decoded = []
    index = value.find(b"\x00\x00")
    try:
        decoded = value[0:index + 1].decode("utf-16-le")
    except UnicodeDecodeError:
        try:
            decoded = value[0:index + 1].decode("utf-8")
        except UnicodeDecodeError:
            decoded = "".join([c for c in value[0:index + 1]])

    value_decoded.append(decoded)
    # index+3 because the last char also ends with \x00 + null bytes \x00\x00, +14 is the offset for the link name
    index_end_link_name = value.find(b"\x00", index + 3 + 14)
    value_decoded.append(value[index + 3 + 14:index_end_link_name])
    return value_decoded


def construct_list_from_key(hive_list, key, is_recursive=True):
    """
    Constructs the hive list. Recursive method if is_recursive=True.
    Keyword arguments:
    hive_list -- (List) the list to append to
    key -- (RegistryKey) the key to dump in the list
    """
    hive_list.append(("KEY", key.get_path(), key.get_last_written_time()))
    append_reg_values(hive_list, key)
    for i in xrange(key.get_number_of_sub_keys()):
        try:
            sub_key = key.get_sub_key(i)
        except TypeError:
            # hack for programs using unicode in registry
            for j in xrange(len(hive_list) - 1, 0, -1):
                if hive_list[j][KEY_VALUE_STR] == "KEY":
                    # get the first VALUE item in the list
                    j += 1
                    break
            if hive_list[j][VALUE_NAME] == "":
                tmp = hive_list[j]
                list_names = key.get_sub_keys_names()
                value_name = ""
                for name in list_names:
                    if "\x00" in name:
                        # invalid registry name
                        value_name = "\\x" + "\\x".join("{:02x}".format(ord(c)) for c in name)
                # replace the name of the first VALUE item by the name of the invalid registry name
                hive_list[j] = (tmp[KEY_VALUE_STR], value_name, tmp[VALUE_DATA], tmp[VALUE_TYPE],
                                tmp[VALUE_LAST_WRITE_TIME], tmp[VALUE_PATH])
            sub_key = None
        if sub_key and is_recursive:
            construct_list_from_key(hive_list, sub_key, is_recursive)


class _Reg(object):
    def __init__(self, params):
        self.computer_name = "computer_name"
        self.output_dir = "output"
        # get logged off users hives
        self.user_hives = []
        users = registry_obj.get_registry_key(registry_obj.HKEY_LOCAL_MACHINE,
                                              r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList")
        if users:
            for i in xrange(users.get_number_of_sub_keys()):
                user = users.get_sub_key(i)
                path = user.get_value_by_name("ProfileImagePath").get_data() + r"\NTUSER.DAT"
                try:
                    regf_file = registry_obj.RegfFile()
                    regf_file.open(path)
                    self.user_hives.append((user.get_name(), regf_file.get_root_key()))
                except IOError:  # user is logged on or not a user
                    pass

    def _generate_hklm_csv_list(self, to_csv_list, csv_type, path, is_recursive=True):
        """
        Generates a generic list suitable for CSV output.
        Extracts information from HKEY_LOCAL_MACHINE hives.
        """
        hive_list = self._get_list_from_registry_key(registry_obj.HKEY_LOCAL_MACHINE, path, is_recursive=is_recursive)
        for item in hive_list:
            if item[KEY_VALUE_STR] == "VALUE":
                to_csv_list.append((self.computer_name,
                                    csv_type,
                                    item[VALUE_LAST_WRITE_TIME],
                                    "HKEY_LOCAL_MACHINE",
                                    item[VALUE_PATH],
                                    item[VALUE_NAME],
                                    item[KEY_VALUE_STR],
                                    registry_obj.get_str_type(item[VALUE_TYPE]),
                                    item[VALUE_DATA]))

    def _generate_hku_csv_list(self, to_csv_list, csv_type, path, is_recursive=True):
        """
        Generates a generic list suitable for CSV output.
        Extracts information from HKEY_USERS hives.
        """
        hive_list = self._get_list_from_registry_key(registry_obj.HKEY_USERS, path, is_recursive=is_recursive)
        for item in hive_list:
            if item[KEY_VALUE_STR] == "VALUE":
                to_csv_list.append((self.computer_name,
                                    csv_type,
                                    item[VALUE_LAST_WRITE_TIME],
                                    "HKEY_USERS",
                                    item[VALUE_PATH],
                                    item[VALUE_NAME],
                                    item[KEY_VALUE_STR],
                                    registry_obj.get_str_type(item[VALUE_TYPE]),
                                    item[VALUE_DATA]))

    def _get_list_from_users_registry_key(self, key_path, is_recursive=True):
        """
        Extracts information from HKEY_USERS. Since logged off users hives are not mounted by Windows, it is necessary
        to open each NTUSER.DAT files, except for currently logged on users.
        :param key_path: the registry key to list
        :param is_recursive: whether the function should also list subkeys
        :return: a list of all extracted keys/values
        """
        hive_list = []
        key_users = registry_obj.get_registry_key(registry_obj.HKEY_USERS)
        if key_users:
            for i in xrange(key_users.get_number_of_sub_keys()):
                key_user = key_users.get_sub_key(i)
                key_data = key_user.get_sub_key_by_path(key_path)
                if key_data:
                    construct_list_from_key(hive_list, key_data, is_recursive)
        # same thing for logged off users (NTUSER.DAT)
        for sid, root_key in self.user_hives:
            key_data = root_key.get_sub_key_by_path(key_path)
            if key_data:
                key_data.prepend_path_with_sid(sid)
                construct_list_from_key(hive_list, key_data, is_recursive)
        return hive_list

    def _get_list_from_registry_key(self, hive, key_path, is_recursive=True):
        """
        Creates a list of all nodes and values from a registry key path.
        Keyword arguments:
        hive -- (String) the hive name
        key_path -- (String) the path of the key from which the list should be created
        """
        if hive == registry_obj.HKEY_USERS:
            return self._get_list_from_users_registry_key(key_path, is_recursive)
        hive_list = []
        root_key = registry_obj.get_registry_key(hive, key_path)
        if root_key:
            append_reg_values(hive_list, root_key)
            for i in xrange(root_key.get_number_of_sub_keys()):
                sub_key = root_key.get_sub_key(i)
                if sub_key:
                    construct_list_from_key(hive_list, sub_key, is_recursive)
        return hive_list

    def _csv_user_assist(self, count_offset, is_win7_or_further):
        """
        Extracts information from UserAssist registry key which contains information about executed programs
        The count offset is for Windows versions before 7, where it would start at 6
        """
        path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\\UserAssist"
        count = "\Count"
        # logged on users
        users = registry_obj.RegistryKey(registry_obj.HKEY_USERS)
        hive_list = []
        for i in xrange(users.get_number_of_sub_keys()):
            user = users.get_sub_key(i)
            user_assist_key = user.get_sub_key_by_path(path)
            if user_assist_key:
                for j in xrange(user_assist_key.get_number_of_sub_keys()):
                    # getting Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\*\Count
                    path_no_sid = "\\".join(user_assist_key.get_sub_key(j).get_path().split("\\")[1:])
                    hive_list += self._get_list_from_registry_key(registry_obj.HKEY_USERS, path_no_sid + count)
        if is_win7_or_further:
            to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                            "ATTR_TYPE", "ATTR_DATA", "DATA_SESSION", "DATA_COUNT", "DATA_FOCUS", "DATA_LAST_EXEC")]
        else:
            to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                            "ATTR_TYPE", "ATTR_DATA", "DATA_SESSION", "DATA_COUNT", "DATA_LAST_EXEC")]
        for item in hive_list:
            if item[KEY_VALUE_STR] == "VALUE":
                str_value_name = codecs.decode(item[VALUE_NAME], "rot_13")
                str_value_datatmp = item[VALUE_DATA]
                # some data are less than 16 bytes for some reason...
                if len(str_value_datatmp) < 16:
                    to_csv_list.append((self.computer_name,
                                        "userassist",
                                        item[VALUE_LAST_WRITE_TIME],
                                        "HKEY_USERS",
                                        item[VALUE_PATH],
                                        item[VALUE_NAME],
                                        item[KEY_VALUE_STR],
                                        registry_obj.get_str_type(item[VALUE_TYPE]),
                                        str_value_name))
                else:
                    if is_win7_or_further:
                        data = csv_user_assist_value_decode_win7_and_after(str_value_datatmp, count_offset)
                    else:
                        data = csv_user_assist_value_decode_before_win7(str_value_datatmp, count_offset)
                    to_csv_list.append((self.computer_name,
                                        "user_assist",
                                        item[VALUE_LAST_WRITE_TIME],
                                        "HKEY_USERS",
                                        item[VALUE_PATH],
                                        item[VALUE_NAME],
                                        item[KEY_VALUE_STR],
                                        registry_obj.get_str_type(item[VALUE_TYPE]),
                                        str_value_name) + tuple(data))
        with open(self.output_dir + "\\" + self.computer_name + "_user_assist.csv", "wb") as output:
            csv_writer = get_csv_writer(output)
            write_list_to_csv(to_csv_list, csv_writer)

    def csv_registry_services(self):
        """Extracts services"""
        path = r"System\CurrentControlSet\Services"
        to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                        "ATTR_TYPE", "ATTR_DATA")]
        self._generate_hklm_csv_list(to_csv_list, "registry_services", path)
        with open(self.output_dir + "\\" + self.computer_name + "_registry_services.csv", "wb") as output:
            csv_writer = get_csv_writer(output)
            write_list_to_csv(to_csv_list, csv_writer)

    def csv_run_mru_start(self):
        """Extracts run MRU, containing the last 26 oommands executed using the RUN command"""
        path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
        to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                        "ATTR_TYPE", "ATTR_DATA")]
        self._generate_hku_csv_list(to_csv_list, "run_MRU_start", path)
        #with open(self.output_dir + "\\" + self.computer_name + "_run_MRU_start.csv", "wb") as output:
            #csv_writer = get_csv_writer(output)
        write_list_to_csv(to_csv_list, None)

    def csv_recent_docs(self):
        """Extracts information about recently opened files saved location and opened date"""
        path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"
        hive_list = self._get_list_from_registry_key(registry_obj.HKEY_USERS, path)
        to_csv_list = []
        for item in hive_list:
            if item[KEY_VALUE_STR] == "VALUE":
                if item[VALUE_NAME] != "MRUListEx":
                    values_decoded = decode_recent_docs_mru(item[VALUE_DATA])
                    for value_decoded in values_decoded:
                        to_csv_list.append((self.computer_name,
                                            "recent_docs",
                                            item[VALUE_LAST_WRITE_TIME],
                                            "HKEY_USERS",
                                            item[VALUE_PATH],
                                            item[VALUE_NAME],
                                            item[KEY_VALUE_STR],
                                            registry_obj.get_str_type(item[VALUE_TYPE]),
                                            value_decoded))
       # with open(self.output_dir + "\\" + self.computer_name + "_recent_docs.csv", "wb") as output:
        #csv_writer = get_csv_writer(output)
        write_list_to_csv(to_csv_list, None)

    def csv_startup_programs(self):
        """Extracts programs running at startup from various keys"""
        software = "Software"
        wow = r"\Wow6432Node"
        ts_run = (r"\Microsoft\Windows NT\CurrentVersion\Terminal Server\Install\Software"
                  r"\Microsoft\Windows\CurrentVersion\Run")
        ts_run_once = (r"\Microsoft\Windows NT\CurrentVersion\Terminal Server\Install\Software"
                       r"\Microsoft\Windows\CurrentVersion\RunOnce")
        paths = [r"\Microsoft\Windows\CurrentVersion\Run",
                 r"\Microsoft\Windows\CurrentVersion\RunOnce",
                 r"\Microsoft\Windows\CurrentVersion\RunOnceEx",
                 r"\Microsoft\Windows\CurrentVersion\RunServices",
                 r"\Microsoft\Windows\CurrentVersion\RunServicesOnce",
                 # r"\Microsoft\Windows NT\CurrentVersion\Winlogon\\Userinit",
                 # r"\Microsoft\Windows NT\CurrentVersion\Windows",
                 r"\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
                 ts_run,
                 ts_run_once]
        to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                        "ATTR_TYPE", "ATTR_DATA")]
        for path in paths:
            full_path = software + path
            self._generate_hklm_csv_list(to_csv_list, "startup", full_path)
            full_path = software + wow + path
            self._generate_hklm_csv_list(to_csv_list, "startup", full_path)

        paths = [r"\Microsoft\Windows\CurrentVersion\Run",
                 r"\Microsoft\Windows\CurrentVersion\RunOnce",
                 r"\Microsoft\Windows\CurrentVersion\RunOnceEx",
                 r"\Microsoft\Windows\CurrentVersion\RunServices",
                 r"\Microsoft\Windows\CurrentVersion\RunServicesOnce",
                 r"\Microsoft\Windows NT\CurrentVersion\Windows",
                 r"\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
                 ts_run,
                 ts_run_once]
        for path in paths:
            full_path = software + path
            self._generate_hku_csv_list(to_csv_list, "startup", full_path)
            full_path = software + wow + path
            self._generate_hku_csv_list(to_csv_list, "startup", full_path)
       # with open(self.output_dir + "\\" + self.computer_name + "_startup.csv", "wb") as output:
            #csv_writer = get_csv_writer(output)
        write_list_to_csv(to_csv_list, None)

    def csv_installed_components(self):
        """
        Extracts installed components key
        When an installed component key is in HKLM but not in HKCU, the path specified in HKLM will be added in HKCU
        and will be executed by the system
        """
        path = r"Software\Microsoft\Active Setup\Installed Components"
        to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                        "ATTR_TYPE", "ATTR_DATA")]
        self._generate_hklm_csv_list(to_csv_list, "installed_components", path)
        with open(self.output_dir + "\\" + self.computer_name + "_installed_components.csv", "wb") as output:
            csv_writer = get_csv_writer(output)
            write_list_to_csv(to_csv_list, csv_writer)

    def csv_winlogon_values(self):
        """
        Extracts winlogon values, in particular UserInit, where the specified executable will be executed at
        system startup
        """
        path = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
        to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                        "ATTR_TYPE", "ATTR_DATA")]
        self._generate_hklm_csv_list(to_csv_list, "winlogon_values", path)
        self._generate_hku_csv_list(to_csv_list, "winlogon_values", path)
        with open(self.output_dir + "\\" + self.computer_name + "_winlogon_values.csv", "wb") as output:
            csv_writer = get_csv_writer(output)
            write_list_to_csv(to_csv_list, csv_writer)

    def csv_windows_values(self):
        """
        Extracts windows values, in particular AppInit_DLLs, where any DLL specified here will be loaded by any
        application
        """
        path = r"Software\Microsoft\Windows NT\CurrentVersion\Windows"
        to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "ATTR_NAME", "REG_TYPE",
                        "ATTR_TYPE", "ATTR_DATA")]
        self._generate_hklm_csv_list(to_csv_list, "windows_values", path)
        self._generate_hku_csv_list(to_csv_list, "windows_values", path)
        with open(self.output_dir + "\\" + self.computer_name + "_windows_values.csv", "wb") as output:
            csv_writer = get_csv_writer(output)
            write_list_to_csv(to_csv_list, csv_writer)

    def csv_usb_history(self):
        """Extracts information about USB devices that have been connected since the system installation"""
        hive_list = self._get_list_from_registry_key(
            registry_obj.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{53f56307-b6bf-11d0-94f2-00a0c91efb8b}",
            is_recursive=False)
        to_csv_list = [("COMPUTER_NAME", "TYPE", "LAST_WRITE_TIME", "HIVE", "KEY_PATH", "KEY_VALUE", "USB_ID")]
        for item in hive_list:
            if item[KEY_VALUE_STR] == "KEY":
                usb_decoded = get_usb_key_info(item[KEY_PATH])
                to_csv_list.append((self.computer_name,
                                    "USBHistory",
                                    item[KEY_LAST_WRITE_TIME],
                                    "HKEY_LOCAL_MACHINE",
                                    item[KEY_PATH],
                                    item[KEY_VALUE_STR],
                                    usb_decoded))
        with open(self.output_dir + "\\" + self.computer_name + "_USBHistory.csv", "wb") as output:
            csv_writer = get_csv_writer(output)
            write_list_to_csv(to_csv_list, csv_writer)
