from __future__ import unicode_literals
from registry.reg import _Reg


class Windows2003ServerR2UserReg(_Reg):
    def __init__(self, params):
        _Reg.__init__(self, params)

    def list_recent_docs(self):
        super(Windows2003ServerR2UserReg, self).csv_recent_docs()

    def list_startup_files(self):
        super(Windows2003ServerR2UserReg, self).csv_startup_programs()

    def csv_open_save_mru(self):
        super(Windows2003ServerR2UserReg, self)._csv_open_save_mru(
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSaveMRU")

    def csv_user_assist(self):
        super(Windows2003ServerR2UserReg, self)._csv_user_assist(-6, False)