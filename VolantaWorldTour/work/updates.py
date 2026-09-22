from pathlib import Path
p=Path('work/route_source.py');s=p.read_text(encoding='utf8').replace('YPCC WICT WIMM','YPCC WIEE WIMM');p.write_text(s,encoding='utf8')
import urllib.request
urllib.request.urlretrieve('https://www.rotorua-airport.co.nz/site_files/21129/upload_files/221111_RRAMasterPlanFINAL.pdf?dl=1','work/rotorua-masterplan.pdf')
