#!/bin/sh
gunicorn teamGS.wsgi:application --bind 0.0.0.0:8000