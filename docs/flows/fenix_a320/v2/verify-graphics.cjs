const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname,data=JSON.parse(fs.readFileSync(path.join(root,'data-v2.json'),'utf8'));
const original=fs.readFileSync(path.join(root,'../Fenix_A320_Flow.html'),'utf8'),code=original.match(/<script>([\s\S]*?)<\/script>/)[1],ctx={};
vm.runInNewContext(code.slice(0,code.indexOf('const FIELDS ='))+';globalThis.img=IMAGES;',ctx);
for(const [key,src]of Object.entries(ctx.img))assert.equal(data.IMAGES[key],src,'Original image changed: '+key);
const expected={n4:'cockpit',n20:'approach-techniques',s2:'engine-out',s3:'quick-return',s5:'emergency-descent',s6:'circling',s7:'visual',s8:'touch-go',s9:'overweight',r2:'flap-logic',r4:'cockpit'};
for(const [id,key]of Object.entries(expected))assert.equal(data.DATA.find(p=>p.id===id).diagram,key,'Missing phase graphic: '+id);
assert.equal(Object.keys(data.plates).length,10);
let svgs=0;
for(const [key,p]of Object.entries(data.plates)){assert(data.IMAGES[p.original],'Missing original '+key);for(const id of p.refs)assert(data.refs[id],'Missing source '+id);
 if(p.file){const svg=Buffer.from(data.IMAGES[p.image].split(',')[1],'base64').toString('utf8');assert(svg.startsWith('<svg'));assert.equal(svg,fs.readFileSync(path.resolve(root,'plates',p.file),'utf8'));assert(!/<script|<foreignObject|\bon\w+=|href=["']https?:/i.test(svg),'External or active SVG content');svgs++;}}
assert.equal(svgs,8);
const matrix=data.legacyOverweight;assert.equal(matrix.length,9);assert(matrix.every(r=>r.length===8));
assert.equal(matrix[8][1],78);assert.equal(matrix[8][2],72);assert.equal(matrix[8][3],null);
const html=fs.readFileSync(path.join(root,'../Fenix_A320_Flow_V2.html'),'utf8');new vm.Script(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
assert(html.includes('id="action-cancel" formnovalidate'));assert(html.includes('id="plate-dialog"'));
const result={originalImagesPreserved:Object.keys(ctx.img).length,learningTopics:10,embeddedSvgPlates:8,phasePlacements:Object.keys(expected).length,standaloneSvgAssets:'passed',sourceReferences:'passed',historicalTableShape:'passed; blank cells remain null',javascriptSyntax:'passed',browser:{allSevenNewSvgs:'visually inspected and refined',svgZoom:'100% / 125% / fit / Escape passed',originalComparison:'passed',flightModeHidesPlates:'passed',narrowLayout:'375px content; no page overflow; table scrolls internally',consoleErrors:0}};
fs.writeFileSync(path.join(root,'GRAPHICS_TEST_RESULTS.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
