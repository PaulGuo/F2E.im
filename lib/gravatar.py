#!/usr/bin/env python3
#
# python-gravatar - Copyright (c) 2009 Pablo Seminario
# This software is distributed under the terms of the GNU General
# Public License
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
A library that provides a Python 3 interface to the Gravatar APIs.
"""

__author__ = 'Pablo SEMINARIO <pabluk@gmail.com>'
__version__ = '0.2'

# import xmlrpc.client
from hashlib import md5


class Gravatar(object):
    """
    This class encapsulates all the unauthenticated methods from APIs.

    Gravatar Image Requests http://en.gravatar.com/site/implement/images/
    Gravatar Profile Requests http://en.gravatar.com/site/implement/profiles/

    """

    def __init__(self, email):
        self.email = sanitize_email(email)
        self.email_hash = md5_hash(self.email)

    def get_image(self, size=80, filetype_extension=True):
        """
        Returns an URL to the user profile image.
        """
        base_url = 'http://www.gravatar.com/avatar/' \
            '{hash}{extension}?size={size}'
        extension = '.jpg' if filetype_extension else ''

        data = {
            'hash': self.email_hash,
            'extension': extension,
            'size': size,
        }
        return base_url.format(**data)

    def get_profile(self, data_format=''):
        """
        Returns an URL to the profile information associated with the
        Gravatar account.
        """
        base_url = 'http://www.gravatar.com/{hash}{data_format}'

        valid_formats = ['json', 'xml', 'php', 'vcf', 'qr']
        if data_format and data_format in valid_formats:
            data_format = '.%s' % data_format

        data = {
            'hash': self.email_hash,
            'data_format': data_format,
        }
        return base_url.format(**data)


class GravatarXMLRPC(object):
    """
    This class encapsulates all the authenticated methods from the XML-RPC API.

    API details: http://en.gravatar.com/site/implement/xmlrpc
    """
    API_URI = 'https://secure.gravatar.com/xmlrpc?user={0}'

    def __init__(self, email, apikey='', password=''):
        self.apikey = apikey
        self.password = password
        self.email = sanitize_email(email)
        self.email_hash = md5_hash(self.email)
        self._server = xmlrpc.client.ServerProxy(
            self.API_URI.format(self.email_hash))

    def exists(self, hashes):
        """Checks whether a hash has a gravatar."""
        response = self._call('exists', params={'hashes': hashes})
        results = {}
        for key, value in response.items():
            results[key] = True if value else False
        return results

    def addresses(self):
        """Gets a list of addresses for this account."""
        return self._call('addresses')

    def userimages(self):
        """Returns a dict of userimages for this account."""
        return self._call('userimages')

    def test(self):
        """Test the API."""
        return self._call('test')

    def _call(self, method, params={}):
        """Call a method from the API, gets 'grav.' prepended to it."""

        args = {
            'apikey': self.apikey,
            'password': self.password,
        }
        args.update(params)

        try:
            return getattr(self._server, 'grav.' + method, None)(args)
        except xmlrpc.client.Fault as error:
            error_msg = "Server error: {1} (error code: {0})"
            print(error_msg.format(error.faultCode, error.faultString))


def sanitize_email(email):
    """
    Returns an e-mail address in lower-case and strip leading and trailing
    whitespaces.

    >>> sanitize_email(' MyEmailAddress@example.com ')
    'myemailaddress@example.com'

    """
    return email.lower().strip()


def md5_hash(email):
    """
    Returns a md5 hash from an e-mail address.

    >>> md5_hash('myemailaddress@example.com')
    '0bc83cb571cd1c50ba6f3e8a78ef1346'

    """
    return md5(email.encode('utf-8')).hexdigest()
