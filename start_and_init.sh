#!/bin/bash
export FLASK_APP=MyAmazonClone.app
echo "--- Initializing Database ---"
flask init-db
echo "--- Starting Flask Server ---"
flask run
