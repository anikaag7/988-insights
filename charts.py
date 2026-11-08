import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
def proportion_confint(k,n,method='wilson',z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*((p*(1-p)/n+z*z/(4*n*n))**0.5)/d; return c-h,c+h
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clean import load_and_clean
df, _ = load_and_clean(sys.argv[1] if len(sys.argv) > 1 else 'data/survey.xlsx')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'outputs/charts'
os.makedirs(OUT, exist_ok=True)
BLUE,ORANGE,RED,GRAY='#2a78d6','#eb6834','#e34948','#c3c2b7'
INK,INK2,MUTED,SURF='#0b0b0b','#52514e','#8a8984','#fcfcfb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':GRAY,'axes.labelcolor':INK2,
 'xtick.color':INK2,'ytick.color':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF,'savefig.facecolor':SURF,
 'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':14,'axes.titleweight':'bold','axes.titlecolor':INK,'axes.titlelocation':'left'})
def sub(ax,t): ax.text(0,1.02,t,transform=ax.transAxes,color=INK2,fontsize=10,va='bottom')
def save(fig,n): fig.savefig(f'{OUT}/{n}.png',dpi=200,bbox_inches='tight'); plt.close(fig)
N=len(df)

# 1 Before/after dumbbell
items=[('describe','Can describe 988 and how it works'),('when','Know when to use 988'),('identify','Can identify mental health crises')]
fig,ax=plt.subplots(figsize=(8,3.6))
for y,(k,lab) in enumerate(items[::-1]):
    b=round((df['pre_'+k]>=4).mean()*100+1e-9); a=round((df['post_'+k]>=4).mean()*100+1e-9)
    ax.plot([b,a],[y,y],color=GRAY,lw=2.5,zorder=1)
    ax.scatter([b],[y],s=90,color=SURF,edgecolor=MUTED,lw=2,zorder=2)
    ax.scatter([a],[y],s=90,color=BLUE,edgecolor=SURF,lw=2,zorder=3)
    ax.text(b-2,y+0.22,f'{b:.0f}%',ha='right',color=INK2,fontsize=10)
    ax.text(a+2,y+0.22,f'{a:.0f}%',ha='left',color=INK,fontsize=10,fontweight='bold')
ax.set_yticks(range(3)); ax.set_yticklabels([l for _,l in items[::-1]],color=INK)
ax.set_xlim(30,105); ax.set_ylim(-0.6,2.8); ax.xaxis.set_major_formatter(lambda v,_:f'{v:.0f}%')
ax.grid(axis='x',color='#ecebe8',lw=0.8); ax.set_axisbelow(True); ax.spines['left'].set_visible(False); ax.tick_params(axis='y',length=0)
ax.set_title('Knowledge jumps after the training',pad=28)
sub(ax,f'% who agree or strongly agree, before vs. after (n = {N:,}). "Before" was rated after the training.')
ax.scatter([],[],s=70,color=SURF,edgecolor=MUTED,lw=2,label='Before (recalled)'); ax.scatter([],[],s=70,color=BLUE,label='After')
ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.12),ncol=2,frameon=False,fontsize=10)
save(fig,'1_knowledge_before_after')

# 2 Recommend: students vs adults, diverging stacked
df['grp']=np.where(df.role=='Student','Students','Adults')
fig,ax=plt.subplots(figsize=(8,2.9))
for y,g in enumerate(['Adults','Students']):
    r=df.loc[df.grp==g,'recommend'].dropna(); n=len(r)
    d,p,pr=(r<=6).mean()*100,((r>=7)&(r<=8)).mean()*100,(r>=9).mean()*100
    ax.barh(y,-d,color=RED,height=0.55,edgecolor=SURF,lw=2); ax.barh(y,p,color=GRAY,height=0.55,edgecolor=SURF,lw=2); ax.barh(y,pr,left=p,color=BLUE,height=0.55,edgecolor=SURF,lw=2)
    ax.text(-d-2,y,f'{d:.0f}%',ha='right',va='center',color=INK2,fontsize=10)
    ax.text(p+pr+2,y,f'{pr:.0f}%',ha='left',va='center',color=INK2,fontsize=10)
    ax.text(-62,y,f'{g}\nn = {n:,}   NPS {pr-d:+.0f}',ha='right',va='center',color=INK,fontsize=10.5)
