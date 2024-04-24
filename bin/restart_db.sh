#!/bin/bash
cd /home/franco/Documentos/ROYAL-MOTO-MANAGER
source venv/bin/activate

python3 -m extras.json_transformation
python3 -m extras.print_archive

python3 -m extras.backup_table
python3 -m extras.print_archive

python3 -m databases.drop_tables_reset
python3 -m extras.print_archive

python3 -m app.init_db
python3 -m extras.print_archive

python3 -m app.extraction_main
python3 -m extras.print_archive

git checkout cambios_produccion
git add .
git commit -m "add: backup $(date +'%Y-%m-%d %H:%M:%S')"
git push