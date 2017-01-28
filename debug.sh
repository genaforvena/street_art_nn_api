#!/bin/bash
source flask/bin/activate
export FLASK_APP=street_art_nn
export FLASK_DEBUG=True
flask run
