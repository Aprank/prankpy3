# -*- coding: utf-8 -*-
from .client import LineClient
from types import *

import os, sys, threading

class LinePoll(object):
    OpInterrupt = {}
    client = None

    def __init__(self, client):
        if type(client) is not LineClient:
            raise Exception("You need to set LineClient instance to initialize LinePoll")
        self.client = client
    
    def fetchOperation(self, revision, count=1):
        return self.client.poll.fetchOps(revision, count, 0, 0)
        # return self.client.poll.fetchOperations(revision, count)

    def addOpInterruptWithDict(self, OpInterruptDict):
        self.OpInterrupt.update(OpInterruptDict)

    def addOpInterrupt(self, OperationType, DisposeFunc):
        self.OpInterrupt[OperationType] = DisposeFunc
        
    def execute(self, op, thread):
        try:
            if thread == True:
                _td = threading.Thread(target=self.OpInterrupt[op.type], args=(op,))
                _td.daemon = False
                _td.start()
            else:
                self.OpInterrupt[op.type](op)
        except Exception as e:
            self.client.log(e)
    
    def setRevision(self, revision):
        self.client.revision = max(revision, self.client.revision)

    def singleTrace(self, count=2):
        try:
            operations = self.fetchOperation(self.client.revision, count=count)
        except KeyboardInterrupt:
            exit()
        except:
            return
        
        if operations is None:
            self.client.log('No operation available now.')
        else:
            return operations

    def trace(self, thread=False):
        try:
            operations = self.fetchOperation(self.client.revision)
        except KeyboardInterrupt:
            exit()
        except:
            return
        
        for op in operations:
            if op.type in self.OpInterrupt.keys():
                self.execute(op, thread)
            self.setRevision(op.revision)