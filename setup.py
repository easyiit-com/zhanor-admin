import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [ 
     'alembic==1.13.1',
        'aniso8601==9.0.1',
        'annotated-types==0.6.0',
        'apispec==6.6.1',
        'apispec-webframeworks==1.1.0',
        'attrs==23.2.0',
        'Babel==2.14.0',
        'bcrypt==4.1.2',
        'Beaker==1.13.0',
        'blinker==1.7.0',
        'Brotli==1.1.0',
        'cachelib==0.9.0',
        'captcha==0.5.0',
        'certifi==2024.2.2',
        'charset-normalizer==3.3.2',
        'click==8.1.7',
        'flasgger==0.9.7.1',
        'Flask==3.0.3',
        'flask-apispec==0.11.4',
        'flask-babel==4.0.0',
        'Flask-Caching==2.3.0',
        'Flask-Compress==1.15',
        'Flask-JWT-Extended==4.6.0',
        'Flask-Login==0.6.3',
        'Flask-RESTful==0.3.10',
        'Flask-SQLAlchemy==3.1.1',
        'Flask-WTF==1.2.1',
        'greenlet==3.0.3',
        'idna==3.7',
        'inflect==7.2.1',
        'iniconfig==2.0.0',
        'itsdangerous==2.2.0',
        'Jinja2==3.1.3',
        'jsonschema==4.22.0',
        'jsonschema-specifications==2023.12.1',
        'Mako==1.3.5',
        'MarkupSafe==2.1.5',
        'marshmallow==3.21.2',
        'mistune==3.0.2',
        'more-itertools==10.2.0',
        'Naked==0.1.32',
        'packaging==24.0',
        'pillow==10.3.0',
        'pluggy==1.5.0',
        'pycryptodome==3.20.0',
        'pydantic==2.7.1',
        'pydantic-core==2.18.2',
        'PyJWT==2.8.0',
        'PyMySQL==1.1.0',
        'pypng==0.20220715.0',
        'pytest==8.2.0',
        'python-dotenv==1.0.1',
        'pytz==2024.1',
        'PyYAML==6.0.1',
        'qrcode==7.4.2',
        'redis==5.0.4',
        'referencing==0.35.1',
        'requests==2.31.0',
        'rpds-py==0.18.1',
        'setuptools==69.5.1',  # 注意：通常不需要显式列出setuptools作为依赖
        'shellescape==3.8.1',
        'six==1.16.0',
        'SQLAlchemy==2.0.29',
        'transaction==4.0',
        'typeguard==4.2.1',
        'typing_extensions==4.11.0',
        'urllib3==2.2.1',
        'webargs==8.4.0',
        'WebOb==1.8.7',
        'Werkzeug==3.0.2',
        'WTForms==3.1.2',
        'zope.interface==6.3',
        'zope.sqlalchemy==3.1',
        'zstandard==0.22.0'
]

tests_require = [
    'WebTest',
    'pytest',
    'pytest-cov',
]


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    with open(version_file) as f:
        return f.read().strip()


__version__ = get_version()

setup(
    name='zhanor_1.0.4',
    version=__version__ ,
    description='flask admin panel',
    long_description='',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: flask',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='zhanor',
    author_email='zhanfish@foxmail.com',
    url='https://github.com/easyiit-com/zhanor-admin',
    keywords='web flask pylons',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = fastapi_admin_pro:main',
        ],
        'console_scripts': [
            'initialize_db=initialize_db:main',
        ],
    },
)
