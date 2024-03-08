#!/usr/bin/env python3
"""
Fake Sudo

https://github.com/0ex/fake-sudo
"""

import os, sys, re
import signal
from seccomp import SyscallFilter, Attr, NOTIFY, ALLOW, Arch, NotificationResponse
from seccomp import resolve_syscall
from threading import Thread

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

def handle_syscalls(f):
    while alive:
        notify = f.receive_notify()
        syscall = resolve_syscall(Arch(), notify.syscall)
        log(f'faking {syscall.decode()}({", ".join(str(a) for a in notify.syscall_args)}) pid={notify.pid}')
        f.respond_notify(NotificationResponse(notify, val=0, error=0, flags=1))

def log(msg):
    print(f'sudo: {msg}', file=sys.stderr)
    
alive = True

def handle_signal(sig, frame):
    global alive

    log(f'signal {sig}')

    if sig == signal.SIGCHLD:
        alive = False

def run(cmd):

    # setup filter
    f = SyscallFilter(ALLOW)
    f.set_attr(Attr.CTL_TSYNC, 1)
    for c in SYSCALLS:
        f.add_rule(NOTIFY, c)
    f.load()

    # interrupt receive_notify when the child is dead
    signal.signal(signal.SIGCHLD, handle_signal)
    signal.siginterrupt(signal.SIGCHLD, True)
    signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGCHLD})
    
    # we could use this instead
    # get_notify_fd()

    pid = os.fork()
    if pid == 0:
        os.execvp(cmd[0], cmd)
    
    log(f'waiting {pid}')

    try:
        handle_syscalls(f)
    except Exception as e:
        if alive:
            raise

    _, rc = os.waitpid(pid, 0)
    log(f'done {rc}')
    sys.exit(os.WEXITSTATUS(rc))

if __name__ == '__main__':
    main()

