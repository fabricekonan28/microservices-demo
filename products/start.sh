#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z db.monapp.svc.cluster.local 5432; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - starting app"

exec "$@"
