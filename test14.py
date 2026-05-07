import requests
from docxtpl import DocxTemplate
import os
import datetime

# --- CONFIGURATION ---
ISSUE_ID = "sysdes-33612"
TOKEN = "perm-ci5oYW1pbGk=.NzctMTM3.2DmnYBuMYzQf04AlOrYtisyZago3Rm"
BASE_URL = "https://youtrack.meteocontrol.de/api"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

params = {
    "fields": "summary,customFields(name,value(name,fullName,presentation,text))"
}

def get_issue_data():
    print(f"--- Fetching Data for {ISSUE_ID} ---")
    try:
        response = requests.get(f"{BASE_URL}/issues/{ISSUE_ID}", headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return None
        
        issue = response.json()
        summary = issue.get("summary", "")

        # Split Summary (1=Client, 2=Project, 3=Subsystem as per image_783750.png)
        parts = [p.strip() for p in summary.split("-")]
        
        # Pre-defined list for 'Opérations réalisées' as requested
        installation_tasks = [
            "Analyse des risques",
            "Etat des lieux de l’installation",
            "Contrôle des composants après transport/ installation",
            "Vérification polarité 230V",
            "Mise en place Fusibles Batterie",
            "Vérification polarité 24VDC",
            "Alimentation des composants"
        ]
        
        context = {
            "Client": parts[0] if len(parts) > 0 else "N/A",
            "Project": parts[1] if len(parts) > 1 else "N/A",
            "Subsystem": parts[2] if len(parts) > 2 else "N/A",
            "ProjectNumero": "N/A",
            "OrderNo": "N/A",
            "CustomerPA": "N/A",
            "subcontractor": "N/A",
            "Assignee": "Non assigné",
            "Spent_time": "0h",
            "work_items": [],
            "energy_tasks": installation_tasks
        }

        # Extract Sidebar Custom Fields
        for field in issue.get("customFields", []):
            name = field.get("name")
            val = field.get("value")

            if not val:
                continue

            if name == "Project Number":
                context["ProjectNumero"] = val.get("name", str(val)) if isinstance(val, dict) else str(val)
            elif name == "Order No":
                context["OrderNo"] = str(val)
            elif name == "Customer pA":
                context["CustomerPA"] = str(val)
            elif name == "Assignee":
                context["Assignee"] = val.get("fullName", "")
            elif name == "Spent time":
                context["Spent_time"] = val.get("presentation", "0h") if isinstance(val, dict) else str(val)
                
                # Chronology fallback for 'Chronologie' table
                context["work_items"].append({
                    "date": datetime.datetime.now().strftime('%d/%m/%Y'),
                    "duration": context["Spent_time"],
                    "type": context["Subsystem"].upper()
                })

        return context

    except Exception as e:
        print(f"❌ Script Error: {e}")
        return None

def main():
    data = get_issue_data()
    if not data:
        return

    output_path = f"Rapport_{ISSUE_ID}.docx"

    if not os.path.exists("template.docx"):
        print("❌ Error: 'template.docx' not found.")
        return

    try:
        doc = DocxTemplate("template.docx")
        doc.render(data)
        doc.save(output_path)
        print(f"🎉 SUCCESS: {output_path} generated.")

    except PermissionError:
        print(f"❌ ERROR: Please close '{output_path}' in Word and run again.")
    except Exception as e:
        print(f"❌ Rendering Error: {e}")

if __name__ == "__main__":
    main()