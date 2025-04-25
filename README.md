# Eats Data Miner

If you’ve ever found yourself overspending on food delivery apps like DoorDash, Uber Eats, and Menulog, you’re not alone. Tracking those expenses can quickly become a messy chore. That’s why I created **Eats Data Miner**!

**Eats Data Miner** is designed to automatically extract and organize your DoorDash order receipts into clean, structured data you can easily track and analyze.

---

### 📊 Looker Studio Dashboard

<p align="center">
  <img src="assets/dashboard-screenshot-1.png" alt="Looker Studio Mobile Dashboard" width="800" height="300"/>
</p>

_Real-time insights into spending trends, most-ordered items, and vendor breakdowns — optimized for mobile._

---

### Here’s how it works:

1. **Connect to Gmail** – Authenticates with the Gmail API to fetch order confirmation emails.
2. **Extract** – Parses vendor, items, pricing, fees, and delivery details from email content using a custom-built scraper.
3. **Transform** – Flattens and organizes the extracted data into two clean tables: `Orders` and `Order Items`.
4. **Validate** – Applies built-in rule checks to catch parsing errors early and ensure data quality.
5. **Load** – Saves results locally and updates a connected Google Sheets workbook for easy access.
6. **Visualize** – Connects to a Looker Studio dashboard that automatically refreshes from the Sheet, providing real-time spending insights, ordering trends, and item breakdowns.

---

## Project Setup

### Directory Structure
Before starting, set up the following directory structure in the project root:

- `creds/`: For storing API credentials.
- `data/`: For data files including results of `main.py`. 
    - `cache/`: Subdirectory for cached data files.
  - `cache/`: Subdirectory for cached data files.

Note: The `creds/` and `data` directories are ignored in `.gitignore` for security and privacy reasons.

## Setting Up Credentials

### Gmail API Access
To use the Gmail functionalities, you need to set up your Google API credentials. Follow the *'Set up your environment'* section in this [Python Quickstart guide](https://developers.google.com/gmail/api/quickstart/python), which contains a step-by-step walkthrough.

After completing the guide::
1. Ensure the `creds/` directory exists at the root of the project.
2. Save your credentials as `creds/credentials.json`.

Note: The `creds/` directory is ignored in `.gitignore` for security reasons. Ensure your personal credentials are not pushed to the repository.

### Google Sheets API Access
To utilize the Google Sheets functionalities in the project, configure Google Sheets API credentials:

1. Navigate to the [Google Developer Console](https://console.developers.google.com/).
2. Create a new project or select an existing one.
3. Enable the `Google Sheets API` and the `Google Drive API` for your project.
4. Go to the "Credentials" page and click on "Create Credentials". Choose "Service account".
5. Fill in the service account details (optional, grant it a role with appropriate permissions)
6. Once the service account is created, click on it to manage keys.
7. Add a new key of type JSON. The key file will be downloaded automatically.
8. Rename this file to `sheets_serviceaccount.json` and place it in the `creds/` directory of your project.

Note: Like with the Gmail API, the `creds/` directory is part of the `.gitignore` file to prevent sensitive data from being pushed to the public repository. Ensure you do not upload your personal credentials.

### Set up Access to Doordash Orders Spreadsheet

1. Go to [Google Sheets](https://docs.google.com/spreadsheets/).
2. Create a blank spreadsheet and rename it "Doordash Orders".
3. Click on "Share" and add your service account email as an Editor. This can be found as the value associated with `client_email` in the `sheets_serviceaccount.json` file you created in the previous step.

You're all set up and ready to go!
