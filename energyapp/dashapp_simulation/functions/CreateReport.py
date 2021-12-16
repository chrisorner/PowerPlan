from energyapp.dashapp_simulation.functions.exportReport import generate_report, convert_html_to_pdf
import webbrowser


graphs = [
    'https://plotly.com/~christopherp/308',
    'https://plotly.com/~christopherp/306',
    'https://plotly.com/~christopherp/300',
    'https://plotly.com/~christopherp/296'
]

static_report,_ = generate_report(graphs)

#convert_html_to_pdf(static_report, 'report.pdf')
webbrowser.open_new(static_report)