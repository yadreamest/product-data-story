#!/usr/bin/env python3
"""Render validated analytical notes. No network or account access."""
import argparse
import html
import json
import math
from pathlib import Path
import textwrap
import time
import tempfile

KINDS = {'bar', 'funnel', 'line', 'stacked', 'kpi'}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def validate(doc):
    require(isinstance(doc, dict), 'Root must be an object')
    require(isinstance(doc.get('pages'), list) and doc['pages'], 'pages must be a nonempty list')
    warnings = []
    for p, page in enumerate(doc['pages'], 1):
        require(isinstance(page, dict), f'Page {p}: expected object')
        for key in ('title', 'period', 'source'):
            require(isinstance(page.get(key), str) and page[key].strip(), f'Page {p}: {key} is required')
        require(len(page['title']) <= 110, f'Page {p}: shorten title to 110 characters')
        require(1 <= len(page.get('charts', [])) <= 3, f'Page {p}: use 1–3 charts')
        for c, chart in enumerate(page['charts'], 1):
            loc = f'Page {p}, chart {c}'
            require(chart.get('type') in KINDS, f'{loc}: unsupported type')
            for key in ('title', 'base', 'unit'):
                require(isinstance(chart.get(key), str) and chart[key].strip(), f'{loc}: {key} is required')
            require(len(chart['title']) <= 90 and len(chart['base']) <= 170 and len(chart.get('note','')) <= 220, f'{loc}: shorten text or split the page')
            if 'не указан' in chart['base'].lower() or 'unknown' in chart['base'].lower():
                warnings.append(f'{loc}: population is unknown; do not infer comparisons')
            labels, values = chart.get('labels'), chart.get('values')
            require(isinstance(labels, list) and isinstance(values, list) and len(labels) == len(values) and len(labels) > 0, f'{loc}: labels/values must be equal-length nonempty lists')
            cap = {'bar':7,'funnel':6,'line':12,'stacked':5,'kpi':3}[chart['type']]
            require(len(labels) <= cap, f'{loc}: maximum {cap} values; split the chart')
            require(all(isinstance(x,str) and 0 < len(x) <= 80 for x in labels), f'{loc}: labels must contain 1–80 characters')
            require(all(v is None or (type(v) in (int,float) and math.isfinite(v) and v >= 0) for v in values), f'{loc}: values must be finite nonnegative numbers or null')
            require(any(v is not None for v in values), f'{loc}: no observations')
            require(type(chart.get('decimals',0)) is int and chart.get('decimals',0) in (0,1,2), f'{loc}: decimals must be 0, 1 or 2')
            if chart['unit'] == '%':
                require(all(v is None or v <= 100 for v in values), f'{loc}: percent exceeds 100')
            if chart['type'] == 'stacked':
                require(chart.get('exclusive') is True and chart['unit'] == '%', f'{loc}: stacked needs exclusive=true and percent units')
                require(all(v is not None for v in values) and abs(sum(values)-100) < 0.001, f'{loc}: stacked must sum to 100; do not silently normalize')
            if chart['type'] == 'funnel':
                require(all(v is not None for v in values), f'{loc}: funnel cannot contain missing stages')
                require(all(a >= b for a,b in zip(values,values[1:])), f'{loc}: funnel must be non-increasing; otherwise use bar')
                require(values[0] > 0, f'{loc}: funnel starting population must be positive')
            if chart['type'] == 'line':
                require(len(values)>=2, f'{loc}: line requires at least two time points')
                require(chart.get('equally_spaced') is True, f'{loc}: this renderer supports equally spaced time points only')
            highlight = chart.get('highlight', [0])
            require(isinstance(highlight,list) and all(type(i) is int and 0 <= i < len(values) for i in highlight), f'{loc}: invalid highlight indices')
    return warnings


def render(doc, out):
    """Publish a complete new report only after successful rendering and checks."""
    validate(doc)
    out=Path(out)
    require(not out.exists() or (out.is_dir() and not any(out.iterdir())),
            'Output must be a new or empty directory; choose a new report version')
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.product-data-story-',dir=out.parent) as tmp:
        stage=Path(tmp)/'report'
        result=_render(doc,stage)
        if out.exists(): out.rmdir()
        stage.replace(out)
    return result


