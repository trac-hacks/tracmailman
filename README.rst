===========
TracMailman
===========

About
-----

TracMailman is a plugin for Trac_ that integrates with Mailman_,
allowing users to browse mailing list archives and search the
mailing list, all from a tab within Trac.

Created by Spencer Fang <sfang@lbl.gov> and Theron Ji <tji@lbl.gov>.
Additional development by Benjamin Weaver <benjamin.weaver@noirlab.edu>.

.. _Trac: https://trac.edgewall.org
.. _Mailman: https://www.list.org

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

- Trac_ (0.11.1 or above recomended)
- Mailman_ (2.1.11 or above recomended)
- Swish-e_ (2.4.5 or above recommended)

.. _Swish-e: http://swish-e.org

Functionality
-------------

This plugin adds a 'Mailing Lists' tab inside of Trac. Users logged in
will be able to click on this tab and be taken to a search page,
where they can choose to search a particular mailing list (or 'All'),
or browse through the mailing lists, all within Trac.

This plugin handles privacy concerns by looking at a manually specified
list of mailing lists inside the trac.ini configuration file, and
preventing searches or browsing on those lists. NOTE: this functionality
is disabled for **all** users, including those who may have the proper
permissions.

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
   Swish-e' below). Run it to create the index files [*]_.
7. Restart the Trac daemon - the plugin should now be functional.
8. Set up a cron job or some script to periodically run swish-e.sh to
   re-index the archives to keep the search up-to-date.

.. [*] The private mailman archive (*e.g.*, ``/var/lib/mailman/archives/private``)
   has read permission restricted to root or the mailman group, by default. In
   order for Trac to be able to read these files, and the Swish-e script to be
   able index these files, they must be run with appropriate permissions.

Configuring trac.ini
--------------------

In the trac.ini configuration file, 3 items need to be specified under
the ``[tracmailman]`` section:

**private_lists**
    As mentioned above, this will be a comma separated
    list of mailing lists that should not be made publicly searchable or
    browsable. Obsolete lists that still remain archived but are no longer
    of any use may also be put here. This is **not** related to the private
    directory created by default under ``/var/lib/mailman/archives/private``.
    Defaults to nothing.

**mail_archive_path**
    This should be set to the full path to the top-
    level directory of where the mailman archives are stored. Default
    location is at ``/var/lib/mailman/archives``.

**search_index_path**
    This should be set to the full path of where
    the search indices created by Swish-e are located. This **must** be the
    same as the ``$INDEX_LOCATION`` variable in the swish-e.sh script.

Configuring Swish-e
-------------------

To use the search feature of the plugin, you must have Swish-e installed
and an index file to search in. The config file for Swish-e is included,
(swish-e.config), as well as a shell script (swish-e.sh). The swish-e.config
file should **not** be changed, but modifications should be made to the
swish-e.sh script to tell it 1) where the config file is, and 2) where to
store the indices created by the search engine.
