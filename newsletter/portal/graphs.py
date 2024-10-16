import plotly.express as px
import plotly.graph_objects as go

def radar(df, x, y):
    fig = px.line_polar(df, x, y, line_close=True)

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        polar= dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                showticklabels=False,
            )
        )
    )

    fig.update_traces(line_color='lightseagreen', fill='toself', fillcolor='rgba(32,178,170,0.2)')

    fig.update_layout(
        font=dict(color='white', size=10),
        title_text='',
        showlegend=False,
    )

    fig.update_layout(polar=dict(radialaxis=dict(showticklabels=False)))

    return fig


def barras(df, x, y):
    fig = px.bar(df, x, y)

    fig.update_traces(
        marker_color='lightseagreen',
        marker_line_color='lightseagreen',
        marker_line_width=1.5
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    fig.update_layout(
        font=dict(color='white', size=10),
        title_text='',
        showlegend = False,
        xaxis=dict(tickcolor='white', linecolor='white', showgrid=False),
        yaxis=dict(tickcolor='white', linecolor='white', showgrid=False),
    )

    return fig


def barras_comparacao(df):
    colors = {'CLT': 'lightseagreen', 'PJ': 'lightyellow'}
    fig = px.bar(df, x='Categoria', y='Salário', color='Contrato', barmode='group',
                 color_discrete_map=colors)

    fig.update_traces(marker_line_width=0)

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=10),
        showlegend=True,
        xaxis=dict(tickcolor='white', linecolor='white', showgrid=False),
        yaxis=dict(tickcolor='white', linecolor='white', showgrid=False),
        title_font=dict(size=12, color='white')
    )

    return fig


def evolucao_salario(df):

    df['semana'] = df['data_publicacao'].dt.to_period('W').dt.start_time

    fig = go.Figure()

    for senioridade in df['senioridade'].unique():
        df_subset = df[df['senioridade'] == senioridade]
        fig.add_trace(go.Scatter(
            x=df_subset['semana'],
            y=df_subset['salario'],
            mode='lines',
            name=senioridade
        ))

    fig.update_layout(
        xaxis_title='Semana',
        yaxis_title='Salário Médio',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            tickmode='array',
            ticks='outside',
            tickvals=df['semana'].drop_duplicates().sort_values(),
            tickformat='%d-%m-%Y',
            color = 'white',
            title_font = dict(color='white'),
        ),
        yaxis = dict(
            color='white',
            title_font=dict(color='white'),
        ),
        legend_title_text = 'Senioridade',
        legend_title_font_color = 'white',
        legend_font_color = 'white'

    )

    return fig
