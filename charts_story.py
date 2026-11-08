import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clean import load_and_clean
df, _ = load_and_clean(sys.argv[1] if len(sys.argv) > 1 else 'data/survey.xlsx')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'outputs/charts'
os.makedirs(OUT, exist_ok=True); df['g']=np.where(df.role=='Student','Students','Adults')
BLUE,ORANGE,GRAY='#2a78d6','#eb6834','#c3c2b7'; INK,INK2,MUTED,SURF,GRID='#0b0b0b','#52514e','#8a8984','#fcfcfb','#ecebe8'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':GRAY,'xtick.color':INK2,'ytick.color':INK,
 'figure.facecolor':SURF,'axes.facecolor':SURF,'savefig.facecolor':SURF,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False})
COL={'Adults':BLUE,'Students':ORANGE}
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*((p*(1-p)/n+z*z/(4*n*n))**0.5)/d; return (c-h)*100,(c+h)*100
def pct(g,col,test):
    s=df.loc[df.g==g,col].dropna(); k=int(test(s).sum()); n=len(s); return k/n*100,n,wilson(k,n)
agree=lambda s:s>=4; top=lambda s:s>=9
know=[('post_identify','Can identify mental health crises',agree),('post_describe','Can describe 988',agree),('post_when','Know when to use 988',agree)]
feel=[('q_engaged','Presenter engaged us',agree),('q_knew','Presenter knew the material',agree),('q_organized','Training well organized',agree),
      ('recommend','Would recommend (9–10 of 10)',top),('call988','Likely to call 988 (9–10 of 10)',top)]
def dumbbell(ax,rows,xlim=(30,100),ci=False,labels=True):
    for y,(col,lab,t) in enumerate(rows[::-1]):
        a,na,ca=pct('Adults',col,t); s,ns,cs=pct('Students',col,t)
        close=abs(a-s)<3; dy={'Students':0.13 if close else 0,'Adults':-0.13 if close else 0}
        if not close: ax.plot([s,a],[y,y],color=GRAY,lw=3,zorder=1,solid_capstyle='round')
        ext={}
        for g,v,c,n in [('Adults',a,ca,na),('Students',s,cs,ns)]:
            if ci:
                ax.plot(c,[y+dy[g]-0.2*(1 if g=='Students' else -1)*(not close)]*2,color=COL[g],lw=1.4,alpha=.6,zorder=2)
            ax.scatter(v,y+dy[g],s=110,color=COL[g],edgecolor=SURF,lw=2,zorder=3)
        lo,hi=sorted([(s,'Students'),(a,'Adults')])
        ax.text(lo[0]-2.2,y+dy[lo[1]],f'{lo[0]:.0f}%',ha='right',va='center',fontsize=10,color=COL[lo[1]],fontweight='bold')
        ax.text(hi[0]+2.2,y+dy[hi[1]],f'{hi[0]:.0f}%',ha='left',va='center',fontsize=10,color=COL[hi[1]],fontweight='bold')
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[1] for r in rows[::-1]] if labels else []); ax.tick_params(axis='y',length=0)
    ax.set_xlim(*xlim); ax.set_ylim(-0.6,len(rows)-0.4); ax.xaxis.set_major_formatter(lambda v,_:f'{v:.0f}%')
    ax.grid(axis='x',color=GRID,lw=.8); ax.set_axisbelow(True)
def legend(fig,y):
    from matplotlib.lines import Line2D
    h=[Line2D([],[],marker='o',ls='',ms=9,color=COL[g],label=f'{g}') for g in ['Students','Adults']]
    fig.legend(handles=h,loc='lower center',bbox_to_anchor=(0.5,y),ncol=2,frameon=False,fontsize=10.5)
def head(fig,t,s,x=0.02,y=1.0):
    fig.text(x,y,t,fontsize=15,fontweight='bold',color=INK,va='bottom'); fig.text(x,y-0.012,s,fontsize=10,color=INK2,va='top')
