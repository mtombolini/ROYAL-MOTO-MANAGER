#!/bin/bash
cd /home/nebula/ROYAL-MOTO-MANAGER
source venv/bin/activate

python3 -m extras.backup_table
python3 -m extras.print_archive

python3 -m databases.drop_tables_reset
python3 -m extras.print_archive

python3 -m app.init_db
python3 -m extras.print_archive

python3 -m app.extraction_main