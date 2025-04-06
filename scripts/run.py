import os
import sys
import subprocess
import importlib.util

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

REQUIRED_MODULES = [
    "requests",
    "bs4",
    "playwright"
]

def is_module_installed(module_name):
    return importlib.util.find_spec(module_name) is not None

def install_module(module_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

def ensure_dependencies():
    missing = [m for m in REQUIRED_MODULES if not is_module_installed(m)]
    if missing:
        print(f"Følgende moduler mangler: {', '.join(missing)}")
        confirm = input("Vil du installere dem nu? (y/n): ").strip().lower()
        if confirm in ["y", "yes"]:
            for m in missing:
                install_module(m)
        else:
            print("Afslutter. Manglende moduler.")
            sys.exit(1)

    # Installer Playwright-browsere (en gang)
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])


def list_projects():
    return [name for name in os.listdir(ROOT_DIR)
            if os.path.isdir(os.path.join(ROOT_DIR, name)) and not name.startswith(".") and name != "scripts"]

def prompt_user(msg, valid_choices=None):
    while True:
        answer = input(msg).strip().lower()
        if not valid_choices or answer in valid_choices:
            return answer
        print(f"Ugyldigt valg. Muligheder: {', '.join(valid_choices)}")

def create_new_project():
    project_name = input("Indtast navn på det nye projekt (brug kun bogstaver, tal og - eller _): ").strip()
    project_path = os.path.join(ROOT_DIR, project_name)
    if os.path.exists(project_path):
        print("Projekt findes allerede. Afslutter.")
        sys.exit(1)
    os.makedirs(project_path)
    print(f"Oprettet projektmappe: {project_path}")
    return project_path

def select_existing_project(projects):
    print("Eksisterende projekter:")
    for i, name in enumerate(projects):
        print(f"{i + 1}: {name}")
    while True:
        try:
            choice = int(input("Vælg et projekt ved at skrive tallet: "))
            if 1 <= choice <= len(projects):
                return os.path.join(ROOT_DIR, projects[choice - 1])
        except ValueError:
            pass
        print("Ugyldigt valg. Prøv igen.")

def main():
    print("=== Screenshotværktøj ===")
    ensure_dependencies()

    choice = prompt_user("Vil du oprette et (n)yt projekt eller bruge et (e)ksisterende? ", ["n", "e"])

    if choice == "n":
        project_path = create_new_project()
    else:
        projects = list_projects()
        if not projects:
            print("Ingen eksisterende projekter fundet.")
            sys.exit(1)
        project_path = select_existing_project(projects)

    os.chdir(project_path)

    print("Vælg screenshot-type:")
    print("1: before")
    print("2: after")

    while True:
        mode_choice = input("Indtast valg (1 eller 2): ").strip()
        if mode_choice == "1":
            mode = "before"
            break
        elif mode_choice == "2":
            mode = "after"
            break
        else:
            print("Ugyldigt valg. Prøv igen.")

    start_url = input("Indtast URL'en der skal crawles (inkl. https://): ").strip()

    if not start_url.startswith("http://") and not start_url.startswith("https://"):
        print("Ugyldig URL. Husk at inkludere http:// eller https://")
        sys.exit(1)

    subprocess.check_call([sys.executable, os.path.join(SCRIPT_DIR, "crawl.py"), start_url, mode])
    subprocess.check_call([sys.executable, os.path.join(SCRIPT_DIR, "screenshot.py"), mode])

if __name__ == "__main__":
    main()
