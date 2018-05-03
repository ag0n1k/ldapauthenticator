# ldapauthenticator
Fork of LDAP Authenticator Plugin for JupyterHub. Tested on Active Directory.

## Installation ##

git clone and run setup.

## Requirements ##

Tested with python 3.4 with Active Directory.
In this fork there is algorithm:

-- user insert his `{username}` (ex: `sAMAccountName`) with `{password}`

-- next we connect to AD with `{bind_user}` credentials 

-- search this account by `{filter_base}` (ex: `sAMAccountName`)

-- if it exist -> bind AD with founded user DN and `{password}` the answer is `True/False` and `groups`

-- search first match of founded `groups` in `{allowed_groups}`

-- return `{username}` or `None`  

## Usage ##

You can enable this authenticator with the folling lines in your
`jupyter_config.py`:

```python
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
```

### Required configuration ###

At least the following two configuration options must be set before
the LDAP Authenticator can be used:

#### `LDAPAuthenticator.server_address` ####

Address of the LDAP Server to contact. Use like `ldap://ldap.test.local.`

#### `LDAPAuthenticator.server_user` ####

Bind user of the LDAP Server to contact.

#### `LDAPAuthenticator.server_password` ####

Bind user password of the LDAP Server to contact. 

#### `LDAPAuthenticator.filter_base` ####

The filter pattern contains the attribute of user that it will place in username field. 

```python
c.LDAPAuthenticator.filter_base = '(&(objectClass=*)(sAMAccountName={0}))'
```

#### `LDAPAuthenticator.search_base` ####

The scope where we are looking for the user. If you do not know leave the whole (DC) 

```python
c.LDAPAuthenticator.user_search_base = 'DC=test,DC=local'
```

### Optional configuration ###

#### `LDAPAuthenticator.allowed_groups` ####

`!!!Only group names in this fork is needed!!!`

LDAP groups whose members are allowed to log in. This must be
set to either empty `[]` (the default, to disable) or to a list of
groups names.

As an example, to restrict access only to people in groups
`researcher` or `operations`,

```python
c.LDAPAuthenticator.allowed_groups = [
    'researcher',
    'operations'
]
```

#### `LDAPAuthenticator.valid_username_regex` ####

All usernames will be checked against this before being sent
to LDAP. This acts as both an easy way to filter out invalid
usernames as well as protection against LDAP injection attacks.

By default it looks for the regex `^[a-z][.a-z0-9_-]*$` which
is what most shell username validators do.

#### `LDAPAuthenticator.use_ssl` ####

Boolean to specify whether to use SSL encryption when contacting
the LDAP server. Highly recommended that this be left to `True`
(the default) unless there are very good reasons otherwise.

#### `LDAPAuthenticator.server_port` ####

Port to use to contact the LDAP server. Defaults to 389 if no SSL
is being used, and 636 is SSL is being used. Do not forget about
global configuration 3268 (3269).

#### `LDAPAuthenticator.bind_dn_template` ####

`!!!Do not used in this fork!!!`

Template to use to generate the full dn for a user from the human readable
username. For example, if users in your LDAP database have DN of the form
`uid=Yuvipanda,ou=people,dc=wikimedia,dc=org` where Yuvipanda is the username,
you would set this config item to be:

```
c.LDAPAuthenticator.bind_dn_template = 'uid={username},ou=people,dc=wikimedia,dc=org'
```

Don't forget the preceeding `c.` for setting configuration parameters! JupyterHub
uses [traitlets](https://traitlets.readthedocs.io) for configuration, and the `c` represents the [config object](https://traitlets.readthedocs.io/en/stable/config.html).

The `{username}` is expanded into the username the user provides.


## Compatibility ##

This has been tested against an Active Directory server, with the client
running Python 3.4.


## Future ##

Delete all unneeded params.