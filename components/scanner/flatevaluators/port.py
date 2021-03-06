#!/usr/bin/python

import template

class Evaluator(template.EvaluatorInterface):

    evalList = ['protocol', 'localIP', 'localPort', 'remoteIP', 'remotePort', 'state', 'pid']

    def __init__(self, logger, ioc, remoteCommand, wd, keepFiles, confidential, dirname):
        template.EvaluatorInterface.__init__(self, logger, ioc, remoteCommand, wd, keepFiles, confidential, dirname)

        self.setEvaluatorParams(evalList=Evaluator.evalList, name='port', command='collector getport')