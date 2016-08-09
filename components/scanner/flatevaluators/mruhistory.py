#!/usr/bin/python

import template

class Evaluator(template.EvaluatorInterface):

    evalList = ['computer_name', 'type', 'last_write_time', 'hive', 'key_path', 'attr_name', 'reg_type', 'attr_type', 'attr_data']

    def __init__(self, logger, ioc, remoteCommand, wd, keepFiles, confidential, dirname):
        template.EvaluatorInterface.__init__(self, logger, ioc, remoteCommand, wd, keepFiles, confidential, dirname)

        self.setEvaluatorParams(evalList=Evaluator.evalList, name='mruhistory', command='collector mruhistory')