import urllib.request,pathlib
for name in ['airports','runways','countries']:
    url='https://raw.githubusercontent.com/datasets/airport-codes/master/data/airport-codes.csv' if False else 'https://davidmegginson.github.io/ourairports-data/'+name+'.csv'
    urllib.request.urlretrieve(url, pathlib.Path('work')/(name+'.csv'))
    print(name, (pathlib.Path('work')/(name+'.csv')).stat().st_size)
for name,url in [('world.json','https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json'),('d3.min.js','https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js'),('topojson.min.js','https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js')]:
    urllib.request.urlretrieve(url, pathlib.Path('work')/name)
    print(name, (pathlib.Path('work')/name).stat().st_size)
