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
    print(f"--- Processing Issue: {ISSUE_ID} ---")
    try:
        response = requests.get(f"{BASE_URL}/issues/{ISSUE_ID}", headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return None
        
        issue = response.json()
        summary = issue.get("summary", "")

        # Split Summary (1=Client, 2=Project, 3=Subsystem)
        parts = [p.strip() for p in summary.split("-")]
        
        # --- STATIC CHRONOLOGY LABELS (image_6b2458.png) ---
        # These are displayed exactly as in your source screenshot
        static_chronology = [
            "DATE – DUREE – MISE EN SERVICE SUR SITE",
            "DATE – DUREE – MISE EN SERVICE A DISTANCE",
            "DATE - DUREE – ASSISTANCE / RESOLUTION / ESSAIS",
            "DATE - DUREE – DOCUMENTATION - ECHANGES",
            "DATE - DUREE – RDV NON HONORE : MOBILISATION"
        ]

        # Checklist items for 'Opérations réalisées'
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
            "Total_Spent": "0h",
            "static_chrono": static_chronology, # For the Chronology section
            "energy_tasks": installation_tasks  # For the checklist section
        }

        # Extract Sidebar Custom Fields
        for field in issue.get("customFields", []):
            name = field.get("name")
            val = field.get("value")
            if not val: continue

            if name == "Project Number":
                context["ProjectNumero"] = val.get("name", str(val)) if isinstance(val, dict) else str(val)
            elif name == "Order No":
                context["OrderNo"] = str(val)
            elif name == "Customer pA":
                context["CustomerPA"] = str(val)
            elif name == "Assignee":
                context["Assignee"] = val.get("fullName", "")
            elif name == "Spent time":
                spent_val = val.get("presentation", "0h") if isinstance(val, dict) else str(val)
                context["Spent_time"] = spent_val
                context["Total_Spent"] = spent_val 

        return context

    except Exception as e:
        print(f"❌ Script Error: {e}")
        return None

def main():
    data = get_issue_data()
    if not data: return

    template_file = "template.docx"
    output_file = f"Rapport_{ISSUE_ID}.docx"

    try:
        doc = DocxTemplate(template_file)
        doc.render(data)
        doc.save(output_file)
        print(f"🎉 SUCCESS: {output_file} generated with static Chronology rows.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()