def _render(doc, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.font_manager import FontProperties, fontManager
    from matplotlib.patches import Rectangle
    start=time.perf_counter()
    warnings=validate(doc)
    out.mkdir(parents=True,exist_ok=True)
    fonts=Path(__file__).resolve().parent.parent/'assets/fonts'
    for name in ('Regular','Medium','SemiBold'):
        path=fonts/f'Inter-{name}.ttf'
        require(path.exists(),f'Missing bundled font: {path.name}')
        fontManager.addfont(str(path))
    bg,ink,muted,accent,neutral,grid='#FAFAF8','#202128','#656872','#6946CE','#B9BDC5','#E3E4E8'
    plt.rcParams.update({'font.family':'Inter','svg.fonttype':'none','pdf.fonttype':42})
    probe=plt.figure(figsize=(10,1),dpi=100)
    renderer=probe.canvas.get_renderer()
    def prop(size=16,weight='Regular'):
        return FontProperties(fname=str(fonts/f'Inter-{weight}.ttf'),size=size*.72)
    def width(s,size,weight):return renderer.get_text_width_height_descent(s,prop(size,weight),False)[0]
    def wrap(s,maxwidth,size,weight='Regular'):
        lines=[]
        for paragraph in s.split('\n'):
            line=''
            for word in paragraph.split():
                candidate=(line+' '+word).strip()
                if line and width(candidate,size,weight)>maxwidth:lines.append(line);line=word
                else:line=candidate
            lines.append(line)
        return '\n'.join(lines)
    def fmt(v,ch):
        if v is None:return 'нет данных'
        s=f"{v:,.{ch.get('decimals',0)}f}".replace(',','\u202f').replace('.',',')
        return s+('' if ch['unit']=='count' else ('%' if ch['unit']=='%' else ' '+ch['unit']))
    layout_issues=[]
    with PdfPages(out/'report.pdf') as pdf:
        for idx,page in enumerate(doc['pages'],1):
            ops=[]
            def text(x,y,s,size=16,weight='Regular',color=ink,maxwidth=None,leading=None,ha='left'):
                if maxwidth:s=wrap(s,maxwidth,size,weight)
                leading=leading or size*1.35
                ops.append(('text',x,y,s,size,weight,color,leading,ha))
                return len(s.split('\n'))*leading
            def rect(x,y,w,h,color):ops.append(('rect',x,y,w,h,color))
            def line(x1,y1,x2,y2,color=grid,lw=1):ops.append(('line',x1,y1,x2,y2,color,lw))
            text(56,40,page.get('eyebrow','АНАЛИТИЧЕСКАЯ ЗАПИСКА').upper(),13,'Medium',muted)
            text(944,40,page['period'],13,'Regular',muted,ha='right')
            y=80+text(56,80,page['title'],34,'SemiBold',maxwidth=888,leading=40)+32
            for j,ch in enumerate(page['charts']):
                if j:
                    line(56,y,944,y);y+=28
                y+=text(56,y,ch['title'],22,'SemiBold',maxwidth=888,leading=28)+8
                y+=text(56,y,'База: '+ch['base'],14,color=muted,maxwidth=888,leading=20)+16
                kind=ch['type'];vals=ch['values'];labels=ch['labels']
                highlights=ch.get('highlight',[0])
                if kind in ('bar','funnel'):
                    x0=316;barwidth=510
                    maximum=100 if ch['unit']=='%' else max(v for v in vals if v is not None) or 1
                    prepared=[wrap(label,240,16) for label in labels]
                    heights=[max(44,len(label.split('\n'))*22+12) for label in prepared]
                    chartend=y+sum(heights)
                    ticks=[0,50,100] if ch['unit']=='%' else [0,maximum]
                    for tick in ticks:
                        x=x0+tick/maximum*barwidth
                        line(x,y+5,x,chartend-5)
                        text(x,chartend+6,fmt(tick,ch),12,color=muted,ha='center')
                    for k,(v,label,rh) in enumerate(zip(vals,prepared,heights)):
                        cy=y+rh/2
                        text(56,cy-len(label.split('\n'))*11,label,16,leading=22)
                        color=accent if k in highlights else neutral
                        length=(v or 0)/maximum*barwidth
                        if v is not None:rect(x0,cy-9,length,18,color)
                        text(x0+length+12,cy-11,fmt(v,ch),17,'SemiBold',accent if k in highlights else ink,leading=22)
                        y+=rh
                    y=chartend+34
                elif kind=='kpi':
                    step=888/len(vals)
                    maxlabel=0
                    for k,v in enumerate(vals):
                        x=56+k*step
                        text(x,y,fmt(v,ch),44,'SemiBold',accent,leading=48)
                        maxlabel=max(maxlabel,text(x,y+58,labels[k],16,maxwidth=step-24,leading=22))
                    y+=58+maxlabel+4
                elif kind=='stacked':
                    palette=[accent,'#9881D8','#79818E','#ABB1BB','#D9DDE3']
                    x=56
                    for k,v in enumerate(vals):
                        w=888*v/100
                        rect(x,y,w,28,palette[k]);x+=w
                        if k<len(vals)-1:line(x,y,x,y+28,bg,2)
                    y+=44;step=888/len(vals)
                    wrapped=[wrap(label,step-30,14) for label in labels]
                    labelheight=max(len(label.split('\n')) for label in wrapped)*20
                    for k,v in enumerate(vals):
                        x=56+k*step
                        rect(x,y+4,8,8,palette[k])
                        text(x+18,y,wrapped[k],14,leading=20)
                        text(x+18,y+labelheight+4,fmt(v,ch),20,'SemiBold',leading=26)
                    y+=labelheight+30
                else:
                    x0=88;x1=922;ph=190
                    time_labels=[wrap(label,70,12) for label in labels]
                    tick_height=max(len(label.split('\n')) for label in time_labels)*16
                    maximum=100 if ch['unit']=='%' else (max(v for v in vals if v is not None) or 1)*1.2
                    for tick in [0,maximum/2,maximum]:
                        yy=y+ph*(1-tick/maximum)
                        line(x0,yy,x1,yy)
                        text(x0-12,yy-8,fmt(tick,ch),12,color=muted,ha='right',leading=16)
                    previous=None
                    for k,v in enumerate(vals):
                        x=x0+(x1-x0)*k/(len(vals)-1)
                        text(x,y+ph+12,time_labels[k],12,color=muted,ha='center',leading=16)
                        if v is None:previous=None;continue
                        yy=y+ph*(1-v/maximum)
                        if previous:line(*previous,x,yy,accent,2.5)
                        ops.append(('dot',x,yy,accent))
                        text(x,yy-26,fmt(v,ch),14,'Medium',ha='center',leading=20)
                        previous=(x,yy)
                    y+=ph+12+tick_height+24
                note=ch.get('note','')
                if kind=='funnel':
                    conversions=['—' if a==0 else f'{b/a*100:.1f}%'.replace('.',',') for a,b in zip(vals,vals[1:])]
                    overall=f'{vals[-1]/vals[0]*100:.1f}%'.replace('.',',')
                    conversion='   ·   '.join(f'Этап {k+1} → {k+2}: {rate}' for k,rate in enumerate(conversions))+'   ·   Общая: '+overall
                    y+=8
                    y+=text(56,y,conversion,14,'Medium',muted,maxwidth=888,leading=20)+8
                if kind=='line' and None in vals:note='Разрыв линии — нет наблюдения. '+note
                if note:y+=8+text(56,y+8,note,14,color=muted,maxwidth=888,leading=20)
                y+=28
            line(56,y,944,y);y+=18
            y+=text(56,y,'Источник: '+page['source'],12,color=muted,maxwidth=835,leading=18)
            text(944,y-18,f'{idx:02}',12,color=muted,ha='right')
            height=y+36
            fig=plt.figure(figsize=(10,height/100),dpi=100,facecolor=bg)
            ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1000);ax.set_ylim(height,0);ax.axis('off')
            for op in ops:
                if op[0]=='text':
                    _,x,yy,s,size,weight,color,leading,ha=op
                    # Draw each baseline separately: line advance is independent of font metrics.
                    for li,part in enumerate(s.split('\n')):
                        ax.text(x,yy+li*leading,part,fontproperties=prop(size,weight),color=color,ha=ha,va='top')
                elif op[0]=='rect':
                    _,x,yy,w,h,color=op;ax.add_patch(Rectangle((x,yy),w,h,color=color,linewidth=0,zorder=2))
                elif op[0]=='line':
                    _,x1,y1,x2,y2,color,lw=op;ax.plot([x1,x2],[y1,y2],color=color,lw=lw*.72,solid_capstyle='butt',zorder=3 if color==bg else 1)
                else:
                    _,x,yy,color=op;ax.plot([x],[yy],marker='o',ms=4,color=color)
            fig.canvas.draw();canvas_renderer=fig.canvas.get_renderer()
            for artist in ax.texts:
                box=artist.get_window_extent(canvas_renderer)
                if box.x0 < -1 or box.y0 < -1 or box.x1>fig.bbox.width+1 or box.y1>fig.bbox.height+1:
                    layout_issues.append(f'Page {idx}: text outside canvas: {artist.get_text()[:60]}')
            fig.savefig(out/f'page-{idx:02}.png',dpi=160,facecolor=bg)
            fig.savefig(out/f'page-{idx:02}.svg',facecolor=bg)
            pdf.savefig(fig,facecolor=bg)
            plt.close(fig)
    plt.close(probe)
    require(not layout_issues,'\n'.join(layout_issues))
    cards=''.join(f'<article><h2>{html.escape(p["title"])}</h2><a href="page-{i:02}.svg"><img src="page-{i:02}.png" alt="{html.escape(p["title"],quote=True)}"></a></article>' for i,p in enumerate(doc['pages'],1))
    (out/'index.html').write_text('<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Product Data Story</title><style>body{margin:32px auto;max-width:1000px;background:#e8e9ed;color:#20212b;font:16px system-ui}article{margin:32px 0}img{width:100%;height:auto}h2{font-size:16px}a{color:#6543c7}</style><h1>Product Data Story</h1><a href="report.pdf">Скачать PDF</a>'+cards+'</html>',encoding='utf-8')
    (out/'input.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    result={'pages':len(doc['pages']),'warnings':warnings,'render_seconds':round(time.perf_counter()-start,2),'matplotlib':matplotlib.__version__,'design':'v2-inter','font':'Bundled Inter 4.1'}
    (out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--out',type=Path,default=Path('report'));parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    try:
        doc=json.loads(args.input.read_text(encoding='utf-8'))
        if args.validate_only: print(json.dumps({'warnings':validate(doc)},ensure_ascii=False))
        else: print(json.dumps(render(doc,args.out),ensure_ascii=False))
    except (ValueError,KeyError,TypeError) as e:
        parser.exit(2,f'Invalid report: {e}\n')
