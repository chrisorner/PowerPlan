from dash.dependencies import Input, Output

def register_callbacks(dashapp):
    @dashapp.callback(
        Output('dummy_div3', 'children'), 
        [Input('dummy_div2', 'children')])
    def update_graph(input_value):
        return input_value