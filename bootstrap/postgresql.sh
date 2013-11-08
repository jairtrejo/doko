POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/
createdb -E UTF8 -l en_US.utf8 postgisdb -T template0
createlang -d postgisdb plpgsql
psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='postgisdb';"
psql -d postgisdb -f $POSTGIS_SQL_PATH/postgis.sql
psql -d postgisdb -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
psql -d postgisdb -c "GRANT ALL ON geometry_columns TO PUBLIC;"
psql -d postgisdb -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
createuser --no-superuser --createdb --no-createrole vagrant
