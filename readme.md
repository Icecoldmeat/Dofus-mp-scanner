

## Start script using git bash

1) move to dofus-mp-scanner repo
2) source `source .venv/Scripts/activate`
3) `export PYTHONPATH="$(pwd)/src:$(pwd)"`
4) `python commands/scanner.py`
5) check your path `python -c "import sys; print('\n'.join(sys.path))"`



Yes, formula is (3 * value * density * lvl / 200 + 1) / density, so for a lvl 100 item not focused on ap generation, you will get ((3 * 1 * 100 * 100) / 200 + 1) / 100= 151 / 100 = 1.51 runes with a 100% multiplier, where you will get ((3 * 1 * 100 * 200) / 200 + 1) / 100 = 3.01 ap runes for a lvl 200 item. 




image made with paint.net



## locks mysql
SELECT OBJECT_TYPE,
       OBJECT_SCHEMA,
       OBJECT_NAME,
       LOCK_TYPE,
       LOCK_STATUS,
       THREAD_ID,
       PROCESSLIST_ID,
       PROCESSLIST_INFO
FROM performance_schema.metadata_locks
INNER JOIN performance_schema.threads ON THREAD_ID = OWNER_THREAD_ID
WHERE PROCESSLIST_ID <> CONNECTION_ID();    

KILL <THREAD_ID> 