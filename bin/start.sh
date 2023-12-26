#!/bin/bash

python -m app.init_db

gunicorn app.app:app
