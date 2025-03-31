# %%
import dash
from dash import html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

# ======================================= Initialisation de l'application =================================== #
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# ======================================= Chargement et traitement des données ============================== #
file_path = "supermarket_sales.csv"
df = pd.read_csv(file_path)
df['Date'] = pd.to_datetime(df['Date'])
df['Week'] = df['Date'].dt.strftime('%Y-%U')  # Année-Semaine

# ======================================= Layout de l'application =========================================== #
app.layout = dbc.Container([
    dbc.Row([
        html.H1("Tableau de Bord des Ventes du Supermarché", 
                     style={'fontSize': '30px','fontWeight': 'bold','color': 'white', 'textAlign': 'center'}),
    ], style={'display': 'flex', 'alignItems': 'center','justifyContent': 'center', 'width': '100%', 'marginBottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='filtre_ville',
                options=[{'label': city, 'value': city} for city in df['City'].unique()],
                clearable=True,
                placeholder='Choississez une ville :',
                style = {'width': '80%'}
            )], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'height': '100%'},
            width=6),
        dbc.Col([
            dcc.Dropdown(
                id='filtre_genre',
                options=[{'label': gender, 'value': gender} for gender in df['Gender'].unique()],
                clearable=True,
                placeholder='Choississez un genre :',
                style = {'width': '80%'}
            )], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'height': '100%'},
            width=6)
    ], style={'marginBottom': '40px'}),
    
    dbc.Row([
        # Indicateurs clés
        dbc.Col([
            ## Total des ventes
            dbc.Row([
                dbc.Card([
                    dbc.CardHeader("Montant total des Achats", style={'textAlign': 'center'}),
                    dbc.CardBody(html.H4(id='Total_achat', children='0 $', style={'textAlign': 'center', 'fontSize': '50px'}))
                ], style={'marginLeft': '20px', 'width': '90%', 'backgroundColor': '#eaeaea'}) 
            ], style={'height': '45%', 'marginBottom': '20px'}),
            ## Moyenne des évaluations
            dbc.Row([
                dbc.Card([
                    dbc.CardHeader("Évaluation Moyenne", style={'textAlign': 'center'}),
                    dbc.CardBody(html.H4(id='Evaluation_moyenne', children='0 / 10', style={'textAlign': 'center', 'fontSize': '50px'}))
                ], style={'marginLeft': '20px', 'width': '90%', 'backgroundColor': '#eaeaea'}) 
            ], style={'height': '45%', 'marginBottom': '10px'})
        ], width=4),
        # Courbe
        dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id='line-chart'))
            ]), width=8)
    ], style={'marginBottom': '20px'}),
    
    dbc.Row([  
        # Histogramme
        dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id='histogram'))
            ]), width=6),
        # Diagramme circulaire
        dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id='pie-chart'))
            ]), width=6)
    ])
], fluid=True, style={'backgroundColor': '#4682B4', 'padding': '30px'})

# ================================================= Callbacks ================================================= #

## Callback des indicateurs
@callback(
    [Output('Total_achat', 'children'),
     Output('Evaluation_moyenne', 'children')],
    [Input('filtre_ville', 'value'),
     Input('filtre_genre', 'value')]
)
def update_indicators(selected_city, selected_gender):
    filtered_df = df.copy()

    ### Filtrer par ville si sélectionnée
    if selected_city:
        filtered_df = filtered_df[filtered_df['City'] == selected_city]

    ### Filtrer par genre si sélectionné
    if selected_gender:
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]


    # Calcul de l'évaluation moyenne
    Evaluation_moyenne = filtered_df['Rating'].mean()
    Seuil_Evaluation_recommande = 7
    pourcentage_variation_eval = ((Evaluation_moyenne - Seuil_Evaluation_recommande) / Seuil_Evaluation_recommande) * 100

    # Logique de coloration pour l'évaluation
    eval_color = 'green' if Evaluation_moyenne >= 7 else 'red'
    eval_trend = '▲' if Evaluation_moyenne >= 7 else '▼'

    eval_format = html.Div([
        html.Span(f"{Evaluation_moyenne:.2f} / 10", style={'fontSize': '1em'}),
        html.Span(
            f"{eval_trend} {pourcentage_variation_eval:.2f}%",
            style={
                'color': eval_color,
                'fontSize': '0.6em',
                'display': 'block',
            }
        )
    ])

    return f"{filtered_df['Total'].sum():,.2f} $", eval_format


