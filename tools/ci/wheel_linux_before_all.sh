#!/bin/bash

# Configure the libraries needed to build wheel packages on linux.
# This script is designed to be used by cibuildwheel as CIBW_BEFORE_ALL_LINUX

set -euo pipefail

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source /etc/os-release

# Install GaussDB development files.
case "$ID" in
    alpine)
        # tzdata is required for datetime tests.
        "${dir}/build_libpq.sh" > /dev/null
        ;;

    debian)
        # Note that the pgdg doesn't have an aarch64 repository so wheels are
        # build with the libpq packaged with Debian 9, which is 9.6.
        if [ "$AUDITWHEEL_ARCH" != 'aarch64' ]; then
            echo "deb http://apt.postgresql.org/pub/repos/apt $VERSION_CODENAME-pgdg main" \
                > /etc/apt/sources.list.d/pgdg.list
            # TODO: On 2021-11-09 curl fails on 'ppc64le' with:
            #   curl: (60) SSL certificate problem: certificate has expired
            # Test again later if -k can be removed.
            curl -fsSLk https://www.postgresql.org/media/keys/ACCC4CF8.asc \
                > /etc/apt/trusted.gpg.d/postgresql.asc
        fi

        apt-get update
        apt-get -y upgrade
        apt-get -y install libpq-dev flex
        ;;

    centos)
        "${dir}/build_libpq.sh" > /dev/null
        ;;

    *)
        echo "$0: unexpected Linux distribution: '$ID'" >&2
        exit 1
        ;;
esac
