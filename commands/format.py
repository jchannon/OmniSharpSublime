import os
import sublime
import sublime_plugin
import operator

from ..lib import omnisharp
from ..lib import helpers


class OmniSharpFormat(sublime_plugin.TextCommand):
    data = None

    def run(self, edit, keyvalue):
        self.keyvalue = keyvalue

        if self.data is None:
            pos = self.view.sel()[0].begin() 
            self.view.insert(edit, pos, keyvalue) #put back the character the user just typed into the editor
            params = {}
            params["Character"] = keyvalue
            omnisharp.get_response(self.view, '/formatAfterKeystroke', self._handle_format, params)
        else:
            self._formatlikeresharper(edit)

    def _handle_format(self, data):
        if data is None:
            return
        self.data = data
        self.view.run_command('omni_sharp_format', {'keyvalue':self.keyvalue})

    def _formatlikeresharper(self, edit):
        if self.data != None:
            #order it by highest endline number otherwise could mess up line numbers by values with NewText : '\n    '
            # self.data["Changes"].sort(key= lambda x: x["EndLine"], reverse=True) 
            for i in self.data["Changes"]:
                if i['NewText']:
                    #replace text
                    firstpoint = self.view.text_point(int(i['StartLine'])-1, int(i['StartColumn'])-1)
                    secondpoint = self.view.text_point(int(i['EndLine'])-1,int(i['EndColumn'])-1)
                    reg = sublime.Region(firstpoint,secondpoint)
                    self.view.replace(edit, reg, i['NewText'])
                else:
                    #if NewText is empty delete from a certain points
                    firstpoint = self.view.text_point(int(i['StartLine'])-1, int(i['StartColumn'])-1)
                    secondpoint = self.view.text_point(int(i['EndLine'])-1,int(i['EndColumn'])-1)
                    reg = sublime.Region(firstpoint,secondpoint)
                    self.view.erase(edit, reg)

        self.data = None

    def is_enabled(self):
        return helpers.is_csharp(self.view)