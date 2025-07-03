#!/bin/bash

# This program will install required packages.


if uname -r | grep -q 'arch'; then
	yay -Sy
	yay -S pyside6 pyside6-tools python-dotenv sqlite python-sqlalchemy rubygems
	yay -S python-segno python-qrcode-artistic --mflags --nocheck
	echo "Required Packages are Installed!"
else
	echo "You are running a non-arch distribution; please install required packages manually."
fi

