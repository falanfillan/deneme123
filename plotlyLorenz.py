import numpy as np
from dash import Dash, html, dcc, Input, Output, clientside_callback
from scipy.integrate import solve_ivp

# Lorenz equations
def lorenz(t, state, sigma=10, rho=28, beta=8/3):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]

# Solve Lorenz equations
sol = solve_ivp(lorenz, [0, 100], [0.1, 0.1, 0.1], t_eval=np.linspace(0, 100, 10000))

# Prepare data for plotting
x, y, z = sol.y

figure = dict(
    data=[{"x": [], "y": []}],
    layout=dict(xaxis=dict(range=[-25, 25]), yaxis=dict(range=[-25, 25])),
)

app = Dash(__name__, update_title=None)
app.layout = html.Div(
    [
        html.H4("Lorenz System"),
        dcc.Graph(id="graph", figure=dict(figure)),
        dcc.Interval(id="interval", interval=25, max_intervals=400),
        dcc.Store(id="offset", data=0),
        dcc.Store(id="store", data=dict(x=x, y=y)),
    ]
)

clientside_callback(
    """
    function (n_intervals, data, offset) {
        offset = offset % data.x.length;
        const end = Math.min((offset + 10), data.x.length);
        return [[{x: [data.x.slice(offset, end)], y: [data.y.slice(offset, end)]}, [0], 500], end]
    }
    """,
    [
        Output("graph", "extendData"),
        Output("offset", "data"),
    ],
    [Input("interval", "n_intervals")],
    [State("store", "data"), State("offset", "data")],
)

if __name__ == "__main__":
    app.run_server()