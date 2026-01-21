import os
import glob
import vdf

steam_root = os.path.expanduser("~/.local/share/Steam")
if not os.path.exists(steam_root):
    steam_root = os.path.expanduser("~/.steam/steam")

userdata_path = os.path.join(steam_root, "userdata")
config_files = glob.glob(os.path.join(userdata_path, "*", "config", "localconfig.vdf"))

print(f"Found {len(config_files)} config files.")

for cf in config_files:
    print(f"Checking: {cf}")
    try:
        with open(cf, 'r', encoding='utf-8') as f:
            data = vdf.load(f)
        
        # Check structure
        store = data.get('UserLocalConfigStore', {})
        if not store:
            print("  [WARN] UserLocalConfigStore not found")
            continue
            
        params = [
            'Software', 'Valve', 'Steam', 'apps'
        ]
        
        curr = store
        path_str = "UserLocalConfigStore"
        
        found_apps = False
        
        for p in params:
            if p in curr:
                print(f"  [OK] Found key '{p}' in {path_str}")
                curr = curr[p]
                path_str += f".{p}"
            else:
                print(f"  [FAIL] Key '{p}' NOT found in {path_str}")
                print(f"  Available keys: {list(curr.keys())}")
                break
        else:
            # Reached apps
            print(f"  [OK] Successfully reached 'apps'")
            print(f"  First 5 AppIDs found: {list(curr.keys())[:5]}")
            
            # Check launch options for first few
            for appid, info in list(curr.items())[:5]:
                print(f"    AppID: {appid} (Type: {type(appid)})")
                if isinstance(info, dict):
                    opts = info.get('LaunchOptions', 'N/A')
                    print(f"      LaunchOptions: {opts}")
                else:
                    print(f"      Data: {info}")

    except Exception as e:
        print(f"Error: {e}")
