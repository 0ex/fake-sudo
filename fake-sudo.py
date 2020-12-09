#!/usr/bin/env python3
"""
Fake Sudo

https://github.com/0ex/fake-sudo
"""

import os, sys, re
from seccomp import SyscallFilter, Attr, NOTIFY, ALLOW, Arch, NotificationResponse
from seccomp import resolve_syscall

def main():
    progname, *args = sys.argv[:]
    shell = None

    while args:
        a = args.pop(0)

        # convert --a=b → --a b
        m = re.match(r'--(.+)=(.*)', a)
        if m:
            a = m[1]
            args.insert(0, m[2])

        if a in ['-h', '--help']:
            print('usage: %s [-u <user>] [<cmd> <arg>...]' % progname)
            sys.exit(0)

        elif a in ['-i', '--login']:
            shell = ['/bin/bash', '-l']

        elif a in ['-s', '--shell']:
            # use SHELL env, passwd entry
            shell = ['/bin/bash']

        elif a in ['-u', '--user']:
            u = args.pop(0)
            print('%s: ignoring user %s', progname, u)

        elif a[0] == '-':
            print('ERROR invalid option %s', a)
            sys.exit(1)

        elif a == '--':
            break

        else:
            args.insert(0, a)
            break

    if shell and args:
        args = shell + ['-c', ' '.join(args)]
    elif shell:
        args = shell
    elif not args:
        print('ERROR missing command')
        sys.exit(1)

    run(['unshare', '-r', '--'] + args)

SYSCALLS = [
    'chown', 'chown32', 'lchown', 'lchown32',
    'fchown', 'fchown32', 'fchownat',
]

def run(cmd):
    """Run cmd (an argv-style list of strings)
    """

    f = SyscallFilter(ALLOW)
    f.set_attr(Attr.CTL_TSYNC, 1)
    for c in SYSCALLS:
        f.add_rule(NOTIFY, c)
    f.load()
    pid = os.fork()
    if pid == 0:
        print('exec', cmd)
        os.execvp(cmd[0], cmd)
        sys.exit(1)
   
    while True:
        notify = f.receive_notify()
        syscall = resolve_syscall(Arch(), notify.syscall)
        print('call', syscall, notify.args)
        f.respond_notify(NotificationResponse(notify, val=0, error=0, flags=1))

    wpid, rc = os.waitpid(pid, 0)
    if os.WIFEXITED(rc) == 0:
        raise RuntimeError("Child process error")
    if os.WEXITSTATUS(rc) != 0:
        raise RuntimeError("Child process error")
    sys.exxit(1)

if __name__ == '__main__':
    main()

