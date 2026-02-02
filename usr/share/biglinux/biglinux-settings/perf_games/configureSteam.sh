#!/bin/bash
# Steam GameMode Configuration Script
TEXTDOMAIN=biglinux-settings
export TEXTDOMAIN

# Detect Steam paths on demand
detect_config() {
    for p in "$HOME/.steam/steam" "$HOME/.local/share/Steam" "$HOME/.steam/debian-installation"; do
        [ -f "$p/config/config.vdf" ] && steam_path="$p" && break
    done
    [ -z "$steam_path" ] && echo "error: Steam path not found." && exit 0
    
    # Sort by modification time to get the latest active config
    local_config=$(find "$steam_path/userdata" -maxdepth 3 -name "localconfig.vdf" -printf "%T@ %p\n" | sort -n | tail -n 1 | cut -d' ' -f2-)
}

# Exclusions
exclude_ids=("228980" "1070560" "1391110" "1628350" "1493710" "2180100" "961940" "1054830" "1113280" "1245040" "1420170" "1580130" "1887720" "2348590" "2805730" "250820" "1826330")
exclude_keywords=("proton" "steam linux runtime" "steamworks" "redistributable" "redist" "directx" "vcredist" "visual c++" "physx" "openal" ".net" "easyanticheat" "battleye" "steam client" "steamvr" "steam controller" "dedicated server" "sdk" "soldier" "sniper" "scout" "pressure-vessel")

is_excluded() {
    local id=$1 name="${2,,}"
    for ex in "${exclude_ids[@]}"; do [ "$id" == "$ex" ] && return 0; done
    for kw in "${exclude_keywords[@]}"; do [[ "$name" == *"$kw"* ]] && return 0; done
    return 1
}

action="$1"
args="${@:2}"

list_games() {
    detect_config
    [ ! -f "$local_config" ] && echo "error: Local config not found." && exit 0

    # Find IDs with gamemoderun AND %command% in LaunchOptions using robust VDF parsing
    enabled_games=$(awk '
        BEGIN { depth=0; id=""; app_d=0; pending="" }
        {
            line=$0; 
            clean_line = line;
            gsub(/\\"/, "", clean_line);
            gsub(/"[^"]*"/, "", clean_line);
            nopen = gsub(/{/, "{", clean_line); nclose = gsub(/}/, "}", clean_line);
            
            if (app_d == 0) {
                if (match(line, /^[[:space:]]*"[0-9]+"[[:space:]]*$/)) {
                    match(line, /[0-9]+/); pending=substr(line, RSTART, RLENGTH);
                } else if (match(line, /^[[:space:]]*"[0-9]+"[[:space:]]*\{/)) {
                    match(line, /[0-9]+/); id=substr(line, RSTART, RLENGTH); app_d=depth+1; pending=""
                } else if (match(line, /^[[:space:]]*\{/) && pending != "") {
                    id=pending; app_d=depth+1; pending=""
                } else if (match(line, /^[[:space:]]*"[^"]+"/) && pending != "") {
                     pending=""
                }
            }
            if (id != "" && depth >= app_d) {
                lc = tolower(line);
                if (lc ~ /"launchoptions"/ && lc ~ /%command%/) {
                    if (lc ~ /(^|[^a-z0-9_])gamemoderun([^a-z0-9_]|$)/) print id
                }
            }
            depth += nopen; depth -= nclose;
            if (app_d > 0 && depth < app_d) { id=""; app_d=0; pending="" }
        }
    ' "$local_config")
    enabled_str=" $(echo "$enabled_games" | tr '\n' ' ') "

    for manifest in "$steam_path"/steamapps/appmanifest_*.acf; do
        [ -f "$manifest" ] || continue
        appid=$(awk -F'"' '/"appid"/ {print $4; exit}' "$manifest")
        name=$(awk -F'"' '/"name"/ {print $4; exit}' "$manifest")
        [ -z "$appid" ] || [ -z "$name" ] && continue
        is_excluded "$appid" "$name" && continue
        
        has_gm="false"
        [[ "$enabled_str" == *" $appid "* ]] && has_gm="true"
        echo "$appid|$has_gm|$name"
    done
}

apply_changes() {
    detect_config
    [ ! -f "$local_config" ] && echo "error: Local config not found." && exit 0
    cp "$local_config" "$local_config.backup"
    
    tmp_file=$(mktemp)
    awk -v enabled=" $args " '
    BEGIN { depth=0; id=""; app_d=0; found=0; pending="" }
    {
        line=$0; out=1; temp=line; gsub(/"[^"]*"/,"",temp)
        nopen=gsub(/{/,"{",temp); nclose=gsub(/}/,"}",temp)
        
        if (match(line, /^[[:space:]]*"[0-9]+"[[:space:]]*$/)) {
            gsub(/[^0-9]/,"",line); pending=line; line=$0
        } else if (match(line, /^[[:space:]]*"[0-9]+"[[:space:]]*\{/)) {
            str=line; gsub(/[^0-9]/,"",str); id=str; app_d=depth+1; found=0; pending=""
        } else if (match(line, /^[[:space:]]*\{[[:space:]]*$/) && pending) {
            id=pending; app_d=depth+1; found=0; pending=""
        }
        if (id && depth>=app_d && match(line, /"[Ll]aunch[Oo]ptions"/)) {
            found=1; is_on=(index(enabled," "id" ")>0)
            if (match(line, /"[Ll]aunch[Oo]ptions"[[:space:]]*"[^"]*"/)) {
                match(line, /^.*"[Ll]aunch[Oo]ptions"[[:space:]]*/); pre=substr(line,1,RLENGTH); rest=substr(line,RLENGTH+1)
                if (match(rest, /^"[^"]*"/)) {
                    val=substr(rest,2,RLENGTH-2)
                    gsub(/(^| )gamemoderun( |$)/, " ", val); gsub(/[[:space:]]+/, " ", val); gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
                    if (is_on) {
                        if (val ~ /%command%/) sub(/%command%/, "gamemoderun %command%", val)
                        else val = (val=="" ? "gamemoderun %command%" : val " gamemoderun %command%")
                    }
                    gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
                    print pre"\""val"\""; out=0
                }
            }
        }
        depth+=nopen
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
        depth-=nclose; if (out) print $0
    }' "$local_config" > "$tmp_file"
    
    mv "$tmp_file" "$local_config"
    echo "Success"
}

close_steam() { pkill -9 steam; pkill -9 steamwebhelper; echo "done"; }
check_steam() { pgrep -x steam >/dev/null && echo "running" || echo "stopped"; }

case "$action" in
    list) list_games ;;
    apply) apply_changes ;;
    close_steam) close_steam ;;
    check_steam) check_steam ;;
    *) echo "Usage: $0 {list|apply|close_steam|check_steam}"; exit 1 ;;
esac
