import ldap3
import re

from jupyterhub.auth import Authenticator
from tornado import gen
from traitlets import Unicode, Int, Bool, Union, List


class LDAPAuthenticator(Authenticator):
    server_address = Unicode(
        config=True,
        help='Address of LDAP server to contact'
    )
    server_port = Int(
        config=True,
        help='Port on which to contact LDAP server',
    )
    server_user = Unicode(
        config=True,
        help='Bind username'
    )
    server_password = Unicode(
        config=True,
        help='Bind user password'
    )

    def _server_port_default(self):
        if self.use_ssl:
            return 636  # default SSL port for LDAP
        else:
            return 389  # default plaintext port for LDAP

    use_ssl = Bool(
        True,
        config=True,
        help='Use SSL to encrypt connection to LDAP server'
    )

    bind_dn_template = Unicode(
        config=True,
        help="""
        Template from which to construct the full dn
        when authenticating to LDAP. {username} is replaced
        with the actual username.

        Example:

            uid={username},ou=people,dc=wikimedia,dc=org
        """
    )

    allowed_groups = List(
        config=True,
        help="List of LDAP Group DNs whose members are allowed access"
    )

    valid_username_regex = Unicode(
        r'^[a-z][.a-z0-9_-]*$',
        config=True,
        help="""Regex to use to validate usernames before sending to LDAP

        Also acts as a security measure to prevent LDAP injection. If you
        are customizing this, be careful to ensure that attempts to do LDAP
        injection are rejected by your customization
        """
    )

    lookup_dn = Bool(
        False,
        config=True,
        help='Look up the user\'s DN based on an attribute'
    )

    user_search_base = Unicode(
        config=True,
        help="""Base for looking up user accounts in the directory.

        Example:

            ou=people,dc=wikimedia,dc=org
        """
    )

    user_attribute = Unicode(
        config=True,
        help="""LDAP attribute that stores the user's username.

        For most LDAP servers, this is uid.  For Active Directory, it is
        sAMAccountName.
        """
    )
    filter_base = Unicode(
        config=True,
        help="""LDAP attribute to search users
        example: (&(objectClass=*)(sAMAccountName={0}))
        """
    )


    @gen.coroutine
    def authenticate(self, handler, data):
        def connect_via_bind_user(user, password, address, port, use_ssl=False):
            server = ldap3.Server(address, port=port, use_ssl=use_ssl, get_info=ldap3.ALL)
            connection = ldap3.Connection(server, user=user, password=password)
            return connection

        def search_user_dn(connection, search_base, filter, user, attrs=['memberOf']):
            connection.search(search_base=search_base, search_scope=ldap3.SUBTREE, search_filter=filter.format(user), attributes=attrs)
            tmp = connection.response.pop()
            dn_ = tmp.get('dn')
            groups = tmp.get('attributes').get('memberOf')

            return dn_, [el.split(',')[0].split('=').pop() for el in groups]

        username = data['username']
        password = data['password']

        # Protect against invalid usernames as well as LDAP injection attacks
        if not re.match(self.valid_username_regex, username):
            self.log.warn('Invalid username')
            return None

        # No empty passwords!
        if password is None or password.strip() == '':
            self.log.warn('Empty password')
            return None

        connection = connect_via_bind_user(user=self.server_user, password=self.server_password,
                                           address=self.server_address, port=self.server_port, use_ssl=self.use_ssl)
        connection.bind()

        dn_, user_groups = search_user_dn(connection=connection, search_base=self.user_search_base, filter=self.filter_base, user=username)
        self.log.debug('Found dn: {}'.format(dn_))
        self.log.debug('Found groups: {}'.format(user_groups))

        conn = connect_via_bind_user(user=dn_, password=password, address=self.server_address, port=self.server_port)
        res = conn.bind()
        self.log.debug('Result of user {} is {} \nAdditional info: {}'.format(username, res, conn.result))

        if not res:
            self.log.warn('Invalid password for user {username}'.format(username=username))
            return None

        if not self.allowed_groups:
            return username

        for allow_g in self.allowed_groups:
            if allow_g in user_groups:
                return username
        self.lof.warn('User {username} is not allowed in groups'.format(username=username))
        return None
