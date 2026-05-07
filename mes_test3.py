import requests
from docxtpl import DocxTemplate
import os

# --- CONFIGURATION ---
ISSUE_ID = "SYS-ENR-VGP-Rouen-Commissioning"  # use idReadable
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

        issue = response.json()
        print("✅ API response received")

        # --- DEFAULT VALUES ---
        nom_assignee = "Non assigné"
        project_num = "N/A"
        client_name = "N/A"

        # --- EXTRACT CUSTOM FIELDS ---
        print("➡️ Parsing custom fields...")
        for field in issue.get("customFields", []):
            name = field.get("name")
            val = field.get("value")

            print(f"Field: {name} -> {val}")  # DEBUG

            if not val:
                continue

            # Assignee
            if name == "Assignee":
                nom_assignee = val.get("fullName", "Non assigné")

            # Project Number (adjust if needed after debug)
            elif name in ["Project Number", "Project Numero", "Project Numéro"]:
                project_num = val.get("name", str(val))

            # Client
            elif name == "Client":
                client_name = val.get("name", str(val))

        # --- SPENT TIME ---
        spent_time = issue.get("spentTime")
        temps_passe = spent_time.get("presentation") if spent_time else "0h"

        return {
            "p_name": issue.get("summary", "Inconnu"),
            "p_num": project_num,
            "p_client": client_name,
            "p_assignee": nom_assignee,
            "p_spent": temps_passe
        }

    except Exception as e:
        print("❌ ERROR:", e)
        return None


# --- MAIN EXECUTION ---
data = get_issue_data()

if not data:
    raise Exception("🚨 No data retrieved. Stopping script.")

print("➡️ Data extracted:", data)

# --- TEMPLATE CHECK ---
print("➡️ Checking template:", TEMPLATE_FILE)

if not os.path.exists(TEMPLATE_FILE):
    raise FileNotFoundError(f" Template not found: {TEMPLATE_FILE}")

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

    print("Context sent to template:")
    for k, v in context.items():
        print(f"   {k}: {v}")

    doc.render(context)
    doc.save(OUTPUT_FILE)

    print(f" SUCCESS: File created -> {OUTPUT_FILE}")
    print("Location:", os.getcwd())

except Exception as e:
    print("Error while generating document:", e)