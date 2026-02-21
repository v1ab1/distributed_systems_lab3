#!/usr/bin/env bash
set -e

export VARIANT="${VARIANT:-v1}"
export PGHOST="${PGHOST:-postgres}"
export PGUSER="${PGUSER:-program}"

psql -h "$PGHOST" -U "$PGUSER" -d postgres -f "/scripts/db-$VARIANT.sql"
