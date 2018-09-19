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

zetup.toplevel(__name__, [
    'Environment',
    'ZConsError', 'ZConsSConsError', 'ZConsResolveSConsError',
    'scons',
])
# __call__=lambda *args, **options: scons(*args, **options)

from distutils.errors import DistutilsError
from setuptools.dist import Distribution
from pkg_resources import get_distribution, working_set, \
    DistributionNotFound, VersionConflict

from path import Path

from .error import ZConsError, ZConsSConsError, ZConsResolveSConsError


def resolve_scons():
    # called below
    """Check for installed SCons and install as local egg if not found.

    - Automatically called on ``import zcons``.
    - Returns :class:`pkg_resources.Distribution` instance for SCons.
    """
    # don't pollute stdout with SCons installation output
    stdout = sys.__stdout__
    sys.stdout = sys.__stdout__ = sys.__stderr__

    print("Resolving SCons...")
    try:
        dist = get_distribution('SCons >= 3.0')
    except (DistributionNotFound, VersionConflict):
        try:
            dist = Distribution().fetch_build_egg('SCons >= 3.0')
        except DistutilsError as exc:
            raise ZConsResolveSConsError(reason=exc)
        working_set.entries.insert(0, dist.location)
        working_set.by_key[dist.key] = dist
    pkgroot = Path(dist.location) / ('scons-%s' % dist.version)
    if not pkgroot.exists():
        raise ZConsResolveSConsError(reason=(
            "SCons package root does not exist: {}".format(pkgroot)))
    sys.path.insert(0, str(pkgroot))
    print(repr(dist))
    print("SCons package root: {}".format(pkgroot))

    sys.stdout = sys.__stdout__ = stdout
    return dist


SCONS = resolve_scons()


from SCons.Environment import Environment


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
    if zetup.call(
            [sys.executable, '-c',
             "__import__('SCons.Script').Script.main()"] +
            args, **options):
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
    if zetup.call(
            [sys.executable, '-c',
             "__import__('SCons.Script').Script.main()",
             "--debug=pdb"] +
            args, **options):
        raise ZConsSConsError(args=args)


scons.debug = scons_debug
