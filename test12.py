import requests
from docxtpl import DocxTemplate
import os

# --- CONFIGURATION ---
ISSUE_ID = "FRANCE-8"
TOKEN = "perm-ci5oYW1pbGk=.NzctMTM3.2DmnYBuMYzQf04AlOrYtisyZago3Rm"
YOUTRACK_URL = f"https://youtrack.meteocontrol.de/api/issues/{ISSUE_ID}"

TEMPLATE_FILE = "template.docx"
OUTPUT_FILE = f"Rapport_{ISSUE_ID}.docx"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

# Requesting summary and customFields with names and presentation values
params = {
    "fields": "summary,customFields(name,value(name,fullName,presentation,text))"
}

def get_issue_data():
    print(f"--- Fetching Data for {ISSUE_ID} ---")
    try:
        response = requests.get(YOUTRACK_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
        
        issue = response.json()

        # Initial context mapping for template placeholders
        context = {
            "Project": issue.get("summary", "N/A"),
            "ProjectNumero": "N/A",  # Maps to Project Number
            "Subsystem": "N/A",      # New field from screenshot
            "Client": "N/A",
            "subcontractor": "N/A",
            "Assignee": "Non assigné",
            "Spent_time": "0h"
        }

        # Parse custom fields
        for field in issue.get("customFields", []):
            name = field.get("name")
            val = field.get("value")

            if not val:
                continue

            # 1. Project Number (e.g., '251011258' from screenshot)
            if name == "Project Number":
                # Project Number is often a string or single-value field
                context["ProjectNumero"] = val if isinstance(val, str) else val.get("name", str(val))

            # 2. Subsystem (e.g., 'Quotation' from screenshot)
            elif name == "Subsystem":
                # Subsystem is usually a state or single-enum field
                context["Subsystem"] = val.get("name", str(val))

            # 3. Client
            elif name == "Client":
                context["Client"] = val.get("name", str(val))

            # 4. Assignee
            elif name == "Assignee":
                context["Assignee"] = val.get("fullName", "")

            # 5. Spent Time
            elif name == "Spent time":
                context["Spent_time"] = val.get("presentation", "0h") if isinstance(val, dict) else str(val)

        return context

    except Exception as e:
        print(f"❌ API Request Failed: {e}")
        return None

def main():
    data = get_issue_data()
    if not data:
        return

    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Error: Template '{TEMPLATE_FILE}' not found.")
        return

    try:
        doc = DocxTemplate(TEMPLATE_FILE)
        
        # Ensure your Word template has the tag {{Subsystem}}
        doc.render(data)
        doc.save(OUTPUT_FILE)
        print(f"🎉 SUCCESS: {OUTPUT_FILE} generated.")
        print("Data applied:", data)
        
    except PermissionError:
        print(f"❌ PERMISSION ERROR: Close '{OUTPUT_FILE}' in Word first.")
    except Exception as e:
        print(f"❌ Rendering Error: {e}")

if __name__ == "__main__":
    main()