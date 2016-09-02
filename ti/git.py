# coding: utf-8
import os.path
import subprocess


class Git(object):
    path = '/usr/bin/git'

    def is_git_installed(self):
        return os.path.exists(self.path)

    def is_cwd_repo(self):
        return self.get_cmd_retcode(['git', 'rev-parse', 'HEAD']) == 0

    def get_active_branch(self):
        return self.get_cmd_retcode_and_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

    def get_top_level(self):
        return self.get_cmd_retcode_and_output(['git', 'rev-parse', '--show-toplevel'])

    def get_cmd_retcode(self, cmd):
        devnull = open(os.devnull, 'w')
        retcode = subprocess.call(cmd, stdout=devnull, stderr=subprocess.STDOUT)
        return retcode

    def get_cmd_retcode_and_output(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        retcode = process.returncode
        if retcode == 0:
            return output.decode('utf-8').strip()
        return False
