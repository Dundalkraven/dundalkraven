ISSUE_ID = "SYS-ENR-VGP-Rouen-Commissioning"

def get_issue_data():
    response = requests.get(YOUTRACK_URL, headers=headers, params=params)

    print("Status:", response.status_code)
    issue = response.json()

    nom_assignee = "Non assigné"
    project_num = "N/A"
    client_name = "N/A"

    for field in issue.get("customFields", []):
        name = field.get("name")
        val = field.get("value")

        if name == "Assignee" and val:
            nom_assignee = val.get("fullName", "Non assigné")

        elif name == "Project Number" and val:
            project_num = val.get("name", str(val))

        elif name == "Client" and val:
            client_name = val.get("name", str(val))

    spent_time = issue.get("spentTime", {})
    temps_passe = spent_time.get("presentation", "0h")

    return {
        "p_name": issue.get("summary", "Inconnu"),
        "p_num": project_num,
        "p_client": client_name,
        "p_assignee": nom_assignee,
        "p_spent": temps_passe
    }