## Callback des graphiques
@callback(
    [Output('line-chart', 'figure'),
     Output('histogram', 'figure'),
     Output('pie-chart', 'figure')
     ],
    [Input('filtre_ville', 'value'),
     Input('filtre_genre', 'value')
    ]
)
def update_dashboard(selected_city, selected_gender):
    filtered_df = df.copy()
    
    ### Filtrer par ville si sélectionnée
    if selected_city:
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    
    ### Filtrer par genre si sélectionné
    if selected_gender:
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
     # Définition des palettes de couleurs
    male_color = "#FF6347"  # Rouge Tomato pour Male
    female_color = "#4169E1"  # Bleu Royal pour Female
    default_line_color = "#8A2BE2"  # Violet par défaut
    
    # Choix de la couleur pour la courbe
    line_color = (male_color if selected_gender == 'Male' else 
                  (female_color if selected_gender == 'Female' else 
                   default_line_color))
    
    hist_color_male = "#FF6347"
    hist_color_female = "#4169E1"
    
    # Évolution des ventes par semaine
    sales_by_week = filtered_df.groupby('Week')['Total'].sum().reset_index()
    sales_by_week['Week_Label'] = ['S' + str(i + 1) for i in range(len(sales_by_week))] # Labels des semaines
    line_fig = px.line(sales_by_week, x='Week_Label', y='Total', 
                       title='Evolution du montant total des achats par semaine',
                       color_discrete_sequence=[line_color])
    line_fig.update_traces(
        hovertemplate='<b>Semaine:</b> %{customdata[0]}<br><b>Total des ventes:</b> %{y:,.2f} $<extra></extra>',
        customdata=sales_by_week[['Week']] # Ajout de la colonne 'Week' pour le survol
    )
    line_fig.update_layout(
        plot_bgcolor="#f7f7f7",  # Couleur de fond de l'aire de tracé
        paper_bgcolor="#eaeaea",  # Couleur de fond de tout le graphique
        xaxis=dict(tickcolor="black", tickangle=0),  # Orientation verticale de la légende x
        yaxis=dict(tickcolor="black"),
        font=dict(color="#333333")
    )
    
    # Histogramme de la répartition des montants totaux des achats par sexe
    if selected_gender == 'Male':
        hist_fig = px.histogram(filtered_df, x="Total", color="Gender", 
                                barmode="group", 
                                color_discrete_map={'Male': hist_color_male, 'Female': '#CCCCCC'},
                                title="Répartition des Montants Totaux des Achats")
    elif selected_gender == 'Female':
        hist_fig = px.histogram(filtered_df, x="Total", color="Gender", 
                                barmode="group", 
                                color_discrete_map={'Female': hist_color_female, 'Male': '#CCCCCC'},
                                title="Répartition des Montants Totaux des Achats")
    else:
        # Par défaut, couleurs originales
        hist_fig = px.histogram(filtered_df, x="Total", color="Gender", 
                                barmode="group", 
                                title="Répartition des Montants Totaux des Achats")
    
    hist_fig.update_layout(
        plot_bgcolor="#f7f7f7",  
        paper_bgcolor="#eaeaea",  
        xaxis=dict(tickcolor="black"),
        yaxis=dict(tickcolor="black"),
        font=dict(color="#333333"),
        bargap=0.2,  
        bargroupgap=0.1
    )
    
    # Diagramme circulaire
    pie_fig = px.pie(filtered_df, names='Product line', title='Répartition des Catégories de Produits')
    pie_fig.update_traces(marker=dict(line=dict(color='grey', width=1)))
    pie_fig.update_layout(
        plot_bgcolor="#f7f7f7", 
        paper_bgcolor="#eaeaea",  
        font=dict(color="#333333")
    )
    return line_fig, hist_fig, pie_fig

# ======================================== Exécution du serveur ======================================== #
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)
