#!/bin/ksh

# Needed to DB Name, User, HostName Port specified in postgres-inf.cfg file
source ./postgres-inf.cfg

LOGFILE="./log/createTables_sql.log"
if [ -f $LOGFILE ];
then
    # If log file size exceeds 5MB, overwrite the old backup file
    if [ $(wc -c "${LOGFILE}" | cut -f 1 -d ' ') -ge 5000000 ]; then
        mv -f $LOGFILE $LOGFILE.backup
    fi
fi

echo "`date +%Y-%m-%d_%H.%M.%S`:INFO Starting table creation" >> ${LOGFILE} 2>&1

# mv the .dataprocessorrc file
if [ -f /usr/local/infobright-products/dlp/.dataprocessorrc ]
then 
	mv /usr/local/infobright-products/dlp/.dataprocessorrc  /usr/local/infobright-products/dlp/.dataprocessorrc-old
	echo "`date +%Y-%m-%d_%H.%M.%S`:INFO Moved .dataprocessorrc file to .dataprocessorrc-old" >> ${LOGFILE} 2>&1

fi

function runScript {
    echo "`date +%Y-%m-%d_%H.%M.%S`:INFO: running SQL script $5 on host $3" >> ${LOGFILE} 2>&1
    
    #psql -dpostgres -Upostgres -p5029 -q -t -f /opt/servicepath/xsightDb/current/scripts/createTables.sql >> ${LOGFILE} 2>&1
    psql -d$1 -U$2 -h$3 -p$4 -q -t -f $5 >> ${LOGFILE} 2>&1
    psqlret=$?

    if [ $psqlret -eq 0 ]
    then
      echo "`date +%Y-%m-%d_%H.%M.%S`:INFO: psql successfully run" >> ${LOGFILE} 2>&1
    elif [ $psqlret -eq 1 ]
    then
      echo "`date +%Y-%m-%d_%H.%M.%S`:ERROR: psql encountered fatal error internally" >> ${LOGFILE} 2>&1
    elif [ $psqlret -eq 2 ]
    then
      echo "`date +%Y-%m-%d_%H.%M.%S`:ERROR: psql encountered errors in db server connection and/or session" >> ${LOGFILE} 2>&1
    elif [ $psqlret -eq 3 ]
    then
      echo "`date +%Y-%m-%d_%H.%M.%S`:ERROR: psql encountered errors in sql commands" >> ${LOGFILE} 2>&1
    fi
}


    runScript ${DATABASE_NAME} ${DB_USER} ${DB_HOSTNAME} ${DB_PORT} ./createPropertyTables.sql
    
exit $psqlret
