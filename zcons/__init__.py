# ZCons
#
# Zimmermann's SCons wrapper
#
# Copyright (C) 2016 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# ZCons is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZCons is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ZCons. If not, see <http://www.gnu.org/licenses/>.

"""
Zimmermann's SCons wrapper.

Checks availability of SCons and, if not found, implicitly installs SCons as
local Python egg.

Defines :func:`zetup.scons` for running SCons sub-processes

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys

import zetup
from zetup.version import Version
from path import Path
from pkg_resources import get_distribution

from .error import ZConsError, ZConsSConsError, ZConsResolveSConsError

zetup.toplevel(__name__, [
    'Environment',
    'ZConsError', 'ZConsSConsError', 'ZConsResolveSConsError',
    'scons',
])
# __call__=lambda *args, **options: scons(*args, **options)


REQUIRES_SCONS = "SCons >=  3.0.0"

zetup.resolve([REQUIRES_SCONS])

SCONS = get_distribution(REQUIRES_SCONS)

SCONS_ROOT = Path(SCONS.location) / ("scons")
if Version(SCONS.version) < '3.0.3':
    SCONS_ROOT += "-%s" % SCONS.version

if not SCONS_ROOT.exists():
    raise ZConsResolveSConsError(reason=(
        "SCons package root does not exist: {}".format(SCONS_ROOT)))

sys.path.insert(0, str(SCONS_ROOT))

import SCons  # pylint: disable=import-error

if SCons.__version__ != SCONS.version:
    raise ZConsResolveSConsError(reason=(
        "SCons.__version__ {} doesn't match {!r}"
        .format(SCons.__version__, SCONS)))

print("SCons package root: {}".format(SCONS_ROOT))

from SCons.Environment import Environment  # pylint: disable=import-error


def scons(*args, **options):
    """
    Run SCons as separate sub-process through ``sys.executable``.

    :param args:
        SCons command line arguments
    :param options:
        SCons variables and keyword arguments for ``zetup.call``

    All `options` starting with upper case letters are used as SCons variables
    and appended to `args`

    See ``zetup.call`` and ``subprocess.call`` for info about general
    `options`
    """
    args = list(args)
    for name in list(options):
        if name[0].isupper():
            args.append('%s=%s' % (name, options.pop(name)))

    if zetup.call([
            sys.executable, '-c', "__import__('SCons.Script').Script.main()"
    ] + args, **options):
        raise ZConsSConsError(args=args)


def scons_debug(*args, **options):
    """
    Run SCons with ``--debug=pdb``.

    See :func:`zcons.scons` for info about arguments and the sub-process
    """
    args = list(args)
    for name in list(options):
        if name[0].isupper():
            args.append('%s=%s' % (name, options.pop(name)))

    if zetup.call([
            sys.executable, '-c',
            "__import__('SCons.Script').Script.main()",
            "--debug=pdb"
    ] + args, **options):
        raise ZConsSConsError(args=args)


scons.debug = scons_debug
