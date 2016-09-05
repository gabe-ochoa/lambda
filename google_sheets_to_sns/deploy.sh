#!/usr/bin/env bash
# deploy.sh

rm google_sheets_to_sns.zip

zip -9 google_sheets_to_sns.zip google_sheets_to_sns.py

cd $VIRTUAL_ENV/lib/python2.7/site-packages
zip -r9 ~/code/lambda/google_sheets_to_sns/google_sheets_to_sns.zip *
cd $VIRTUAL_ENV/lib64/python2.7/site-packages
zip -r9 ~/code/lambda/google_sheets_to_sns/google_sheets_to_sns.zip *
