# Setup Instructions

> **Goal**  
> Get Eats Data Miner running locally with a connected Google Sheets workbook and a ready-to-use Looker Studio dashboard.

---

## 1. Prerequisites

| Requirement                                          | Why                              |
| ---------------------------------------------------- | -------------------------------- |
| **Python 3.9+**                                      | Core runtime                     |
| **Git**                                              | Clone the repo                   |
| A Google account that receives DoorDash order emails | Data source                      |
| Basic access to the Google Cloud Console             | Enable APIs & create credentials |

---

## 2. Clone the Repository & Create the Project Folders

```bash
git clone https://github.com/your-username/eats-data-miner.git
cd eats-data-miner
mkdir -p creds data/data/cache
```

`creds/` will store API keys.
`data/` will hold CSV outputs; `data/cache/` stores cached raw emails.

---

## 3. Set Up Gmail API Access

1. Go to <https://console.cloud.google.com/> and **create a new project** (or select an existing one).
2. **Enable** the **Gmail API**.
3. Navigate to **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
   - Application type: **Desktop app**
   - Download the `credentials.json` file and place it inside `creds/`.
4. In the project root, run:

   ```bash
   python main.py
   ```

   A browser window will prompt you to grant Gmail access. A token file is stored automatically for future runs.

---

## 4. Set Up Google Sheets API Access

1. In the same Cloud project, **enable** both **Google Sheets API** and **Google Drive API**.
2. **Create a Service Account** (APIs & Services → Credentials → Create Credentials → Service Account). No roles are required.
3. Under the new service account, go to **Keys → Add Key → JSON**.
   - Download the JSON key.
   - Rename it to `sheets_serviceaccount.json` and place it inside `creds/`.

---

## 5. Create & Share the Destination Google Sheet

1. In Google Sheets, create a blank spreadsheet and name it **“Doordash Orders”**.
2. Share the sheet with the **service-account email** (found in `sheets_serviceaccount.json`) and give it **Editor** access.
3. No need to add tabs manually—the script will create “Orders” and “Order Items” worksheets on first run.

---

## 6. Prepare the Looker Studio Dashboard

1. Open <https://lookerstudio.google.com/>.
2. **Create a new report** → **Add data → Google Sheets** → select **“Doordash Orders”**.
3. Use the two worksheets as data sources.
4. Design your own visuals _or_ reach out if you'd like me to help set up a ready-made dashboard.
5. Any time the script updates the Sheet, the dashboard refreshes automatically.

---

## 7. Install Dependencies

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
```

---

## 8. Run the Pipeline

```bash
python main.py
```

- **orders.csv / order_items.csv** saved to `data/`
- **Google Sheet** updated
- **Looker Studio dashboard** reflects the latest data

---

## 9. Troubleshooting

| Symptom                               | Fix                                                                                 |
| ------------------------------------- | ----------------------------------------------------------------------------------- |
| `403: Access Not Configured`          | Ensure the corresponding API is enabled in Google Cloud.                            |
| Service account cannot write to Sheet | Re-check sharing permissions (Editor).                                              |
| Gmail fetch returns zero messages     | Verify email filter: script searches for _DoorDash order confirmation_ emails only. |

---

**That’s it — you’re ready to mine your DoorDash spending data.**
If you hit issues not covered here, open an issue or ping me on GitHub.
