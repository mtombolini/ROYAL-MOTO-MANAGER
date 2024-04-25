#!/bin/bash
cd /home/franco/Documentos/ROYAL-MOTO-MANAGER
source venv/bin/activate

git checkout cambios_produccion
git add .
git commit -m "add: backup $(date +'%Y-%m-%d %H:%M:%S')"
git push