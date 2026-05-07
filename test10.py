import requests
from docxtpl import DocxTemplate
import os

# --- CONFIGURATION ---
ISSUE_ID = "sysdes-33612"  # use idReadable
TOKEN = "perm-ci5oYW1pbGk=.NzctMTM3.2DmnYBuMYzQf04AlOrYtisyZago3Rm"

YOUTRACK_URL = f"https://youtrack.meteocontrol.de/api/issues/{ISSUE_ID}"
TEMPLATE_FILE = "template.docx"
OUTPUT_FILE = f"Rapport_{ISSUE_ID}.docx"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

params = {
    "fields": "summary,spentTime(presentation),customFields(name,value(name,fullName,presentation,text))"
}

print("=== SCRIPT STARTED ===")


def get_issue_data():
    print(" Calling YouTrack API...")

    try:
        response = requests.get(YOUTRACK_URL, headers=headers, params=params, timeout=10)
        print("Status Code:", response.status_code)

        if response.status_code == 401:
            raise Exception(" Unauthorized (bad token)")
        if response.status_code == 404:
            raise Exception(f" Issue not found: {ISSUE_ID}")
        
        response.raise_for_status() # Catch other HTTP errors
        
        issue = response.json()
        print("API response received")

        # --- INITIALIZE DEFAULT VALUES ---
        # This prevents "NameError" if the fields aren't found in the loop
        assignee_name = "N/A"
        project_num = "N/A"
        client_name = "N/A"

        # --- EXTRACT CUSTOM FIELDS ---
        print(" Parsing custom fields...")
        for field in issue.get("customFields", []):
            field_name = field.get("name")
            val = field.get("value")

            if not val:
                continue

            # Assignee
            if field_name == "Assignee":
                # Check if it's a single user or list
                if isinstance(val, list): val = val[0]
                assignee_name = val.get("fullName", val.get("name", "N/A"))

            # Project Number
            elif field_name in ["Project Number", "Project Numero", "Project Numéro"]:
                project_num = val.get("name", str(val))

            # Client
            elif field_name == "Client":
                client_name = val.get("name", str(val))

        # --- SPENT TIME ---
        spent_time = issue.get("spentTime")
        temps_passe = spent_time.get("presentation") if spent_time else "0h"

        return {
            "p_name": issue.get("summary", "Inconnu"),
            "p_num": project_num,
            "p_client": client_name,
            "p_assignee": Assignee,
            "p_spent": spent_time
        }

    except Exception as e:
        print(f"ERROR: {e}")
        return None


# --- MAIN EXECUTION ---
data = get_issue_data()

if not data:
    # This matches your screenshot error - it triggers because the function returned None
    print("🚨 No data retrieved. Check the error message above.")
    exit(1)

print("Data extracted successfully.")

# --- TEMPLATE CHECK ---
if not os.path.exists(TEMPLATE_FILE):
    print(f"❌ Template not found: {TEMPLATE_FILE}")
    exit(1)

# --- GENERATE DOCUMENT ---
try:
    print(" Generating Word document...")
    doc = DocxTemplate(TEMPLATE_FILE)

    context = {
        "Project_Name": data["p_name"],
        "Project_Number": data["p_num"],
        "Client": data["p_client"],
        "Assignee": data["p_assignee"],
        "spenttime": data["p_spent"]
    }

    doc.render(context)
    doc.save(OUTPUT_FILE)

    print(f" SUCCESS: File created -> {OUTPUT_FILE}")

except Exception as e:
    print("Error while generating document:", e)