def save(fig,n): fig.savefig(f'{OUT}/{n}.png',dpi=200,bbox_inches='tight'); plt.close(fig)
na=(df.g=='Adults').sum(); ns=(df.g=='Students').sum()

# 6 Hero: same learning, different feelings
fig,(a1,a2)=plt.subplots(1,2,figsize=(12,4.4),gridspec_kw={'width_ratios':[1,1.25],'wspace':0.95})
dumbbell(a1,know,xlim=(60,100)); dumbbell(a2,feel,xlim=(20,100))
a1.set_title('Same learning',loc='left',fontsize=12.5,fontweight='bold',color=INK,pad=8)
a2.set_title('Different feelings',loc='left',fontsize=12.5,fontweight='bold',color=INK,pad=8)
a1.text(0,-0.2,'% agree after the training',transform=a1.transAxes,fontsize=9.5,color=INK2)
a2.text(0,-0.2,'% agree, or % giving 9–10',transform=a2.transAxes,fontsize=9.5,color=INK2)
head(fig,'Students learn as much as adults, but don\'t feel the same',f'Students n = {ns:,}, adults n = {na:,}. "Likely to call 988" was asked on some survey versions only (students 253, adults 40).',x=0.0,y=1.08)
legend(fig,-0.17); save(fig,'6_same_learning_different_feelings')

# 7 Same learning: before and after by group
fig,ax=plt.subplots(figsize=(9,4.8))
items=[('identify','Can identify\nmental health crises'),('describe','Can describe 988'),('when','Know when\nto use 988')]
for i,(k,lab) in enumerate(items):
    for j,g in enumerate(['Students','Adults']):
        y=i*3+j; b,_,_=pct(g,'pre_'+k,agree); a,_,_=pct(g,'post_'+k,agree)
        ax.plot([b,a],[y,y],color=GRAY,lw=3,zorder=1)
        ax.scatter(b,y,s=80,color=SURF,edgecolor=COL[g],lw=2,zorder=2); ax.scatter(a,y,s=100,color=COL[g],edgecolor=SURF,lw=2,zorder=3)
        ax.text(b-2,y,f'{b:.0f}%',ha='right',va='center',fontsize=9.5,color=INK2)
        ax.text(a+2,y,f'{a:.0f}%',ha='left',va='center',fontsize=10,color=COL[g],fontweight='bold')
        ax.text(31,y,g,ha='left',va='center',fontsize=9.5,color=COL[g],fontweight='bold')
ax.set_yticks([i*3+0.5 for i in range(3)]); ax.set_yticklabels([l for _,l in items]); ax.tick_params(axis='y',length=0)
ax.invert_yaxis(); ax.set_xlim(30,102); ax.xaxis.set_major_formatter(lambda v,_:f'{v:.0f}%'); ax.grid(axis='x',color=GRID,lw=.8); ax.set_axisbelow(True)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([],[],marker='o',ls='',ms=8,mfc=SURF,mec=MUTED,mew=2,label='Before (recalled)'),Line2D([],[],marker='o',ls='',ms=9,color=MUTED,label='After')],
          loc='upper center',bbox_to_anchor=(0.5,-0.1),ncol=2,frameon=False,fontsize=10)
head(fig,'Same learning: students and adults end up in the same place','% agree or strongly agree, before vs. after. Students start ahead on "when to use 988"; both finish at 90–93%.',x=0.0,y=1.07)
save(fig,'7_same_learning')

# 8 Different feelings, with 95% CIs
fig,ax=plt.subplots(figsize=(9,4.4))
dumbbell(ax,feel,xlim=(20,105),ci=True)
legend(fig,-0.08)
head(fig,'Different feelings: students are less engaged and less likely to act',f'% agree (presenter items) or % giving 9–10 (0–10 scales). Thin colored lines are 95% confidence intervals.\nThe adult "likely to call" estimate rests on only 40 people.',x=0.0,y=1.1)
save(fig,'8_different_feelings')
