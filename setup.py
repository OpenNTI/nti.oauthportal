import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'plaster_pastedeploy',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'gunicorn[gevent]',
    'automatic',
    'itsdangerous',
    'requests',
    'zope.cachedescriptors',
    'nti.common @ git+ssh://git@github.com/OpenNTI/nti.common',
    'zope.component',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest >= 3.7.4',
    'pytest-cov',
    'PyHamcrest',
    'fudge',
]

tools_require = [
    'ipython',
]

setup(
    name='nti.oauthportal',
    version_format='{tag}.dev{commits}+{sha}',
    setup_requires=['very-good-setuptools-git-version'],
    description='oauthportal',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['nti'],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
        'tools': tools_require,
    },
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'nti_pserve = nti.oauthportal.authentication.nti_gunicorn:main',
        ],
        'paste.app_factory': [
            'main = nti.oauthportal.authentication:main',
        ],
        "paste.filter_app_factory": [
            "ops_ping = nti.oauthportal.authentication.views.ping:ping_handler_factory",
        ],
    },
)
