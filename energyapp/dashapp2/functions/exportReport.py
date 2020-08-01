import numpy as np
import pandas as pd
import xhtml2pdf
import plotly.tools as tls
import plotly.graph_objs as go
from xhtml2pdf import pisa
import json
import requests
from requests.auth import HTTPBasicAuth

username = 'christianorner' # Replace with YOUR USERNAME
api_key = 'rDZwRMFq2BJ5ixdMlf3I' # Replace with YOUR API KEY
auth = HTTPBasicAuth(username, api_key)
headers = {'Plotly-Client-Platform': 'python'}


def report_block_template(report_type, graph_url, caption=''):
    if report_type == 'interactive':
        graph_block = '<iframe style="border: none;" src="{graph_url}.embed" width="50%" height="50%"></iframe>'
    elif report_type == 'static':
        graph_block = (''
            '<a href="{graph_url}" target="_blank">' 
                '<img style="height: 200px width:200px;" src="{graph_url}.png">'
            '</a>')

    with open('energyapp/dashapp2/functions/report_template.html') as f:
        report_template = f.read()

    report_block = report_template.format(graph_url=graph_url, caption=caption)

    with open('energyapp/dashapp2/functions/report.html', 'w') as fw:
        fw.write(report_block)

    return report_block


from xhtml2pdf import pisa             # import python module

# Utility function
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return True on success and False on errors
    return pisa_status.err


def generate_report(graphs):
    interactive_report = ''
    static_report = ''


    for graph_url in graphs:
        _static_block = report_block_template('static', graph_url, caption='')
        _interactive_block = report_block_template('interactive', graph_url, caption='')

        static_report += _static_block
        interactive_report += _interactive_block

    return static_report, interactive_report


def get_pages(username, page_size):
    url = 'https://api.plot.ly/v2/folders/all?user='+username+'&page_size='+str(page_size)
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code != 200:
        return
    page = json.loads(response.content)
    yield page
    while True:
        resource = page['children']['next']
        if not resource:
            break
        response = requests.get(resource, auth=auth, headers=headers)
        if response.status_code != 200:
            break
        page = json.loads(response.content)
        yield page

def permanently_delete_files(username, page_size=500, filetype_to_delete='plot'):
    for page in get_pages(username, page_size):
        for x in range(0, len(page['children']['results'])):
            fid = page['children']['results'][x]['fid']
            res = requests.get('https://api.plot.ly/v2/files/' + fid, auth=auth, headers=headers)
           # res.raise_for_status()
            if res.status_code == 200:
                json_res = json.loads(res.content)
                if json_res['filetype'] == filetype_to_delete:
                    # move to trash
                    requests.post('https://api.plot.ly/v2/files/'+fid+'/trash', auth=auth, headers=headers)
                    # permanently delete
                    requests.delete('https://api.plot.ly/v2/files/'+fid+'/permanent_delete', auth=auth, headers=headers)
