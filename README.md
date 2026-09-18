# LinkedIn_Scraping
LinkedIn profile scraper built with Python and Selenium to collect up to 80 Tunisia-based profiles in IT, Data, AI, and related fields, with automatic CSV export.


LinkedIn Profile Scraper – Tunisia

A Python-based LinkedIn profile scraping tool using Selenium to collect up to 80 profiles located in Tunisia and related to IT, Data, Artificial Intelligence, and related fields.

The collected information is automatically stored in a CSV file for further analysis and processing.

--- Features ---
🔎 Searches LinkedIn profiles using a predefined search keyword.
🇹🇳 Collects profiles from Tunisia.
💻 Focuses on IT, Data, AI, and related technical fields.
🎯 Collects up to 80 profiles.
🧠 Automatically identifies the profile domain as:
DATA
AI
IT
or a combination of these domains.
🔍 Detects whether Open To Work is visible in the search result.
👤 Extracts information such as:
Name
Position
Location
Domain
Open To Work status
LinkedIn profile URL
Additional information
💾 Automatically creates and updates a CSV file.
🔄 Includes profile deduplication to avoid saving the same profile multiple times.
📄 Automatically navigates through LinkedIn search result pages.

--- Technologies ---
Python
Selenium
Google Chrome
CSV
Pathlib

--- Requirements ---

Make sure Python is installed on your computer.

Install Selenium with:

pip install selenium

A compatible version of Google Chrome is also required.

--- Configuration ---

Before running the script, open the Python file and replace:

EMAIL_LINKEDIN = "YOUR_EMAIL_HERE"
MOT_DE_PASSE_LINKEDIN = "YOUR_PASSWORD_HERE"

with your LinkedIn credentials.

--- How to Use ---
1. Configure your credentials

Enter your LinkedIn email and password in the configuration section of the script.

2. Run the Python script

Run:

python your_script_name.py

The script will open Google Chrome and access the LinkedIn login page.

3. LinkedIn login

The script fills in the LinkedIn email and password fields.

The login process is then completed through LinkedIn.

4. Apply the Tunisia filter manually

After the search page is opened, the program asks the user to manually:

Open the Locations filter.
Select Tunisia.
Apply the filter.
Keep the existing data search unchanged.
Return to the terminal.
Press ENTER to start the collection.

The Tunisia location filter is intentionally handled manually.

5. Profile collection

Once the user presses ENTER, the script starts collecting profiles from the displayed LinkedIn search results.

Only profiles matching the predefined DATA, AI, or IT keywords are retained.

The script can collect up to 80 profiles and can navigate through a maximum of 15 search result pages.

6. CSV output

The collected profiles are automatically saved into:

candidats_linkedin.csv

The CSV contains:

Column	Description
Nom	Profile name
Poste	Current position or displayed position
Localisation	Profile location
Domaine	Detected domain: DATA, AI, IT
Open To Work	Open To Work status when detected
URL LinkedIn	LinkedIn profile URL
Informations	Additional extracted information
Domain Detection

The script uses predefined keyword lists to identify relevant profiles.

DATA

Examples include:

Data Analyst
Data Scientist
Data Engineer
Business Intelligence
Business Analyst
Power BI
SQL
Data Warehouse
ETL
Analytics
Data Mining
AI

Examples include:

Artificial Intelligence
AI Engineer
Machine Learning
Deep Learning
Computer Vision
NLP
Generative AI
LLM
Neural Networks
Robotics
IT

Examples include:

Software Engineer
Software Developer
Web Developer
DevOps
Cloud
Cybersecurity
System Administrator
Network Engineer
Full Stack
Frontend
Backend
Java
Python
JavaScript
PHP
C++
Open To Work Detection

The script checks the visible text associated with each search result for expressions related to Open To Work.

Possible result:

Détecté

or:

Non détecté
Data Deduplication

The script attempts to prevent duplicate profiles from being stored.

When a LinkedIn profile URL is available, the URL is used for deduplication.

If the URL is not available, the script uses a combination of:

Name
Position
Location
Additional information
Debugging

If no profile results are detected, the script automatically saves the current LinkedIn page source into:

linkedin_debug_final.html

This file can be useful for debugging changes in the LinkedIn page structure.

--- Important Notes ---

This project is intended for educational and research purposes.

LinkedIn's website structure and terms of service may change over time. As a result, Selenium selectors or page elements used by the script may require updates.

The script is designed around the LinkedIn page structure observed during development and may not work unchanged if LinkedIn modifies its interface.

Users are responsible for using the tool in accordance with LinkedIn's applicable terms, policies, and local laws.


--- Author ---

Developed as a Python/Selenium scraping project for collecting and analyzing LinkedIn profile data related to IT, Data, and Artificial Intelligence.
