from __future__ import unicode_literals
from registry.reg import _Reg


class Windows2008ServerUserReg(_Reg):
    def __init__(self, params):
        _Reg.__init__(self, params)

    def list_recent_docs(self):
        super(Windows2008ServerUserReg, self).csv_recent_docs()

    def list_startup_files(self):
        super(Windows2008ServerUserReg, self).csv_startup_programs()

    def list_MRU_history(self):
        super(Windows2008ServerUserReg, self).csv_run_mru_start()