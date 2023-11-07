#!/bin/bash
rm requirements.txt
pip install --upgrade pip
pip install --upgrade -r requirements.in
pip freeze >> requirements.txt
