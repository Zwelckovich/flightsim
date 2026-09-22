from pathlib import Path
p=Path('work/tour-template.html');s=p.read_text(encoding='utf8')
s=s.replace("$('#detail').scrollTop=0}","$('#detail').scrollTop=0;if(focus)$('.workbench').scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'})}")
s=s.replace(".attr('r',1.8).attr('fill','#89a9b5').attr('opacity',.6)",".attr('r',1.8).attr('fill','#89a9b5').attr('opacity',.6).style('cursor','pointer').on('click',(event,a)=>{event.stopPropagation();jumpToAirport(a.icao)})")
s=s.replace('ein kurzerer Küstenabschnitt','ein kürzerer Küstenabschnitt')
p.write_text(s,encoding='utf8')
b=Path('work/briefings.json');t=b.read_text(encoding='utf8').replace('ein kurzerer Küstenabschnitt','ein kürzerer Küstenabschnitt');b.write_text(t,encoding='utf8')
