Bernard
=======

A minimalistic incremental backup script using tar files as the storage format.

Example
-------
`home.bernard`:
    series 0
    backup /home/john
    backup /var/mediaserver.db
    whitelist .db .png .jpg .jpeg
    whitelist .rtf .odt .doc .txt

[john@home]$ ./bernard.py b home

Options
-------
./bernard.py [ACTION] [CONFIG]
ACTION may be one of:
* `b`
    * Backup
* `r`
    * Restore

Configuration
-------------
* `series`
    * Positive integer
    * Version number of the backup.  Increment to avoid trampling over previous
    backups.
* `backup`
    * String
    * Path to back up--multiple backup directives are supported.	
* `blacklist`
    * Space-seperated string
    * File extensions that should not be backed up.
* `whitelist`
    * Space-seperated string
    * File extensions that should be backed up, overriding blacklist.  If only
    the whitelist is given, only file types listed will be processed.

In the last two directives, `blacklist` and `whitelist`, the special value
`none` is accepted as an option.  This will catch any files with no extension.

To run unit-tests:
    cd tests
    ./tests.py
