#!/usr/bin/env python
#
# Copyright 2019 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Deploys Fuchsia packages to a package repository in a Fuchsia
build output directory."""

import pkg_repo
import argparse
import os
import sys


# Populates the GDB-standard symbol directory structure |build_ids_path| with
# the files and build IDs specified in |ids_txt_path|.
def InstallSymbols(ids_txt_path, build_ids_path):
  for entry in open(ids_txt_path, 'r'):
    build_id, binary_relpath = entry.strip().split(' ')
    binary_abspath = os.path.abspath(
        os.path.join(os.path.dirname(ids_txt_path), binary_relpath))
    symbol_dir = os.path.join(build_ids_path, build_id[:2])
    symbol_file = os.path.join(symbol_dir, build_id[2:] + '.debug')

    if not os.path.exists(symbol_dir):
      os.makedirs(symbol_dir)

    if os.path.islink(symbol_file) or os.path.exists(symbol_file):
      # Clobber the existing entry to ensure that the symlink's target is
      # up to date.
      os.unlink(symbol_file)

    os.symlink(os.path.relpath(binary_abspath, symbol_dir), symbol_file)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--package',
                      action='append',
                      required=True,
                      help='Paths to packages to install.')
  parser.add_argument('--fuchsia-out-dir',
                      required=True,
                      help='Path to a Fuchsia build output directory. '
                      'Setting the GN arg '
                      '"default_fuchsia_build_dir_for_installation" '
                      'will cause it to be passed here.')
  args = parser.parse_args()
  assert args.package

  fuchsia_out_dir = os.path.expanduser(args.fuchsia_out_dir)
  repo = pkg_repo.ExternalPkgRepo(os.path.join(fuchsia_out_dir, 'amber-files'))
  print('Installing packages and symbols in package repo %s...' %
        repo.GetPath())

  for package in args.package:
    repo.PublishPackage(package)
    InstallSymbols(os.path.join(os.path.dirname(package), 'ids.txt'),
                   os.path.join(fuchsia_out_dir, '.build-id'))

  print('Installation success.')

  return 0


if __name__ == '__main__':
  sys.exit(main())
