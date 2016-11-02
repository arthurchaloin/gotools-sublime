import sublime
import sublime_plugin
import os
import golangconfig

from .gotools_util import Buffers
from .gotools_util import GoBuffers
from .gotools_util import Logger
from .gotools_util import ToolRunner

class GotoolsGuruCommand(sublime_plugin.TextCommand):
  def is_enabled(self):
    return GoBuffers.is_go_source(self.view)

  def run(self, edit, command=None):
    if not command:
      Logger.log("command is required")
      return

    filename, row, col, offset, offset_end = Buffers.location_at_cursor(self.view)
    if command == "freevars":
      pos = filename+":#"+str(offset)+","+"#"+str(offset_end)
    else:
      pos = filename+":#"+str(offset)

    # Build up a package scope contaning all packages the user might have
    # configured.
    package_scope = []
    project_package = golangconfig.setting_value("project_package", view=self.view)[0]
    if project_package:
      if not golangconfig.setting_value("build_packages")[0]:
        package_scope.append(project_package)
      else:
        for p in golangconfig.setting_value("build_packages", view=self.view)[0]:
          package_scope.append(os.path.join(project_package, p))

    sublime.active_window().run_command("hide_panel", {"panel": "output.gotools_guru"})
    self.do_plain_guru(command, pos, package_scope)

  def do_plain_guru(self, mode, pos, package_scope=[], regex="^(.*):(\d+):(\d+):(.*)$"):
    Logger.status("running guru "+mode+"...")
    args = []
    if len(package_scope) > 0:
      args = ["-scope", ",".join(package_scope)]

    args = args + [mode, pos]
    output, err, rc = ToolRunner.run(self.view, "guru", args, timeout=60)
    Logger.log("guru "+mode+" output: " + output.rstrip())

    if rc != 0:
      print("GoTools: Guru error:\n%s" % err)
      Logger.status("guru call failed (" + str(rc) +")")
      return
    Logger.status("guru "+mode+" finished")

    panel = self.view.window().create_output_panel('gotools_guru')
    panel.set_scratch(True)
    panel.settings().set("result_file_regex", regex)
    panel.run_command("select_all")
    panel.run_command("right_delete")
    panel.run_command('append', {'characters': output})
    self.view.window().run_command("show_panel", {"panel": "output.gotools_guru"})
