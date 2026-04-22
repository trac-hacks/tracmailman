import os.path
import re
import subprocess as sub

# from trac.config import ListOption
from trac.core import *
from trac.web import chrome
from trac.web.chrome import INavigationContributor, ITemplateProvider
from trac.web.main import IRequestHandler
from trac.perm import IPermissionRequestor
from trac.util.html import Markup

from bs4 import BeautifulSoup
from bs4.element import Tag as bs4Tag


def authenticated(req):
    """
    Verify the user is logged in
    """
    if (not req.session.authenticated) or (req.authname == 'anonymous'):
        chrome.add_warning(req, 'Please log in')
        return False
    return True


class _MailmanPluginCore(Component):
    """Common methods for all components, to prevent code reuse.
    """
    _mail_archive_path = None
    _private_lists = None
    _private_archives = None
    _public_archives = None

    # IPermissionRequestor methods
    def get_permission_actions(self):
        return ['MAILMAN_VIEW', ('MAILMAN_ADMIN', ['MAILMAN_VIEW'])]

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('tracmailman', resource_filename(__name__, 'templates'))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    # Other common functionality
    def mail_archive_path(self):
        if self._mail_archive_path is None:
            path = self.env.config.get('tracmailman', 'mail_archive_path')
            if path[-1] != '/':
                path += '/'
            self._mail_archive_path = path
        return self._mail_archive_path

    def private_lists(self):
        if self._private_lists is None:
            self._private_lists = self.env.config.getlist('tracmailman', 'private_lists')
        return self._private_lists

    def private_archives(self):
        if self._private_archives is None:
            self._private_archives = list()
            for a in os.listdir(os.path.join(self.mail_archive_path(), 'private')):
                if a not in self.private_lists() and a[-4:] != "mbox":
                    self._private_archives.append(a)
        return self._private_archives

    def public_archives(self):
        if self._public_archives is None:
            self._public_archives = list()
            for a in os.listdir(os.path.join(self.mail_archive_path(), 'public')):
                if a not in self.private_lists() and a[-4:] != "mbox" and a not in self.private_archives():
                    self._public_archives.append(a)
        return self._public_archives

    def mail_archives(self):
        return list(sorted(self.private_archives() + self.public_archives()))


class MailManPluginIndex(_MailmanPluginCore):
    """
    The main page of the TracMailman plugin. This displays the search box,
    with a drop-down list of all the mailing lists to search by, as well as
    a list of the mailing archives for manual browsing.
    """
    implements(INavigationContributor, IRequestHandler, ITemplateProvider, IPermissionRequestor)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return 'tracmailman'

    def get_navigation_items(self, req):
        """
        Display a tab for TracMailMan at the top nav bar
        """
        if req.perm.has_permission("MAILMAN_VIEW"):
            yield 'mainnav', 'tracmailman', Markup('<a href="%s">Mailing Lists</a>' % (self.env.href.tracmailman()))
        else:
            yield 'mainnav', 'tracmailman', None

    # IRequestHandler methods
    def match_request(self, req):
        """
        This plugin handles requests for the path
        example.com/trac_top_dir/tracmailman/browser/
        """
        return re.match(r'^/tracmailman$', req.path_info)

    def process_request(self, req):
        req.perm.require("MAILMAN_VIEW")
        # The full path to where the mailman archives are stored

        data = {}
        data['title'] = 'Mailing List Search'
        # The default content is an error message. If the code below
        # is successful, it will replace the error with real content
        data['contents'] = 'An error has occured. Please hit "Back" on your browser and try again.'
        data['authenticated'] = authenticated(req)
        if not data['authenticated']:
            return 'tracmailman.html', data

        # The lists of mailing list archives to be displayed.
        data['priv_archives'] = self.private_archives()
        data['pub_archives'] = self.public_archives()
        data['mail_archives'] = self.mail_archives()

        return 'tracmailman.html', data


