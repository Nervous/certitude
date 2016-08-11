from __future__ import unicode_literals
from registry.reg import _Reg


class Windows8_1UserReg(_Reg):
    def __init__(self, params):
        _Reg.__init__(self, params)

    def list_recent_docs(self):
        super(Windows8_1UserReg, self).csv_recent_docs()

    def list_startup_files(self):
        super(Windows8_1UserReg, self).csv_startup_programs()

    def list_MRU_history(self):
        super(Windows8_1UserReg, self).csv_run_mru_start()