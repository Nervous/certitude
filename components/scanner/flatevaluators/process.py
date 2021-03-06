#!/usr/bin/python

import template

class Evaluator(template.EvaluatorInterface):

    evalList = ['pid', 'name', 'command', 'path']

    def __init__(self, logger, ioc, remoteCommand, wd, keepFiles, confidential, dirname):
        template.EvaluatorInterface.__init__(self, logger, ioc, remoteCommand, wd, keepFiles, confidential, dirname)

        self.setEvaluatorParams(evalList=Evaluator.evalList, name='process', command='collector process')