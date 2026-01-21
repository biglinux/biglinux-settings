import os
import glob
import vdf

def recursive_search(d, path=""):
    if isinstance(d, dict):
        for k, v in d.items():
            recursive_search(v, path + "." + str(k))
    elif isinstance(d, str):
        if "gamemode" in d.lower():
            print(f"FOUND MATCH at {path}: {d}")

steam_root = os.path.expanduser("~/.local/share/Steam")
if not os.path.exists(steam_root):
    steam_root = os.path.expanduser("~/.steam/steam")

userdata_path = os.path.join(steam_root, "userdata")
config_files = glob.glob(os.path.join(userdata_path, "*", "config", "localconfig.vdf"))

for cf in config_files:
    print(f"Scanning: {cf}")
    try:
        with open(cf, 'r', encoding='utf-8') as f:
            data = vdf.load(f)
        recursive_search(data)
    except Exception as e:
        print(f"Error: {e}")
