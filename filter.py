# this fells just reads my sites db and appends em to blocked sites
import json

with open("porn_sites.json", "r") as db_file:
    porn_sites = json.load(db_file)

with open("fokus_settings.json", "r") as fokus_file:
    fokus_settings = json.load(fokus_file)

blocked_sites = set(fokus_settings.get("blocked_sites", []))

for entry in porn_sites:
    domain = entry.get("domain")
    if domain:
        blocked_sites.add(domain.strip().lower())

fokus_settings["blocked_sites"] = sorted(blocked_sites)

with open("fokus_settings.json", "w") as fokus_file:
    json.dump(fokus_settings, fokus_file, indent=2)

print("updated :333")
