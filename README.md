Withings Watch Data & Visualization

A tool to retrieve, process, and visualize health data from the Withings watches using a local SQLite database and a Streamlit dashboard.

To use: 

Install dependencies (pip install -r requirements.txt).

Fill `state.json` with your credentials - instructions for retrieving them can be found at (https://developer.withings.com/api-reference/). Set the lastupdate parameter to midnight of the first day your data starts, as a unix timestamp.

Run `main.py` to enter CLI.

Important note: code for Altair charts in `charts.py` has been drafted using AI agents. While i modified and tested it, i do not claim full authorship. Find prompts used in `prompts.txt`.
