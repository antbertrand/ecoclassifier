#!/usr/bin/env bash
# Entrypoint for Django
# Inspired by: https://github.com/docker-library/postgres/blob/master/9.4/docker-entrypoint.sh
# BE CAREFUL, THIS FILE IS NOT ON A VOLUME, thus it's not automatically reloaded on the dev platform!
set -e

# Make sure we pipinstalled requirements.txt
pip install -r /src/requirements.txt

# Propagate
exec $@
