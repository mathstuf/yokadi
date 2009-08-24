# -*- coding: UTF-8 -*-
"""
Simple rendering of t_list output

@author: Aurélien Gâteau <aurelien.gateau@free.fr>
@license: GPLv3
"""

import tui

class PlainListRenderer(object):
    def __init__(self, out, cryptoMgr, decrypt = False):
        self.out = out
        self.first = True
        self.decrypt = decrypt # Wether to decrypt or not encrypted data
        self.cryptoMgr = cryptoMgr # Yokadi cryptographic manager


    def addTaskList(self, sectionName, taskList):
        """Store tasks for this section
        @param sectionName: name of the task groupement section
        @type sectionName: unicode
        @param taskList: list of tasks to display
        @type taskList: list of db.Task instances
        """

        if not self.first:
            print >>self.out
        else:
            self.first = False
        print >>self.out, sectionName.encode(tui.ENCODING)

        for task in taskList:
            if self.cryptoMgr.isEncrypted(task.title):
                if self.decrypt:
                    title = self.cryptoMgr.decrypt(task.title)
                else:
                    title = "<...encrypted data...>"
            else:
                title = task.title

            print >>self.out, (u"- " + title).encode(tui.ENCODING)

    def end(self):
        pass
# vi: ts=4 sw=4 et