class MailManPluginBrowser(_MailmanPluginCore):
    """
    Takes a request and serves the correct document.  A request such
    as
    example.com/trac/tracmilman/browser/private/example_list/23.html
    would be understood to be a request for example_list's private
    archive, email message 23. Other than mail messages, a user can
    also request indices such as thread.html, subject.html,
    author.html and date.html . These are all documents generated by
    MailMan's Pipermail.

    The plugin will first verify that this user is a member of
    example_list. Then it will load the HTML document from disk by
    looking in the path specified by the mail_archive_path variable in
    trac.ini , and keep only the HTML tags between the <body></body>.

    This data is fed through a HTML sanitizer that comes with
    Trac/Genshi, and finally, the sanitized HTML is put in a Trac
    template to preserve the look and feel of the Trac interface.

    """
    implements(IRequestHandler, ITemplateProvider, IPermissionRequestor)

    # IRequestHandler methods
    def match_request(self, req):
        """
        This plugin handles requests for the path
        example.com/trac_top_dir/tracmailman/browser/
        """
        return re.match(r'^/tracmailman/browser/', req.path_info)

    def process_request(self, req):
        req.perm.require("MAILMAN_VIEW")
        # This is a workaround for bug: http://trac.edgewall.org/ticket/5628
        # reload(sys)
        # if sys.getdefaultencoding() == 'ascii':
        #     sys.setdefaultencoding("latin1")
        # End: workaround

        data = {}
        data['title'] = 'Mailing List Archive Browser'
        data['authenticated'] = authenticated(req)
        # Check user is logged in
        if not data['authenticated']:
            return 'tracmailmanbrowser.html', data

        # We won't respond to just anything. Let's use regexps to pull
        # out relevant tokens, and verify the tokens.
        doctypes = '((\d+)|(thread)|(subject)|(author)|(date))'
        result = re.search(r'^/tracmailman/browser/(public|private)/([^/]+)/([^.]+)\.(html|txt|txt\.gz)$', req.path_info)
        if result is None:
            chrome.add_warning(req, 'The URL you requested is does not refer to a valid document')
            return 'tracmailmanbrowser.html', data

        priv     = result.group(1)
        listname = result.group(2)
        docID    = result.group(3)
        extension= result.group(4)

        # Check if user is trying to access a private list
        if listname in self.private_lists():
            chrome.add_warning(req, 'This list is private and not browsable. Please go through the standard Mailman interface.')
            return 'tracmailmanbrowser.html', data

        path = self.mail_archive_path() + priv + '/' + listname + '/' + docID + '.' + extension
        if os.path.isfile(path):
            with open(path, 'r') as archivedFile:
                archivedMail = archivedFile.read()
            if extension == 'html':
                # html = HTML(archivedMail, encoding='utf-8')
                # At this point, the HTML document is turned into a Genshi
                # object. For more info on how to transform the HTML
                # object using Genshi:
                # http://genshi.edgewall.org/wiki/ApiDocs
                #
                # sanitized = html.select('body/*') | HTMLSanitizer()
                # contents = sanitized.render('html')
                soup = BeautifulSoup(archivedMail, 'html.parser')
                contents = '\n'.join([str(t) for t in filter(lambda x: isinstance(x, bs4Tag), soup.body.children)])
                contents = re.sub(r'<a name=.+?a>', "", contents)
                data['contents'] = Markup(contents)
                data['title'] += " - " + listname
                return 'tracmailmanbrowser.html', data
            else:
                req.send_response(200)
                if extension == 'txt':
                    req.send_header('Content-Type', 'text/plain')
                else:
                    req.send_header('Content-Type', 'application/x-gzip')
                req.send_header('Content-Length', len(archivedMail))
                req.end_headers()
                req.write(archivedMail)

        else:
            if docID in ['thread', 'subject', 'author', 'date']:
                chrome.add_warning(req,
                                   """You requested a mail index page
                                   that could not be found.  It is
                                   possible that there are currently
                                   no mail messages archived, so no
                                   index has been created."""
                                   )
            else:
                chrome.add_warning(req, 'The mail message that you requested cannot be found')

            return 'tracmailmanbrowser.html', data


