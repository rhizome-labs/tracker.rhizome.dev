#!/bin/bash

npm install
python -m pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
npx tailwindcss -i ./tracker_rhizome_dev/app/css/main.css -o ./tracker_rhizome_dev/app/static/style.css --minify