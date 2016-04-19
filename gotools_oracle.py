import sublime
import sublime_plugin
import os
import golangconfig

from .gotools_util import Buffers
from .gotools_util import GoBuffers
from .gotools_util import Logger
from .gotools_util import ToolRunner

class GotoolsOracleCommand(sublime_plugin.TextCommand):
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
      for p in golangconfig.setting_value("build_packages", view=self.view)[0]:
        package_scope.append(os.path.join(project_package, p))

    sublime.active_window().run_command("hide_panel", {"panel": "output.gotools_oracle"})
    self.do_plain_oracle(command, pos, package_scope)

  def do_plain_oracle(self, mode, pos, package_scope=[], regex="^(.*):(\d+):(\d+):(.*)$"):
    Logger.status("running oracle "+mode+"...")
    args = ["-pos="+pos, "-format=plain", mode]
    if len(package_scope) > 0:
      args = args + package_scope
    output, err, rc = ToolRunner.run(self.view, "oracle", args, timeout=60)
    Logger.log("oracle "+mode+" output: " + output.rstrip())

    if rc != 0:
      print("GoTools: oracle error:")
      print(err)
      Logger.status("oracle call failed (" + str(rc) +")")
      return
    Logger.status("oracle "+mode+" finished")

    panel = self.view.window().create_output_panel('gotools_oracle')
    panel.set_scratch(True)
    panel.settings().set("result_file_regex", regex)
    panel.run_command("select_all")
    panel.run_command("right_delete")
    panel.run_command('append', {'characters': output})
    self.view.window().run_command("show_panel", {"panel": "output.gotools_oracle"})
