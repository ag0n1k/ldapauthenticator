from setuptools import setup

setup(
    name='jupyterhub-ldapauthenticator-fork',
    version='1.0.1',
    description='Fork of LDAP Authenticator for JupyterHub by Yuvipanda',
    url='https://github.com/ag0n1k/ldapauthenticator',
    author='ag0n1k',
    author_email='ag0n1kness@gmail.com',
    license='3 Clause BSD',
    packages=['ldapauthenticator'],
    install_requires=[
        'ldap3',
    ]
)
