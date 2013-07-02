===========
TracMailman
===========

About
-----

TracMailman is a plugin for Trac that integrates with Mailman,
allowing users to browse mailing list archives and search the
mailing list, all from a tab within Trac.

Created by Spencer Fang <sfang@lbl.gov> and Theron Ji <tji@lbl.gov>

Contents
--------

::

    README.rst
    setup.py
    swish-e.config
    swish-e.sh
    trac-mailman.ini
    tracmailman/
    tracmailman/__init__.py
    tracmailman/paths.py
    tracmailman/web_ui.py
    tracmailman/templates/
    tracmailman/templates/tracmailman.html
    tracmailman/templates/tracmailmanbrowser.html
    tracmailman/templates/tracmailmanoptions.html
    tracmailman/templates/tracmailmansearch.html

Requirements
------------

- Trac (0.11.1 recomended)
- MailMan (2.1.11 recomended)
- Swish-e (2.4.5 or above recommended)
- `Python Swish-e bindings`_ (0.5 or above recommended)


Functionality
-------------

This plugin adds a TracMailman tab inside of trac. Users logged in
will be able to click on this tab and be taken to a search page,
where they can choose to search a particular mailing list (or 'All'),
or browse through the mailing lists, all within trac.

This plugin handles privacy concerns by looking at a manually specified
list of mailing lists inside the trac.ini configuration file, and
preventing searches or browsing on those lists. NOTE: this functionality
is disabled for ALL users, including those who may have the proper
permissions. It is conceivable that this feature is changed in later
versions of the plugin.


Installation
------------

1. Verify requirements have been met!
2. In the plugin directory, run ``python setup.py bdist_egg`` to produce
   a .egg file under the dist/ directory.
3. Copy the .egg into the plugins/ directory under the Trac project
4. Edit the trac-mailman.ini file appropriately (see `Configuring
   trac.ini`_ below)
5. Add the contents of trac-mailman.ini to the trac.ini file inside
   your Trac project (default location under yourproject/conf/)
6. Set the appropriate variables in swish-e.sh. (see 'Configuring
   Swish-e' below). Run it to create the index files[*]_.
7. Restart the Trac daemon[*]_ - the plugin should now be functional
8. Set up a cron job or some script to periodically run swish-e.sh to
   re-index the archives to keep the search up-to-date[*]_.


Configuring trac.ini
--------------------

In the trac.ini configuration file, 3 items need to be specified under
the [tracmailman] section:

private_lists
    As mentioned above, this will be a comma separated
    list of mailing lists that should not be made publicly searchable or
    browsable. Obsolete lists that still remain archived but are no longer
    of any use may also be put here. This is NOT related to the private
    directory created by default under /var/lib/mailman/archives/private.
    Defaults to nothing.

mail_archive_path
    This should be set to the full path to the top-
    level directory of where the mailman archives are stored. Default
    location is at /var/lib/mailman/archives/

search_index_path
    This should be set to the full path of where
    the search indices created by Swish-e are located. This MUST be the
    same as the INDEX_LOCATION variable in the swish-e.sh script.


Configuring Swish-e
-------------------

To use the search feature of the plugin, you must have Swish-e installed
and an index file to search in. The config file for Swish-e is included,
(swish-e.config), as well as a shell script (swish-e.sh). The swish-e.config
file should NOT be changed, but modifications should be made to the
swish-e.sh script to tell it 1) where the config file is, and 2) where to
store the indices created by the search engine.

.. [*] The private mailman archive (/var/lib/mailman/archives/private)
    has read permission restricted to root or the mailman group, by default. In
    order for Trac to be able to read these files, and the Swish-e script to be
    able index these files, they must be run with appropriate permissions.
.. _`Python Swish-e bindings`: http://pypi.python.org/pypi/Swish-E/0.5
