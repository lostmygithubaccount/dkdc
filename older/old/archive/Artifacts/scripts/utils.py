import os
import time
import subprocess
import sys


def run_command(commands,
                cwd=None,
                stderr=subprocess.STDOUT,
                shell=False,
                stream_stdout=True,
                throw_on_retcode=True,
                return_stdout=False,
                verbose=True):
    def _print(line):
        if verbose:
            print(line)

    if cwd is None:
        cwd = os.getcwd()

    retcode = 0

    t0 = time.clock()
    try:
        _print('Executing "{0}" in {1}'.format(" ".join(commands), cwd))
        out = ""
        p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=stderr, cwd=cwd, shell=shell)
        for line in p.stdout:
            line = line.decode("utf-8").rstrip() + "\n"
            if stream_stdout:
                sys.stdout.write(line)
            out += line
        p.communicate()
        retcode = p.poll()
    except Exception as e:
        print(e)
    finally:
        t1 = time.clock()
        _print('Execution took {0}s for "{1}" in {2}'.format(t1 - t0, " ".join(commands), cwd))
        if throw_on_retcode and retcode:
            raise subprocess.CalledProcessError(retcode, p.args, output=out, stderr=p.stderr)
        if return_stdout:
            return out
        return retcode
