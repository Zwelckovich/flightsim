from pathlib import Path
p=Path('work/tour-template.html');s=p.read_text(encoding='utf8').replace('height:clamp(380px,calc(100vh - 315px),610px)','height:clamp(360px,calc(100vh - 350px),610px)').replace('.land{fill:', '.land{vector-effect:non-scaling-stroke;fill:').replace('.graticule{stroke:', '.graticule{vector-effect:non-scaling-stroke;stroke:');p.write_text(s,encoding='utf8')
