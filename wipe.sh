#!/bin/bash

BEARED_TOKEN=TOKEN
#EDIT WEBSITE AND ID
WEBSITE_API="https://WEBSITE.com.br/api/client/servers/ID/startup/variable"


fn_edit_name_server() {

datewipe=$(date +%d/%m)

curl "$WEBSITE_API" \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $BEARED_TOKEN" \
  -X PUT \
  -d '{
    "key": "HOSTNAME",
    "value": "[LATAM] RUSTINITY Vanilla | '$wipetype' '$datewipe'"
  }'

echo "${GREEN} name edited"

}

fn_map_wipe_warning() {
	echo -e "Map wipe will ${RED}reset the map data ${WHITE}and ${GREEN}keep blueprint ${WHITE}data"
	totalseconds=7
	for seconds in {7..1}; do
		echo -e "Map wipe will ${RED}reset the map data ${WHITE}and ${GREEN}KEEPING blueprint ${WHITE}data: ${totalseconds}"
		totalseconds=$((totalseconds - 1))
		sleep 1
		if [ "${seconds}" == "0" ]; then
			break
		fi
	done
}

fn_full_wipe_warning() {
	echo -e  "Server wipe will ${RED}reset the map data ${WHITE}and ${RED}remove blueprint data ${WHITE}"
	totalseconds=7
	for seconds in {7..1}; do
		echo -e  "Server wipe will ${RED}reset the map data ${WHITE}and ${RED}REMOVING blueprint data: ${totalseconds}${WHITE}"
		totalseconds=$((totalseconds - 1))
		sleep 1
		if [ "${seconds}" == "0" ]; then
			break
		fi
	done
}

wipe_files() {
fn_full_wipe_warning
    if [ -n "$(find "${serveridentitydir}" -type f -name "*.map")" ]; then
        echo "Starting countdown to remove .MAP file(s)..."
        for i in {3..1}
        do
            echo -e "$i s to remove .MAP file(s)..."
            sleep 1
        done
        echo -e "${RED}removing .map file(s)...${WHITE}"
        find "${serveridentitydir}" -type f -name "*.map" -printf "%f\n" >> "${logfile}"
    	find "${serveridentitydir}" -type f -name "*.map" -delete | tee -a "${logfile}"
        echo -e "${GREEN}.map file(s) Removed${WHITE}"
        fn_wipe_random_seed
        fn_edit_name_server
        echo -e "${YELLOW}Prepering to Remove .sav${WHITE}"

    else
    	echo -e "${PURPLE}no .map file(s) to remove${WHITE}"
    fi
    if [ -n "$(find "${serveridentitydir}" -type f -name "*.sav*")" ]; then
        echo "Starting countdown to remove .SAV file(s)..."
        for i in {3..1}
        do
            echo -e "$i s to remove .SAV file(s)..."
            sleep 1
        done
        echo -e "${RED}removing .SAV file(s)...${WHITE}"
        find "${serveridentitydir}" -type f -name "*.sav*" -printf "%f\n" >> "${logfile}"
		find "${serveridentitydir}" -type f -name "*.sav*" -delete
        echo -e "${GREEN}.SAV file(s) Removed${WHITE}"
        echo -e "${YELLOW}Prepering to Remove .DB${WHITE}"
    else
		echo -e "${PURPLE}no .sav file(s) to remove${WHITE}"
	fi
	if [ -n "$(find "${serveridentitydir}" -type f ! -name 'player.tokens.db' -name "*.db")" ]; then
		echo -en "${RED}removing .db file(s)...${WHITE}"
        for i in {3..1}
        do
            echo -e "$i s to remove ${RED}.db ${WHITE}file(s)..."
            sleep 1
        done
		find "${serveridentitydir:?}" -type f ! -name 'player.tokens.db' -name "*.db" -printf "%f\n" >> "${logfile}"
		find "${serveridentitydir:?}" -type f ! -name 'player.tokens.db' -name "*.db" -delete
        echo -e "${GREEN}.DB file(s) Removed${WHITE}"
	else
		echo -e "${PURPLE}no .db file(s) to remove${WHITE}"
	fi


}

wipe_map() {

fn_map_wipe_warning

    if [ -n "$(find "${serveridentitydir}" -type f -name "*.map")" ]; then
        echo "Starting countdown to remove .MAP file(s)..."
        for i in {3..1}
        do
            echo -e "$i s to remove .MAP file(s)..."
            sleep 1
        done
        echo -e "${RED}removing .map file(s)...${WHITE}"
        find "${serveridentitydir}" -type f -name "*.map" -printf "%f\n" >> "${logfile}"
    	find "${serveridentitydir}" -type f -name "*.map" -delete | tee -a "${logfile}"
        echo -e "${GREEN}.map file(s) Removed${WHITE}"
        fn_wipe_random_seed
        fn_edit_name_server
        echo -e "${YELLOW}Prepering to Remove .sav${WHITE}"

    else
    	echo -e "${PURPLE}no .map file(s) to remove${WHITE}"
    fi
    if [ -n "$(find "${serveridentitydir}" -type f -name "*.sav*")" ]; then
        echo "Starting countdown to remove .SAV file(s)..."
        for i in {3..1}
        do
            echo -e "$i s to remove .SAV file(s)..."
            sleep 1
        done
        echo -e "${RED}removing .SAV file(s)...${WHITE}"
        find "${serveridentitydir}" -type f -name "*.sav*" -printf "%f\n" >> "${logfile}"
		find "${serveridentitydir}" -type f -name "*.sav*" -delete
    else
		echo -e "${PURPLE}no .sav file(s) to remove${WHITE}"
	fi
datewipe=$(date +%d/%m)

}

fn_wipe_random_seed() {
    seedfile=server/rust/cfg/serverauto.cfg
	seed=$(shuf -i 1-2147483647 -n 1)
	echo -e "generating new random seed (${CYAN}${seed})..."
    sed -i -e '/server.seed/d' $seedfile
    echo "server.seed $seed" >> $seedfile
}


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'

serveridentitydir="./server/rust/"
logfile="wipelog.txt"

if [ "$1" == "full" ]; then
    wipetype=FULLWIPE
    wipe_files
else
    if [ "$1" == "map" ]; then
        wipetype=WIPE
        wipe_map
    else
        if [ "$1" == "seed" ]; then
            fn_wipe_random_seed
        else
            echo "nothing wipped"
            echo "commands: full, map, map"
        fi
    fi
fi
