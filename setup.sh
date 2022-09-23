#! /bin/bash
# cleanup database file
# run on rootdir

rm ./data/weather.db
sqlite3 ./data/weather.db  < ./sql/create_raw_rain_data_table.sql