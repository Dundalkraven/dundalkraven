import requests
from docxtpl import DocxTemplate
import os

# --- CONFIG ---
ISSUE_ID = "sysdes-33612"
TOKEN = "perm-ci5oYW1pbGk=.NzctMTM3.2DmnYBuMYzQf04AlOrYtisyZago3Rm"
YOUTRACK_URL = f"https://youtrack.meteocontrol.de/api/issues/{ISSUE_ID}"

TEMPLATE_FILE = "template.docx"
OUTPUT_FILE = f"Rapport_{ISSUE_ID}.docx"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

params = {
    "fields": "summary,customFields(name,value(name,fullName,presentation,text))"
}

def get_issue_data():
    print(f"--- Processing {ISSUE_ID} ---")
    try:
        response = requests.get(YOUTRACK_URL, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None

        issue = response.json()
        summary = issue.get("summary", "")

        # --- SPLIT SUMMARY (1=Client, 2=Project, 3=Subsystem) ---
        # Splitting by " - " based on the screenshot pattern
        parts = [p.strip() for p in summary.split("-")]
        
        context = {
            "Client": parts[0] if len(parts) > 0 else "N/A",
            "Project": parts[1] if len(parts) > 1 else "N/A",
            "Subsystem": parts[2] if len(parts) > 2 else "N/A",
            "ProjectNumero": "N/A",
            "OrderNo": "N/A",       # New field
            "CustomerPA": "N/A",    # New field
            "subcontractor": "N/A",
            "Assignee": "Non assigné",
            "Spent_time": "0h"
        }

        # --- PARSE SIDEBAR CUSTOM FIELDS ---
        for field in issue.get("customFields", []):
            name = field.get("name")
            val = field.get("value")

            if not val:
                continue

            # Project Number
            if name == "Project Number":
                context["ProjectNumero"] = val.get("name", str(val)) if isinstance(val, dict) else str(val)

            # Order No (Matching sidebar in image_79a3e7.png)
            elif name == "Order No":
                context["OrderNo"] = str(val)

            # Customer pA (Matching sidebar in image_79a3e7.png)
            elif name == "Customer pA":
                context["CustomerPA"] = str(val)

            # Assignee
            elif name == "Assignee":
                context["Assignee"] = val.get("fullName", "")

            # Spent time
            elif name == "Spent time":
                context["Spent_time"] = val.get("presentation", "0h") if isinstance(val, dict) else str(val)

        return context

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    data = get_issue_data()
    if not data: return

    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Template missing: {TEMPLATE_FILE}")
        return

    try:
        doc = DocxTemplate(TEMPLATE_FILE)
        doc.render(data)
        doc.save(OUTPUT_FILE)
        print(f"🎉 SUCCESS: {OUTPUT_FILE} created.")
        print("Data mapping used:")
        for k, v in data.items():
            print(f"  {k} -> {v}")
            
    except PermissionError:
        print(f"❌ ERROR: Please close '{OUTPUT_FILE}' in Word and try again.")

if __name__ == "__main__":
    main()