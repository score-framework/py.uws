# Copyright © 2017,2018 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

import os
import platform

from setuptools import setup
from distutils.extension import Extension
from Cython.Build import cythonize

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

upstream_dir = os.path.join(here, "lib", "uWebSockets", "src")
upstream_src = [os.path.join(upstream_dir, f)
                for f in os.listdir(upstream_dir)
                if f.split(".")[-1] in ("cpp", "cxx", "c")]
upstream_headers = [os.path.join(upstream_dir, f)
                    for f in os.listdir(upstream_dir)
                    if f.split(".")[-1] in ("hpp", "hxx", "h")]

include_dirs = [upstream_dir]
extra_compile_args = ['-std=c++11']
if platform.system() == 'Darwin':
    include_dirs.append('/usr/local/opt/openssl/include')
    extra_compile_args.append('-stdlib=libc++')

setup(
    name='score.uws',
    version='0.0.4',
    description='HTTP handler of The SCORE Framework',
    long_description=README,
    author='strg.at',
    author_email='score@strg.at',
    url='http://score-framework.org',
    keywords='score framework websocket',
    packages=['score', 'score.uws', 'score.uws._hub'],
    namespace_packages=['score'],
    zip_safe=False,
    license='LGPL',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General '
            'Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    install_requires=[
        'score.ctx',
        'score.init >= 0.3',
        'score.ws',
    ],
    ext_modules=cythonize([
        Extension(
            "score.uws._hub.hub",
            define_macros=[
                ("USE_LIBUV", "1"),
            ],
            include_dirs=include_dirs,
            extra_compile_args=extra_compile_args,
            sources=["score/uws/_hub/hub.pyx"] + upstream_src,
            language="c++",
            libraries=['pthread', 'ssl', 'crypto', 'z', 'uv'],
        ),
    ])
)
