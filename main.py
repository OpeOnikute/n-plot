#!/usr/bin/env python3

import re, math
from datetime import datetime
import plotly.graph_objects as go # or plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html

from pyfiglet import print_figlet

class NPlot():
    def __init__(self, max_endpoints=300):

        # Set the max amount of endpoints to display on the graph. The default is 300
        # as the browser won't handle higher than that gracefully.
        self.max_endpoints = max_endpoints

        # Store the total amount of lines traversed
        self.total_hits = 0

        # The regex used to parse the Nginx line matches only up to the endpoint, as that
        # is what is needed for now. It also ignores query params and endpoint variables,
        # as we are only concerned about the base endpoints in the plot.
        # e.g /endpoint/232342342 becomes /endpoint
        self.regex = r"^([0-9\.]+)(\s-\s-\s)(\[.*\])(\s\")([\-a-zA-Z3.\s/]+)(\s|/|\?)"

    def reset(self):
        self.max_endpoints = 300
        self.total_hits = 0
        self.regex = r"^([0-9\.]+)(\s-\s-\s)(\[.*\])(\s\")([\-a-zA-Z3.\s/]+)(\s|/|\?)"

    def match_regex(self, pattern, text, group=1):
        """Match a regex given a pattern and text

        Args:
            pattern (string): 
            text (string): 
            group (string): The match group index to return. Default is the first one.

        Returns:
            string or None: A result or None
        """
        search_obj = re.search(pattern, text, re.I)

        if search_obj:
            return search_obj.groups()

        return None

    def roundup(self, x):
        """rounds up to the nearest 10
        Args:
            x ([type]): [description]

        Returns:
            [type]: [description]
        """
        return int(math.ceil(x / 10.0)) * 10

    def display_graph(self, figure):
        """Displays a graph

        Args:
            figure (plotly.graph_objects.Figure):
        """
        app = dash.Dash()
        app.layout = html.Div([
            dcc.Graph(figure=figure)
        ])

        app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter

    def plot_access_logs(self, filename):
        res = {}
        start_time = 0
        end_time = 0

        try:
            with open(filename, "r") as file:
                for line in file:

                    self.total_hits += 1

                    match = self.match_regex(self.regex, line)
                    endpoint = match[4].replace("HTTP", "")
                    time = match[2].replace("[", "").replace("]", "")

                    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
                    timestamp = datetime.strptime(time, "%d/%b/%Y:%H:%M:%S %z").timestamp()

                    # Set the base start time i.e. min
                    if timestamp < start_time or start_time == 0:
                        start_time = int(timestamp)

                    # Set the base end time i.e. max
                    if timestamp > end_time or end_time == 0:
                        end_time = int(timestamp)

                    if endpoint in res:
                        res[endpoint].append(timestamp)
                    else:
                        res[endpoint] = [timestamp]
                            
                    # max is 300 endpoints for good performance
                    if len(res) >= self.max_endpoints:
                        break
        except FileNotFoundError:
            print("\nThe file path you entered is incorrect. Please check it and try again.\n")
            return False

        # rounds up the interval to the nearest ten for a cleaner plot
        interval = self.roundup((end_time - start_time) / 10)

        # x-axis (time) is the same for all lines 
        x_axis = range(start_time, start_time + (interval * 10), interval)

        # display formatted time on the graph, not timestamp
        x_axis_named = [ str(datetime.fromtimestamp(x)) for x in x_axis]

        fig = go.Figure(
            layout=go.Layout(
                title=go.layout.Title(text="Nginx Access Logs - {:,} hits".format(self.total_hits))
            )
        )

        # aggregate the number of entries an endpoint has for each time interval
        for elem in res:
            timestamps = res[elem]
            
            y_axis = []
            
            # lower limit starts at zero for the first item
            min_y = 0

            # use the intervals to count the number of hits in-between them
            for item in x_axis:
                max_y = item
                
                agg_y = len([ y for y in timestamps if min_y < y and y <= max_y])
                y_axis.append(agg_y)

                # increase the lower limit to the next interval point
                min_y = item
            
            # plot the line on the graph figure
            fig.add_trace(go.Scatter(x=x_axis_named, y=y_axis,
                                mode='lines',
                                name=elem))

        print("\nDone! You can view the graph by going to the URL below:\n")
        self.display_graph(fig)
        return True

if __name__ == "__main__":

    print_figlet("N-Plot", font="slant", colors= "BLUE")

    prompt = "This program helps you plot Nginx URL hits by parsing your access log file.\n\nWhat's the path to the Nginx access logs? (e.g. access.log) "
    path = input(prompt)
    plotter = NPlot()
    plotter.plot_access_logs(path)