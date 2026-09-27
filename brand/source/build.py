import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
S="/tmp/claude-0/-home-user--n-ml-ml/3396f4b9-436f-599b-95f1-9d21bcaee421/scratchpad/"
OUT="/home/user/-n-ml-ml/brand/final/"
NAVY,BLUE,CYAN="#0F172A","#2563EB","#22D3EE"

def text_path(fontfile, text, size, tracking=0.0):
    """Return (svg path d, width) with baseline at y=0, origin x=0."""
    blob=hb.Blob.from_file_path(fontfile); face=hb.Face(blob); font=hb.Font(face)
    buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font,buf,{"kern":True,"liga":True})
    tt=TTFont(fontfile); gs=tt.getGlyphSet(); upm=tt["head"].unitsPerEm; sc=size/upm
    order=tt.getGlyphOrder()
    pen=SVGPathPen(gs); x=0
    infos,poss=buf.glyph_infos,buf.glyph_positions
    for i,(inf,pos) in enumerate(zip(infos,poss)):
        g=order[inf.codepoint]
        tp=TransformPen(pen,(sc,0,0,-sc,(x+pos.x_offset)*sc,-pos.y_offset*sc))
        gs[g].draw(tp)
        x+=pos.x_advance+(tracking/sc if i<len(infos)-1 else 0)
    return pen.getCommands(), x*sc

def mark(plate=BLUE, ink="#FFFFFF", sig=CYAN):
    return f'''<rect width="64" height="64" rx="16" fill="{plate}"/>
<path d="M18 47 V19 L40 47 V27" fill="none" stroke="{ink}" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="40" cy="17.5" r="3.8" fill="{sig}"/>
<path d="M41.2 10.6 A7 7 0 0 1 46.9 18.7" fill="none" stroke="{sig}" stroke-width="3.2" stroke-linecap="round"/>
<path d="M42.1 5.7 A12 12 0 0 1 51.8 19.6" fill="none" stroke="{sig}" stroke-width="3.2" stroke-linecap="round" opacity=".6"/>'''

en,enw=text_path(S+"sora600.ttf","naqra",42,-1.5)
ar,arw=text_path(S+"plexar600.ttf","نقرة",26)

def svg(w,h,body,bg=None):
    b=f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w*10}" height="{h*10}">{b}{body}</svg>'

def primary(txt, artxt):
    W=200
    return (f'<g transform="translate(68,0)">{mark()}</g>'
            f'<path d="{en}" fill="{txt}" transform="translate({(W-enw)/2:.2f},116)"/>'
            f'<path d="{ar}" fill="{artxt}" transform="translate({(W-arw)/2:.2f},156)"/>')
def horizontal(txt, artxt):
    return (f'<g transform="translate(0,4)">{mark()}</g>'
            f'<path d="{en}" fill="{txt}" transform="translate(78,40)"/>'
            f'<path d="{ar}" fill="{artxt}" transform="translate({78+enw-arw:.2f},68)"/>')
HW=int(78+enw+4)
files={
 "naqra-logo-primary.svg": svg(200,170,primary(NAVY,BLUE)),
 "naqra-logo-primary-white.svg": svg(200,170,primary("#FFFFFF",CYAN)),
 "naqra-logo-horizontal.svg": svg(HW,74,horizontal(NAVY,BLUE)),
 "naqra-logo-horizontal-white.svg": svg(HW,74,horizontal("#FFFFFF",CYAN)),
 "naqra-icon.svg": svg(64,64,mark()),
}
for n,c in files.items(): open(OUT+n,"w").write(c)
# social: instagram profile 1080 (icon big on navy), facebook cover 1640x624
prof=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080"><rect width="1080" height="1080" fill="{NAVY}"/><g transform="translate(290,290) scale(7.8125)">{mark()}</g></svg>'
open(OUT+"naqra-instagram-profile.svg","w").write(prof)
tag,tagw=text_path(S+"plexar600.ttf","قرّب تلفونك… وخلصت",46)
sub,subw=text_path(S+"sora600.ttf","ONE TAP. DONE.",22,4)
url,urlw=text_path(S+"sora600.ttf","NaqraJo.com  ·  @naqra.jo",22,0.5)
cover=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1640 624"><rect width="1640" height="624" fill="{NAVY}"/>'
 f'<circle cx="1640" cy="312" r="420" fill="none" stroke="{BLUE}" stroke-width="3" opacity=".35"/>'
 f'<circle cx="1640" cy="312" r="300" fill="none" stroke="{BLUE}" stroke-width="3" opacity=".55"/>'
 f'<circle cx="1640" cy="312" r="180" fill="none" stroke="{CYAN}" stroke-width="3" opacity=".7"/>'
 f'<g transform="translate(560,120) scale(2.6)">{horizontal("#FFFFFF",CYAN)}</g>'
 f'<path d="{tag}" fill="#FFFFFF" transform="translate({820-tagw/2:.1f},400)"/>'
 f'<path d="{sub}" fill="{CYAN}" transform="translate({820-subw/2:.1f},450)"/>'
 f'<path d="{url}" fill="#94A3B8" transform="translate({820-urlw/2:.1f},530)"/></svg>')
open(OUT+"naqra-facebook-cover.svg","w").write(cover)
print("enw",enw,"arw",arw,"HW",HW)
