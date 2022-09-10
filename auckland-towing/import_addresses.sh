#!/usr/bin/env bash

# copy nz-street-address.csv to this repo
sqlite-utils insert towing.db addresses nz-street-address.csv --csv