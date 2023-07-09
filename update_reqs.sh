#!/bin/bash
rm requirements.txt
pip install -r requirements.in
pip freeze >> requirements.txt
