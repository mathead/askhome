# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='askhome',
    packages=['askhome'],
    version='0.1.3',
    author=u'Matěj Hlaváček',
    author_email='hlavacek.matej@gmail.com',
    url='https://github.com/mathead/askhome',
    download_url='https://github.com/mathead/askhome/archive/0.1.tar.gz',
    keywords='',
    description='Alexa Skills Kit library for working with Smart Home Skill API',
    install_requires=[
        'inflection'
    ],
)
