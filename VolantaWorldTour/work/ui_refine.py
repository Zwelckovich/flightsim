from pathlib import Path
p=Path('work/tour-template.html');s=p.read_text(encoding='utf8')
s=s.replace('.map-card{min-width', '.map-card{min-width')
s=s.replace('height:565px','height:clamp(380px,calc(100vh - 315px),610px)')
s=s.replace('.map-card,.detail{height:610px}', '.map-card,.detail{height:clamp(430px,calc(100vh - 315px),650px)}')
s=s.replace(".attr('opacity',state.map==='world'?.25:.16)",".attr('opacity',state.map==='world'?.4:.16)")
s=s.replace(".attr('stroke','#7196a4')", ".attr('stroke',l=>l.over2h?'#d0a36c':'#7196a4')")
needle="const visible=state.map==='leg'?[chosen]:chapterLegs;"
replacement="mapGroup.append('g').selectAll('circle').data(Object.values(A)).join('circle').attr('class','background-pin').attr('cx',a=>proj(point(a))[0]).attr('cy',a=>proj(point(a))[1]).attr('r',1.8).attr('fill','#89a9b5').attr('opacity',.6);"+needle
s=s.replace(needle,replacement)
s=s.replace("mapGroup.selectAll('.pin').attr('r',4/e.transform.k);", "mapGroup.selectAll('.pin').attr('r',4/e.transform.k);mapGroup.selectAll('.background-pin').attr('r',1.8/e.transform.k);")
p.write_text(s,encoding='utf8')
