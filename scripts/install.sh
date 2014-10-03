#!/bin/bash

scriptpath="$(cd "$(dirname "$0")" && pwd -P)"
workingpath="$(dirname "$scriptpath")"
envname="dl_general.env"

if ! which pip > /dev/null; then
    echo "please install pip"
    exit 1
fi

if ! which virtualenv > /dev/null; then
    echo "please install virtualenv: pip install virtualenv"
    exit 1
fi

echo "creating virtualenv: $envname"
virtualenv "$workingpath/$envname"
if source "$workingpath/$envname/bin/activate" > /dev/null; then
    pip install -r "$scriptpath/requirements.txt"
    [[ -f "$workingpath/db/db.sqlite3" ]] || "$workingpath/manage.py" syncdb --noinput --no-initial-data
    "$workingpath/manage.py" migrate
    "$workingpath/manage.py" reset_key
    deactivate
fi

cd "$workingpath"
if ! [ -f "$workingpath/activate" ]; then
    ln -s $envname/bin/activate .
fi
