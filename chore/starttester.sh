#!/bin/bash
cd /usr/gigatester || exit 1
set -a && source tester/.env && set +a
tester/venv/bin/python -m tester.main
