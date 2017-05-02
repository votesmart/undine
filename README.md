# undine
A wrapper for handling multi-archive backups with Borg

## Usage

    usage: undine [-h] [--dry-run] [-v] [-d] [-l LOCKFILE]

    A wrapper for handling multi-archive backups with Borg

    optional arguments:
      -h, --help            show this help message and exit
      --dry-run             Do not actually create archives.
      -v, --verbose         Show output
      -d, --debug           Show debug output
      -l LOCKFILE, --lock-file LOCKFILE
                            Lock file to use

## SSH Configuration

While not strictly required, if you're using SSH to connect to the 
backend, using `~/.ssh/config` will make things much easier.  For 
insance, if using rsync.net, you could do something like the following:

    Host rsync.net
            Hostname example.rsync.net
            IdentityFile /home/user/.ssh/id_rsa.rsync.net
            User 123

## Configuration

Configuration is done through an INI file.  It can be placed in 
`/etc/undine.ini` or `~/.config/undine.ini`.  The one in the user 
directory will take precidence.  The available options are below: 

    [default]
    debug = False
    verbose = False
    repos = 'ssh://rsync.net/path/to/repos'
    notify_email = 'root@example.org'
    lockfile = /tmp/undine.lock

    [smtp]
    host = localhost
    port = 589
    login =
    password =
    tls = true

    [units]
    home = /home
    etc = /etc
    postgres = /var/lib/pgsql