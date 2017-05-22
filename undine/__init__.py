#!/bin/python
""" undine
    A wrapper for handling multi-archive backups with Borg
"""

from __future__ import print_function

__author__="Mike Shultz <mike@votesmart.org>"
__copyright__="Copyright (c) 2017 Vote Smart"
__version__="0.0.2"

import os, sys, argparse, socket, configparser, fasteners
from subprocess import Popen, PIPE
from envelopes import Envelope

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def main():
    """ Script meat """

    # Handle command line args
    parser = argparse.ArgumentParser(description='A wrapper for handling multi-archive backups with Borg')
    parser.add_argument('--dry-run', action='store_true', dest="dryrun", help="Do not actually create archives.")
    parser.add_argument('-v', '--verbose', action='store_true', dest="verbose", help="Show output")
    parser.add_argument('-d', '--debug', action='store_true', dest="debug", help="Show debug output")
    parser.add_argument('-l', '--lock-file', dest="lockfile", default=u"/tmp/backup.log", help="Lock file to use")
    args = parser.parse_args()

    # Config helper
    def get_bool_config(sect, key, default = False):
        try:
            conf = parser.get(sect, key)
            return conf
        except configparser.NoSectionError:
            return default

    # Config handling. 
    config_file = ""
    user_config_file = os.path.expanduser('~/.config/undine.ini')
    system_config_file = '/etc/undine.ini'
    # User ini trumps system ini
    if os.path.isfile(user_config_file):
        config_file = user_config_file
    elif os.path.isfile(system_config_file):
        config_file = system_config_file
    else:
        raise Exception("Could not find configuration ini file at ~/.config/undine.ini or /etc/undine.ini.")
    parser = configparser.ConfigParser()
    parser.read(config_file)

    config = {
        'debug': get_bool_config('default', 'debug'),
        'verbose': False,
        'repos': parser.get('default', 'repos', fallback='ssh://rsync//data1/home/9774/file0.ia.votesmart.org'),
        'notify_email': parser.get('default', 'notify_email', fallback='root@votesmart.org'),
        'lockfile': args.lockfile or parser.get('default', 'lockfile', fallback='/tmp/udine.lock'),
        'units': dict(parser.items('units')),
        'hostname': parser.get('default', 'hostname', fallback=socket.gethostname()),
        'smtp_host': parser.get('smtp', 'host', fallback='localhost'),
        'smtp_port': parser.get('smtp', 'port', fallback='589'),
        'smtp_login': parser.get('smtp', 'login', fallback=None),
        'smtp_password': parser.get('smtp', 'password', fallback=None),
        'smtp_tls': parser.get('smtp', 'tls', fallback=True),
    }

    # debug turns on verbose
    if config['debug']:
        config['debug'] = True
        config['verbose'] = True

    # E-mail log
    email_log = []

    # Should probably prevent multiple backups from running
    with fasteners.InterProcessLock(config['lockfile']):

        if config['verbose']:
            print('Backing up system...')

        # Handle special arguments
        extra_args = ""
        if args.dryrun:
            extra_args += "-n"

        for name,path in config['units'].items():

            # Command we're using
            cmd = "borg create %s -C lz4 %s::%s-{now:%%Y-%%m-%%d} %s" % \
                (extra_args, config['repos'], name, path, )

            if config['debug']:
                print("Running: %s" % cmd)

            # Run the backup
            pipes = Popen(cmd, shell=True, 
                stdout=PIPE, stderr=PIPE)

            # Get output
            out, err = pipes.communicate()

            # Handle the return
            if pipes.returncode != 0:
                if config['verbose']:
                    print("Error creating archive for %s::%s" % (config['repos'], name, ), file=sys.stderr)
                email_log.append("FAIL: %s::%s" % (config['repos'], name, ))
                email_log.append(str(err))
            else:
                if config['verbose']:
                    print("Successfully created archive for %s::%s", (config['repos'], name, ))
                email_log.append("SUCCESS: %s::%s" % (config['repos'], name, ))

    if not args.dryrun and len(email_log) > 0:
        # Create E-mail
        envelope = Envelope(
            from_addr=u'root@votesmart.org',
            to_addr=u'root@votesmart.org',
            subject=u'Backup Summary for %s' % config['hostname'],
            text_body="\n".join(email_log)
        )

        # Send it
        envelope.send(config['smtp_host'], login=config['smtp_login'],
                  password=config['smtp_password'], tls=config['smtp_tls'])

    if config['verbose']:
        print('Complete!')

if __name__ == '__main__':
    main()