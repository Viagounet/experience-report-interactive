import random

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
from dash.dependencies import Output, Input

timeline_df = pd.read_csv("TR/6APB/timeline.csv", sep=";")
timeline_df['time_format'] = pd.to_datetime(
    timeline_df['time'],
    format='%H:%M'
)

metadata_df = pd.read_csv("TR/6APB/metadata.csv", sep=";")

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Interactive Experiences Report"

metadata_string = ""

for column_name in metadata_df.columns:
    column_name_formatted = column_name[0].upper() + column_name[1:]
    metadata_string += "**{}** : {}\n\n".format(column_name_formatted, metadata_df[column_name][0])

drug_data = """**Substance name** : 6-APB\n
---\n
**Description** : A stimulant, empathogen and analog of MDA. Typically more visual than MDMA or MDA, as well as having a much longer onset and duration. Users often report a slightly more psychedelic headspace as well. Commonly sold as an alternative to MDMA and MDA.\n
---\n
**Key words** : Stimulant, Psychedelic, Research chemical, Empathogen, Habit-forming\n\n
---\n
**Doses** : \n
Light : *50-75mg*\n
Common : *50-125mg*\n
Heavy : *125mg+*\n
"""

graph_select = dcc.Dropdown(
    id='graph-dropdown',
    options=[{"label": column, "value": column} for column in timeline_df.columns if column not in ["dose",
                                                                                                    "time",
                                                                                                    "time_format",
                                                                                                    "comment"]
             ],
    value=['intensity', 'euphoria', 'introspection', 'anxiety'],
    multi=True
)

doses_time = []
doses_substance = []
doses = []
for i, dose in enumerate(timeline_df["dose"]):
    if str(dose) != "0":
        if str(dose.split(":")[1]) != "0":
            doses.append(str(dose.split(":")[1]))
            doses_time.append(timeline_df["time_format"][i])
            doses_substance.append(str(dose.split(":")[0]))


def update_plots(categories):
    main_plots_children = []
    for i, column_name in enumerate(categories):
        layout = go.Layout(
            margin=go.layout.Margin(
                l=0,  # left margin
                r=0,  # right margin
                b=0,  # bottom margin
                t=0,  # top margin
            )
        )

        scatter = go.Scatter(x=timeline_df["time_format"], y=timeline_df[column_name],
                             mode='markers+lines',
                             line_shape='spline',
                             fill='tozeroy',
                             name=column_name,
                             marker_color=px.colors.qualitative.Light24[i],
                             showlegend=False
                             )
        figure = go.Figure(data=scatter, layout=layout)

        figure.update_layout(
            autosize=True,
            paper_bgcolor="rgba(255,255,255,0)",
        )

        for i, dose in enumerate(doses_time):
            dose = dose.timestamp() * 1000
            figure.add_vline(x=dose, line_color="rgba(20,20,20,0.9)", line_dash="dash",
                             annotation_text="{} : {}mg".format(doses_substance[i], doses[i]),
                             annotation_position="top right",
                             annotation_font_size=8)

        trip_stats_scatter = dcc.Graph(id=column_name,
                                       figure=figure,
                                       style={'width': '100%',
                                              'height': "300px",
                                              })

        trip_stats_scatter.figure.update_xaxes(showgrid=False)
        trip_stats_scatter.figure.update_yaxes(showgrid=False, range=[timeline_df[column_name].min(), 10])
        trip_stats_scatter.figure.update_layout(plot_bgcolor='rgba(10,10,10, 0)')

        main_plots_children.append(html.P(children=column_name,
                                          className="plot-description"))
        main_plots_children.append(trip_stats_scatter)
    return main_plots_children


TR_string = ""
for time, comment in zip(timeline_df["time"], timeline_df["comment"]):
    comment = str(comment)
    TR_string += "**T+{} : ** ".format(time)
    for paragraph in comment.split("<br>"):
        TR_string += "*{}* \n\n".format(paragraph)
    TR_string += " --- \n"

main_plots_children = update_plots(graph_select.value)

app.layout = html.Div(
    id="global",
    children=[
        html.Div(
            children=[
                html.Div(id="none", children=[]),
                html.H1(children="Interactive Experiences Report",
                        className="header-title"),
                html.P(children="Visualize your trips!",
                       className="header-description")
            ],
            className="header"
        ),
        html.Div(
            children=[html.P(children="6-APB : A healing experience",
                             className="TR-title-text"), ],
            className="TR-title-div"
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Markdown(metadata_string)
                    ],
                    className="personal-info"
                ),
                html.Div(
                    children=[graph_select,
                              html.Div(
                                  children=[
                                      html.Div(children=main_plots_children,
                                               id="div-plots",
                                               className="graphs-div"),
                                      html.Div(children=dcc.Markdown(TR_string),
                                               id="div-text-info",
                                               className="text-info-div")
                                  ],
                                  className="infos-division")],
                    className="main-info"
                ),
                html.Div(
                    children=[
                        dcc.Markdown(drug_data)
                    ],
                    className="drug-info"
                ),
            ],
            className="global-wrapper"
        ),
        html.Div(children=dcc.Markdown("If you wish to support me (**and harm reduction!**), you can buy me a coffee on : [https://ko-fi.com/viag17483](https://ko-fi.com/viag17483) 😖"),
                 className="footer")
    ]
)


@app.callback(
    dash.dependencies.Output('div-plots', 'children'),
    [dash.dependencies.Input('graph-dropdown', 'value')])
def update_output(categories):
    print(categories)
    children = update_plots(categories)
    print(len(children))
    return children


if __name__ == "__main__":
    app.run_server(debug=True)
