# ------------------------------------------------------------
# Import required libraries
# ------------------------------------------------------------
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ------------------------------------------------------------
# Read the SpaceX launch data directly from IBM cloud
# ------------------------------------------------------------
spacex_df = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/'
    'IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv',
    encoding="ISO-8859-1"
)

# Add human-readable outcome labels
spacex_df['Outcome'] = spacex_df['class'].map({0: 'Failure', 1: 'Success'})

# Get min and max payload values for slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique booster versions
booster_versions = spacex_df['Booster Version Category'].unique().tolist()

# ------------------------------------------------------------
# Create a Dash application
# ------------------------------------------------------------
app = dash.Dash(__name__)

# ------------------------------------------------------------
# Application Layout
# ------------------------------------------------------------
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=int(min_payload), max=int(max_payload), step=1000,
        marks={i: str(i) for i in range(0, 10001, 2000)},
        value=[int(min_payload), int(max_payload)]
    ),
    html.Br(),

    # Booster Version dropdown
    html.P("Select Booster Version:"),
    dcc.Dropdown(
        id='booster-dropdown',
        options=[{'label': 'All Boosters', 'value': 'ALL'}] +
                [{'label': booster, 'value': booster} for booster in booster_versions],
        value='ALL',
        placeholder="Select a Booster Version",
        searchable=True
    ),
    html.Br(),

    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------

# Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Show total successful launches by site
        filtered_df = spacex_df[spacex_df['Outcome'] == 'Success']
        fig = px.pie(filtered_df, names='Launch Site', values='class',
                     title='Total Successful Launches by Site')
    else:
        # Show success vs failure for selected site
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(site_df, names='Outcome',
                     title=f'Success vs Failure for {selected_site}')
    return fig

# Scatter plot callback with booster filter
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value'),
     Input('booster-dropdown', 'value')]
)
def update_scatter_chart(selected_site, payload_range, booster_choice):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    if booster_choice != 'ALL':
        filtered_df = filtered_df[filtered_df['Booster Version Category'] == booster_choice]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='Outcome',
                     color='Booster Version Category',
                     title='Payload vs Launch Outcome',
                     labels={'Outcome': 'Launch Outcome'})
    return fig

# ------------------------------------------------------------
# Run the app (modern style)
# ------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
