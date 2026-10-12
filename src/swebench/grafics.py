"""Construcció dels gràfics Plotly, separada dels components Streamlit."""
import plotly.graph_objects as go

from .configuracio import (COLOR_RAONAMENT, COLOR_ALTRE, FONS, TEXT, TEXT_S)

def format_num(x, decimals=1):
    return f'{x:.{decimals}f}'.replace('.', ',')



def format_signe(x, decimals=1):
    return ('+' if x > 0 else '') + format_num(x, decimals)



def colors_per_mode(df, ampliat):
    raonament = 'Raonament alt' if ampliat else 'Amb raonament'
    return [COLOR_RAONAMENT if m == raonament else COLOR_ALTRE for m in df['modalitat']]



def estil(fig, altura, dret=85, superior=55):
    fig.update_layout(
        template='plotly_white', paper_bgcolor=FONS, plot_bgcolor=FONS,
        font=dict(color=TEXT, size=13), height=altura,
        margin=dict(l=14,r=dret,t=superior,b=46),
        bargap=0.32, hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(
        showgrid=False, showticklabels=False, ticks='', showline=False,
        zeroline=True, zerolinecolor='rgba(15,23,42,0.25)',
        zerolinewidth=1, fixedrange=True, title=None,
    )
    fig.update_yaxes(
        showgrid=False, showline=False, ticks='', fixedrange=True,
        title=None, tickfont=dict(color=TEXT,size=12),
    )



def grafica_general(df, ampliat):
    df = df.sort_values('puntuacio_pct', ascending=False).copy()
    y = df['configuracio'].tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['puntuacio_pct'], y=y, orientation='h',
        marker=dict(color=colors_per_mode(df, ampliat),line_width=0),
        text=[f'{format_num(v)} %' for v in df['puntuacio_pct']],
        textposition='outside',textfont=dict(color=TEXT,size=14),
        customdata=[[m, s] for m,s in zip(df['modalitat'], df['font_valor'])],
        hovertemplate='<b>%{y}</b><br>Resultat: %{x:.1f} %<br>Condició: %{customdata[0]}<extra></extra>',
        cliponaxis=False,showlegend=False,
    ))
    llegenda = (
        [('Amb raonament',COLOR_RAONAMENT),('Sense raonament',COLOR_ALTRE)]
        if not ampliat else
        [('Raonament alt (high)', COLOR_RAONAMENT),('Esforç no indicat', COLOR_ALTRE)]
    )
    for etiqueta,color in llegenda:
        fig.add_trace(go.Scatter(
            x=[None],y=[None],mode='markers',name=etiqueta,
            marker=dict(color=color,size=12,symbol='square'),
            showlegend=True,hoverinfo='skip',
        ))
    estil(fig,altura=405 if not ampliat else 540,superior=72)
    fig.update_layout(
        legend=dict(orientation='h',x=0,y=1.10,yanchor='bottom',
                    bgcolor='rgba(0,0,0,0)',font=dict(size=13,color=TEXT)),
        hovermode='closest',
    )
    fig.update_xaxes(range=[0,100], title_text='Tasques resoltes (%)',
                     title_font=dict(color=TEXT, size=12))
    fig.update_yaxes(categoryorder='array',categoryarray=y,autorange='reversed')
    return fig



def grafica_parella(a,b,pa,pb,ma,mb,amb_index,ampliat):
    if amb_index:
        vals = [100*pa/pb,100.0]
        etiquetes = [format_num(vals[0])+' punts d’índex','100,0 punts d’índex']
        final = max(115.0,max(vals)*1.2)
        missatge = 'Índex B = 100'
    else:
        vals = [pa,pb]
        etiquetes = [format_num(pa)+' %',format_num(pb)+' %']
        final = 100
        missatge = 'Tasques resoltes (%)'
    raonament = 'Raonament alt' if ampliat else 'Amb raonament'
    col = [COLOR_RAONAMENT if m == raonament else COLOR_ALTRE for m in [ma,mb]]
    fig = go.Figure(go.Bar(
        x=vals,y=['A - '+a,'B - '+b],orientation='h',
        marker=dict(color=col,line=dict(color=[col[0],'#E2E8F0'],width=[0,2])),
        text=etiquetes,textposition='outside',textfont=dict(color=TEXT,size=13),
        customdata=[[format_num(pa)+' %',ma],[format_num(pb)+' %',mb]],
        hovertemplate='<b>%{y}</b><br>'+missatge+': %{text}'
            '<br>Puntuació original: %{customdata[0]}'
            '<br>Condició: %{customdata[1]}<extra></extra>',
        cliponaxis=False,showlegend=False,
    ))
    estil(fig,altura=215,dret=150,superior=12)
    fig.update_xaxes(range=[0,final],
                     title_text=('Índex normalitzat (B = 100)' if amb_index else 'Tasques resoltes (%)'),
                     title_font=dict(color=TEXT, size=12))
    fig.update_yaxes(autorange='reversed')
    return fig

