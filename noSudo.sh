#!/bin/bash


die() { echo -e "Script failed\n$*"; }

if [[ $EUID -ne 0 ]]; then
  die "You must be root!"
fi

if [ ! -d "/etc/udev/rules.d/" ]; then
  mkdir -p /etc/udev/rules.d/ || die
fi

cd /etc/udev/rules.d/ || die
touch 99-i2c.rules || die
echo 'SUBSYSTEM=="i2c-dev", MODE="0666"' >> 99-i2c.rules || die

echo "You must reboot in order for this to take effect"
exit


