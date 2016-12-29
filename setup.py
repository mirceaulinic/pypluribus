# Copyright 2016 CloudFlare, Inc. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from setuptools import setup, find_packages
from pip.req import parse_requirements
import uuid

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())

reqs = [str(ir.req) for ir in install_reqs]

version = '0.3.1'

setup(
    name                 = 'pyPluribus',
    version              = version,
    packages             = find_packages(),
    platforms            = 'any',
    install_requires     = reqs,
    include_package_data = True,
    description          = 'Python API to interact with Pluribus devices',
    long_description     = 'Python API to interact with Pluribus devices',
    author               = 'Mircea Ulinic',
    author_email         = 'mirucha@cloudflare.com',
    url                  = 'https://github.com/mirceaulinic/pypluribus', # use the URL to the github repo
    download_url         = 'https://github.com/mirceaulinic/pypluribus/tarball/%s' % version,
    keywords             = ['Pluribus', 'networking'],
    license              = 'Apache 2.0',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
      ]
)