class TracMailManSearchPlugin(_MailmanPluginCore):
    implements(IRequestHandler, ITemplateProvider, IPermissionRequestor)

    # swishFormat = '{"title": "%t", "path": "%p", "description": "%d"}\\n'
    swishFormat = '||%t||%p||%d||\\n'
    titleRegex = re.compile(r'^\[(.+?)\s(\d+)\].*')

    # IRequestHandler methods
    def match_request(self, req):
        """
        This plugin handles requests for the path
        example.com/trac_top_dir/tracmailman/search
        """
        return req.path_info == '/tracmailman/search'

    def process_request(self, req):
        req.perm.require("MAILMAN_VIEW")
        # This is a workaround for bug: http://trac.edgewall.org/ticket/5628
        # reload(sys)
        # if sys.getdefaultencoding() == 'ascii':
        #     sys.setdefaultencoding("latin1")
        # End: workaround

        # The full path to where the mailman archives are stored
        mail_archive_path = self.mail_archive_path()

        # The full path to where the indices are stored
        search_index_path = self.env.config.get('tracmailman', 'search_index_path')
        if search_index_path[-1] != '/':
            search_index_path += '/'

        # The private archives not to be searched
        private_lists = self.private_lists()

        data = {}
        data['title'] = 'Mailing List Search'
        data['authenticated'] = authenticated(req)

        # Check the user is logged in
        if not data['authenticated']:
            return 'tracmailmansearch.html', data

        # Add mailing lists to be displayed in the search
        data['mail_archives'] = self.mail_archives()

        # Grab the search query
        query = req.args.get('query', None)
        if query is not None and query.strip():
            data['query'] = query
        else:
            chrome.add_warning(req, 'Please enter a query.')
            return 'tracmailmansearch.html', data

        # Grab which list the user searched
        search_list = req.args.get('search_list', None)
        if search_list is not None and search_list.strip():
            data['search_list'] = search_list
        else:
            chrome.add_warning(req, 'Please select a list to search from.')
            return 'tracmailmansearch.html', data

        # Get the search index for the particular list the user selected
        swishIndex  = search_index_path + search_list + '-index.swish-e'

        swishCommand = ['/usr/local/bin/swish-e', '-f', swishIndex,
                        '-w', query,
                        '-x', self.swishFormat]

        proc = sub.Popen(swishCommand, stdout=sub.PIPE, stderr=sub.PIPE)
        out, err = proc.communicate()
        results = out.decode('latin1')
        if proc.returncode != 0:
            if 'Could not open the index file' in results:
                chrome_warn = f'Search index for "{search_list}" not found. It is possible that this mailing list has never been used. Browse "{search_list}" on the main Mailing Lists page to confirm.'
            else:
                chrome_warn = f'Unknown error. Message was "{results}".'
            chrome.add_warning(req, chrome_warn)
            return 'tracmailmansearch.html', data

        if 'err: no results' in results:
            data['numHits'] = 0
            chrome.add_warning(req, f'No results for "{query}".')
            return 'tracmailmansearch.html', data

        ordered_results = self._parse_results(results, search_list)
        numHits = len(ordered_results)
        data['numHits'] = numHits

        if numHits == 0:
            chrome.add_warning(req, f'No results for "{query}".')
            return 'tracmailmansearch.html', data

        # page and hitsPerPage are to control pagination
        hitsPerPage = 20
        req_page = req.args.get('page', None)
        if req_page is not None:
            # For usability we want to let the user see "page=1", but
            # in reality, this maps to the 0th page
            page = int(req_page) - 1
        else:
            page = 0

        data['currentPage'] = page
        data['maxPage'] = numHits // hitsPerPage
        if numHits % hitsPerPage > 0:
            data['maxPage'] += 1

        data['results'] = []
        firstHit = page * hitsPerPage
        data['firstHit'] = firstHit
        data['lastHit'] = min(firstHit + hitsPerPage, numHits)
        seen = 0
        while((seen < hitsPerPage) and (firstHit + seen < numHits)):
            seen += 1
            sr = ordered_results[firstHit + seen - 1]
            hit = {}
            hit['path'] = 'browser/' + sr['path'].lstrip(mail_archive_path).lstrip('/')
            hit['number'] = firstHit + seen
            hit['title'] = sr['title']
            hit['description'] = sr['description']
            data['results'].append(hit)

        data['title'] += " - " + '"' + query + '"'
        return 'tracmailmansearch.html', data

    def _parse_results(self, results, search_list):
        """Parse results of a SwishE search.

        Parameters
        ----------
        results : :class:`str`
            The results returned by :command:`swish-e`.
        search_list : :class:`str`
            The name of the list in the search.

        Returns
        -------
        :class:`list`
            A :class:`list` of :class:`dict` with the parsed data.
        """
        private_lists = self.private_lists()
        lines = results.split('\n')
        hits = 0
        ordered_results = list()
        for line in lines:
            ll = line.strip()
            # if ll.startswith('# Number of hits:'):
            #     hits = int(ll.split(':')[1].strip())
            if ll.startswith('||'):
                data = dict()
                columns = ll.split('||')
                data['title'] = columns[1]
                data['path'] = columns[2]
                data['description'] = columns[3]
                regex = self.titleRegex.match(data['title'])
                if regex is None:
                    continue
                list_name = regex.group(1)
                list_num = int(regex.group(2))
                # If we searched all the mailing lists, remove the ones from the private lists
                if search_list == 'all' and list_name in private_lists:
                    continue
                data['list_name'] = list_name
                data['list_number'] = list_num
                ordered_results.append(data)
        # if hits == len(ordered_results):
        #     pass
        return list(sorted(ordered_results, key=lambda x: x['list_number'], reverse=True))
