#!/bin/bash
# テスト用データベースの自動作成（docker-compose 初回起動時に実行される）
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE daily_report_test;
EOSQL
