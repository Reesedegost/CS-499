from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from dash import dash_table  # Import dash_table

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["defect_analysis"]
collection = db["defects"]

# Load data from MongoDB into a DataFrame
data = list(collection.find())
df = pd.DataFrame(data)

# Clean up: remove MongoDB's automatic "_id" column if present
if "_id" in df.columns:
    df = df.drop(columns=["_id"])

# Normalize column names (e.g., remove spaces)
df.columns = df.columns.str.replace(" ", "_")

# Count of defects per Part Manf
fig1 = px.bar(
    df.groupby("Part_Manf").size().reset_index(name="Defect_Count").sort_values(by="Defect_Count", ascending=False),
    x="Part_Manf",
    y="Defect_Count",
    title="Defects per Part Manufacturer"
)

# Count of defects per Defect Type
fig2 = px.bar(
    df.groupby("Subject").size().reset_index(name="Defect_Count").sort_values(by="Defect_Count", ascending=False),
    x="Subject",
    y="Defect_Count",
    title="Defects per Defect Type"
)

fig3 = px.line(
    df.groupby("Month_Open").size().reset_index(name="Defect_Count"),
    x="Month_Open",
    y="Defect_Count",
    title="Defects per Month"
)

# Create a heatmap figure
heatmap_fig = px.density_heatmap(
    df,
    x="Part_Manf",
    y="Subject",
    z=None,  # Optional: Use a numeric column for intensity (e.g., "Defect_Count")
    title="Defect Intensity by Manufacturer and Type",
    labels={"Part_Manf": "Part Manufacturer", "Subject": "Defect Type"},
    color_continuous_scale="Viridis"
)

# Adjust the layout to make the heatmap bigger
heatmap_fig.update_layout(
    width=1200,  # Set the width of the heatmap
    height=1200,  # Set the height of the heatmap
    title_font_size=20,  # Optional: Increase the title font size
    margin=dict(l=50, r=50, t=50, b=50)  # Optional: Adjust margins
)

# Get initial unique filter values
def get_unique_values(field):
    return sorted(collection.distinct(field))

# Build Dash app
app = Dash(__name__)

from dash import dash_table  # Import dash_table

# Add an interactive data table to the "Data Table" tab
app.layout = html.Div([
    html.H1("Defect Analysis Dashboard"),
    dcc.Tabs([
        # Tab for Charts
        dcc.Tab(label="Charts", children=[
            html.Div([
                dcc.Graph(figure=fig1),
                dcc.Graph(figure=fig2),
                dcc.Graph(figure=fig3),
            ])
        ]),

        # Tab for Data Table
        dcc.Tab(label="Data Table", children=[
            html.Div([
                html.H3("Defect Data Table"),
                dash_table.DataTable(
                    id="data-table",
                    columns=[{"name": col, "id": col} for col in df.columns],  # Dynamically generate columns
                    data=df.to_dict("records"),  # Convert DataFrame to dictionary
                    style_table={"overflowX": "auto"},  # Enable horizontal scrolling
                    style_cell={"textAlign": "left", "padding": "5px"},  # Cell styling
                    style_header={"fontWeight": "bold"},  # Header styling
                    page_size=10,  # Enable pagination with 10 rows per page
                    sort_action="native",  # Enable sorting
                    filter_action="native",  # Enable filtering
                ),
            ])
        ]),

        # Tab for Map
        dcc.Tab(label="Map", children=[
            html.Div([
                html.H3("Defect Type Heat Map"),
                dcc.Graph(figure=heatmap_fig),  # Display the heatmap here
            ])
        ]),

        # Tab for Feedback
        dcc.Tab(label="Feedback", children=[
            html.Div([
                html.H3("We value your feedback!"),
                html.Label("Your Name:"),
                dcc.Input(id="feedback-name", type="text", placeholder="Enter your name", style={"width": "100%"}),
                html.Label("Your Email:"),
                dcc.Input(id="feedback-email", type="email", placeholder="Enter your email", style={"width": "100%"}),
                html.Label("Your Feedback:"),
                dcc.Textarea(id="feedback-text", placeholder="Enter your feedback here", style={"width": "100%", "height": "100px"}),  # Fixed here
                html.Button("Submit Feedback", id="submit-feedback", n_clicks=0),
                html.Div(id="feedback-confirmation", style={"marginTop": "1rem", "color": "green"}),
            ], style={"maxWidth": "600px", "margin": "auto"})
        ]),
    ]),

    html.Button("Download High-Risk Defects Report (PDF)", id="pdf-download", n_clicks=0),
    html.A("Click here if download doesn't start", href="/download-pdf/", target="_blank")
])

# Callback to handle feedback submission
@app.callback(
    Output("feedback-confirmation", "children"),
    Input("submit-feedback", "n_clicks"),
    [Input("feedback-name", "value"), Input("feedback-email", "value"), Input("feedback-text", "value")]
)
def handle_feedback(n_clicks, name, email, feedback):
    if n_clicks > 0:
        # Process the feedback (e.g., save to a database or file)
        # For simplicity, we'll just print it to the console
        print(f"Feedback received from {name} ({email}): {feedback}")
        return "Thank you for your feedback!"
    return ""

from xhtml2pdf import pisa
import io
from flask import send_file

@app.server.route("/download-pdf/")
def download_pdf():
    # if not data:
        # html = "<h1>No high-risk defects found.</h1>"
    # else:
    df = pd.DataFrame(data)
    summary = df.groupby("Subject").size().reset_index(name="Count")
    html = "<h1>High-Risk Defect Summary</h1><table border='1'><tr><th>Defect Type</th><th>Count</th></tr>"
    for _, row in summary.iterrows():
        html += f"<tr><td>{row['Subject']}</td><td>{row['Count']}</td></tr>"
    html += "</table>"

    pdf_stream = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf_stream)
    pdf_stream.seek(0)
    return send_file(pdf_stream, download_name="high_risk_defects.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=8052)
