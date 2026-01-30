#!/bin/bash
# Steam GameMode Configuration Script

TEXTDOMAIN=biglinux-settings
export TEXTDOMAIN

error_json() { echo "{\"error\": \"$1\"}"; exit 0; }

# Detect Steam paths
get_steam_path() {
    for p in "$HOME/.steam/steam" "$HOME/.local/share/Steam" "$HOME/.steam/debian-installation"; do
        [ -f "$p/config/config.vdf" ] && echo "$p" && return
    done
}

STEAM_PATH=$(get_steam_path)
[ -z "$STEAM_PATH" ] && error_json "Steam path not found."

LOCAL_CONFIG=$(find "$STEAM_PATH/userdata" -maxdepth 3 -name "localconfig.vdf" 2>/dev/null | head -1)

# Exclusions
EXCLUDE_IDS=("228980" "1070560" "1391110" "1628350" "1493710" "2180100" "961940" "1054830" "1113280" "1245040" "1420170" "1580130" "1887720" "2348590" "2805730" "250820" "1826330")
EXCLUDE_KEYWORDS=("proton" "steam linux runtime" "steamworks" "redistributable" "redist" "directx" "vcredist" "visual c++" "physx" "openal" ".net" "easyanticheat" "battleye" "steam client" "steamvr" "steam controller" "dedicated server" "sdk" "soldier" "sniper" "scout" "pressure-vessel")

is_excluded() {
    local id=$1 name="${2,,}"
    for ex in "${EXCLUDE_IDS[@]}"; do [ "$id" == "$ex" ] && return 0; done
    for kw in "${EXCLUDE_KEYWORDS[@]}"; do [[ "$name" == *"$kw"* ]] && return 0; done
    return 1
}

json_escape() { echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

ACTION="$1"
ARGS="${@:2}"

list_games() {
    [ ! -f "$LOCAL_CONFIG" ] && error_json "Local config not found."

    # Find IDs with gamemoderun in LaunchOptions
    ENABLED=$(awk '
        /^[[:space:]]*"[0-9]+"/ { match($0, /[0-9]+/); id = substr($0, RSTART, RLENGTH) }
        tolower($0) ~ /launchoptions/ && tolower($0) ~ /gamemoderun/ { if (id) print id }
    ' "$LOCAL_CONFIG")
    ENABLED_STR=" $(echo "$ENABLED" | tr '\n' ' ') "

    echo "["
    first=1
    for manifest in "$STEAM_PATH"/steamapps/appmanifest_*.acf; do
        [ -f "$manifest" ] || continue
        appid=$(awk -F'"' '/"appid"/ {print $4; exit}' "$manifest")
        name=$(awk -F'"' '/"name"/ {print $4; exit}' "$manifest")
        [ -z "$appid" ] || [ -z "$name" ] && continue
        is_excluded "$appid" "$name" && continue
        
        has_gm="false"
        [[ "$ENABLED_STR" == *" $appid "* ]] && has_gm="true"
        
        [ $first -eq 0 ] && echo ","
        echo "{\"app_id\": \"$appid\", \"name\": \"$(json_escape "$name")\", \"has_gamemode\": $has_gm}"
        first=0
    done
    echo "]"
}

apply_changes() {
    [ ! -f "$LOCAL_CONFIG" ] && error_json "Local config not found."
    cp "$LOCAL_CONFIG" "$LOCAL_CONFIG.backup"
    
    TMP=$(mktemp)
    awk -v enabled=" $ARGS " '
    BEGIN { depth=0; id=""; app_d=0; found=0; pending="" }
    {
        line=$0; out=1
        temp=line; gsub(/"[^"]*"/,"",temp)
        nopen=gsub(/{/,"{",temp); nclose=gsub(/}/,"}",temp)
        
        # Detect app ID
        if (match(line, /^[[:space:]]*"[0-9]+"[[:space:]]*$/)) {
            gsub(/[^0-9]/,"",line); pending=line; line=$0
        } else if (match(line, /^[[:space:]]*"[0-9]+"[[:space:]]*\{/)) {
            str=line; gsub(/[^0-9]/,"",str); id=str; app_d=depth+1; found=0; pending=""
        } else if (match(line, /^[[:space:]]*\{[[:space:]]*$/) && pending) {
            id=pending; app_d=depth+1; found=0; pending=""
        }
        
        # Process LaunchOptions
        if (id && depth>=app_d && match(line, /"[Ll]aunch[Oo]ptions"/)) {
            found=1
            is_on=(index(enabled," "id" ")>0)
            if (match(line, /"[Ll]aunch[Oo]ptions"[[:space:]]*"[^"]*"/)) {
                match(line, /^.*"[Ll]aunch[Oo]ptions"[[:space:]]*/)
                pre=substr(line,1,RLENGTH)
                rest=substr(line,RLENGTH+1)
                if (match(rest, /^"[^"]*"/)) {
                    val=substr(rest,2,RLENGTH-2)
                    gsub(/gamemoderun[[:space:]]*%command%[[:space:]]*/,"",val)
                    gsub(/^[[:space:]]+|[[:space:]]+$/,"",val)
                    if (is_on) val = (val?"gamemoderun %command% "val:"gamemoderun %command%")
                    print pre"\""val"\""; out=0
                }
            }
        }
        
        depth+=nopen
        
        # Add LaunchOptions before closing if needed
        if (nclose && id) {
            nd=depth-nclose
            if (nd<app_d) {
                if (index(enabled," "id" ")>0 && !found) {
                    match($0,/^[[:space:]]*/); ind=substr($0,1,RLENGTH)
                    print ind"\t\"LaunchOptions\"\t\t\"gamemoderun %command%\""
                }
                id=""; app_d=0; found=0
            }
        }
        depth-=nclose
        if (out) print $0
    }' "$LOCAL_CONFIG" > "$TMP"
    
    mv "$TMP" "$LOCAL_CONFIG"
    echo "Success"
}

close_steam() { pkill -9 steam; pkill -9 steamwebhelper; echo "done"; }
check_steam() { pgrep -x steam >/dev/null && echo "running" || echo "stopped"; }

case "$ACTION" in
    list) list_games ;;
    apply) apply_changes ;;
    close_steam) close_steam ;;
    check_steam) check_steam ;;
    *) echo "Usage: $0 {list|apply|close_steam|check_steam}"; exit 1 ;;
esac