ax.axvline(0,color=MUTED,lw=1); ax.set_xlim(-60,100); ax.set_yticks([]); ax.spines['left'].set_visible(False)
ax.xaxis.set_major_formatter(lambda v,_:f'{abs(v):.0f}%')
ax.set_title('Adults love the training; students are split',pad=28,x=-0.32)
ax.text(-0.32,1.02,'"How likely are you to recommend this training?" (0–10)',transform=ax.transAxes,color=INK2,fontsize=10)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=RED,label='0–6 (detractor)'),Patch(color=GRAY,label='7–8 (passive)'),Patch(color=BLUE,label='9–10 (promoter)')],
 loc='upper center',bbox_to_anchor=(0.4,-0.18),ncol=3,frameon=False,fontsize=10)
save(fig,'2_recommend_students_vs_adults')

# 3 Intent gap
i=df[df.call988.notna()&(df.post_when>=4)]
fig,ax=plt.subplots(figsize=(8,3.2))
rows=[('Adults',i[i.grp=='Adults']),('Students',i[i.grp=='Students'])]
for y,(g,s) in enumerate(rows):
    k=(s.call988<=6).sum(); n=len(s); p=k/n*100; lo,hi=[v*100 for v in proportion_confint(k,n,method='wilson')]
    ax.barh(y,p,color=ORANGE if g=='Students' else BLUE,height=0.5)
    ax.errorbar(p,y,xerr=[[p-lo],[hi-p]],color=INK2,capsize=4,lw=1.2)
    ax.text(hi+1.5,y,f'{p:.0f}%  (n = {n})',va='center',color=INK,fontsize=10.5)
ax.set_yticks([0,1]); ax.set_yticklabels(['Adults','Students'],color=INK,fontsize=11); ax.tick_params(axis='y',length=0)
ax.set_xlim(0,50); ax.xaxis.set_major_formatter(lambda v,_:f'{v:.0f}%'); ax.grid(axis='x',color='#ecebe8',lw=0.8); ax.set_axisbelow(True)
ax.set_title('Knowing about 988 ≠ willing to call it, for students',pad=44)
sub(ax,'Of people who agree they "know when to use 988": % rating likelihood to call 988 at 6 or below (0–10).\nBars show 95% confidence intervals. Only asked on some survey versions.')
save(fig,'3_intent_gap')

# 4 Survey version problem
m=df.start.dt.to_period('M')
t=pd.DataFrame({'asked':df.call988.notna()}).groupby(m).asked.agg(['sum','size'])
fig,ax=plt.subplots(figsize=(9,3.6)); x=np.arange(len(t))
ax.bar(x,t['size']-t['sum'],color=GRAY,width=0.7,label='"Likely to call 988" not on form',edgecolor=SURF,lw=1)
ax.bar(x,t['sum'],bottom=t['size']-t['sum'],color=BLUE,width=0.7,label='Question answered',edgecolor=SURF,lw=1)
ax.set_xticks(x); ax.set_xticklabels([p.strftime('%b\n%y') for p in t.index],fontsize=9)
ax.set_ylabel('Responses'); ax.grid(axis='y',color='#ecebe8',lw=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False,loc='upper left',fontsize=10)
ax.set_title('The key behavior question is missing from most surveys',pad=28)
sub(ax,f'Responses per month. Only {df.call988.notna().sum()} of {N:,} ({df.call988.notna().mean()*100:.0f}%) include "How likely are you to call 988?"')
save(fig,'4_survey_versions')

# 5 Who was surveyed
fig,(a1,a2)=plt.subplots(1,2,figsize=(10,3.6),gridspec_kw={'wspace':0.7})
for ax,col,title in [(a1,'role','By role'),(a2,'county','By county')]:
    v=df[col].value_counts().sort_values()
    ax.barh(v.index,v.values,color=BLUE,height=0.6)
    for yy,val in enumerate(v.values): ax.text(val+15,yy,f'{val:,}',va='center',fontsize=9.5,color=INK2)
    ax.set_xlim(0,v.max()*1.2); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.tick_params(axis='y',length=0,labelcolor=INK)
    ax.set_title(title,fontsize=11.5,pad=6)
fig.suptitle(f'Who answered the survey (n = {N:,})',x=0.08,ha='left',fontweight='bold',fontsize=14,color=INK,y=1.04)
fig.text(0.08,0.955,'Students are 83% of responses; most other groups are too small to compare on their own.',fontsize=10,color=INK2)
save(fig,'5_who_responded')
