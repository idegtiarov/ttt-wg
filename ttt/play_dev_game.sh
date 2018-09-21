#!/usr/bin/env bash

sleep 5 && python manage.py migrate --settings=config.settings
python manage.py runserver 0.0.0.0:8008 --settings=config.settings
