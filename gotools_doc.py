import sublime
import sublime_plugin
import os

from .gotools_util import Buffers
from .gotools_util import GoBuffers
from .gotools_util import Logger
from .gotools_util import ToolRunner

class GotoolsDocCommand(sublime_plugin.TextCommand):
  def is_enabled(self):
    return GoBuffers.is_go_source(self.view)

  def run(self, edit):
    command = "go"
    args = ["doc"]

    if self.view.sel()[0].size() > 0:
      args.append(self.view.substr(self.view.sel()[0]))
    else:
      args.append(self.view.substr(self.view.word(self.view.sel()[0].begin())))

    stdout, stderr, rc = ToolRunner.run(command, args)
    output_view = self.view.window().create_output_panel('godoc-output')

    if rc == 0:
      output_view.run_command('append', {'characters': stdout})
    else:
      output_view.run_command('append', {'characters': stderr})

    self.view.window().run_command("show_panel", {"panel": "output.godoc-output"})
