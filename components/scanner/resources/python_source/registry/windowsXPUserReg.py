from __future__ import unicode_literals
from registry.reg import _Reg


class WindowsXPUserReg(_Reg):
    def __init__(self, params):
        _Reg.__init__(self, params)

    def list_recent_docs(self):
        super(WindowsXPUserReg, self).csv_recent_docs()

    def list_startup_files(self):
        super(WindowsXPUserReg, self).csv_startup_programs()

    def list_MRU_history(self):
        super(WindowsXPUserReg, self)._csv_open_save_mru(
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSaveMRU")