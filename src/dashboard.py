import pandas as pd
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from raingauge_manager import Raingauge

raingauge=Raingauge()
raingauge.set_db()
df_daily=raingauge.get_precipitation(begin="2022-10-01 00:00:00", end="2022-10-31 23:59:59", freq="D")
del raingauge

datetimes=[t.strftime("%Y%m%d") for t in df_daily.index]
app=Dash(__name__)
app.layout=html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(id="date-button",options=[{"label":t,"value":t} for t in datetimes], value="20221014")
        ]),
    dcc.Graph(id="graph"),

    ])
])

@app.callback(
    Output("graph","figure"),
    Input("date-button","value")
)
def update_figure(date_button):
    target_date=pd.to_datetime(date_button, format="%Y%m%d")

    hourly_start=target_date - pd.offsets.Day(3)
    hourly_end=target_date + pd.offsets.Day(1) -pd.offsets.Second(1)

    daily_start=target_date - pd.offsets.Day(30)
    daily_end=target_date
    fmt="%Y-%m-%d %H:%M:%S"
    s_hourly_start=hourly_start.strftime(fmt)
    s_hourly_end=hourly_end.strftime(fmt)
    s_daily_start=daily_start.strftime(fmt)
    s_daily_end=daily_end.strftime(fmt)

    raingauge=Raingauge()
    raingauge.set_db()
    df_hourly=raingauge.get_precipitation(begin=s_hourly_start, end=s_hourly_end)
    df_daily=raingauge.get_precipitation(begin=s_daily_start, end=s_daily_end, freq="D")
    
    fig=make_subplots(rows=2,cols=1,subplot_titles=["hourly","daily"])
    fig.add_trace(go.Bar(x=df_hourly.index, y=df_hourly["precip_mm"]),row=1,col=1 )
    fig.add_trace(go.Bar(x=df_daily.index, y=df_daily["precip_mm"]), row=2,col=1)
    fig.update_layout(
        height=700
    )
    
    del raingauge
    return fig

if __name__=="__main__":
    app.run_server(debug=True, port=8050,host="localhost")