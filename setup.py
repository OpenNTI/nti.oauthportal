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
    'nti.common @ git+ssh://git@github.com/NextThought/nti.common',
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
    version='0.0',
    description='oauthportal',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
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
    },
)
