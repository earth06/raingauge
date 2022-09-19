#! /bin/bash
# cleanup database file
# run on rootdir

rm ./data/weather.db
sqlite3 weather.db  < ./sql/create_raw_rain_data_table.sql