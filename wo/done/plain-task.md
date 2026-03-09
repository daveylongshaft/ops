# Just a plain workorder, no front-matter

Do something simple. CSC_ROOT=/opt/csc python3 -c 
import sys, os
sys.path.insert(0, 'irc/packages/csc-service')
os.environ['CSC_ROOT'] = '/opt/csc'
from pathlib import Path
from csc_service.infra import pm
pm.setup(Path('/opt/csc'))
result = pm.run_cycle()
print('assigned:', result)

