#!/bin/bash

# run as . ./runanki.sh

# with gldriver6 > software
#apt-get install -y make
# run with 
. /etc/default/locale
export LANG
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"
anki --no-sandbox  # >/dev/null 2>&1 

