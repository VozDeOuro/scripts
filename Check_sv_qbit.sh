#!/bin/bash

COUNTDOWN_TIMER_SET=30 #in Minutes

#PTERODACTYL CONFIG
PTERO_URL="https://panel.foo.com"
PTERO_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxx"
PTERO_SERVER_ID="8d105c03"
#QBITTORRENT CONFIG
QBIT_URL="http://10.10.10.10:8080"
QBIT_USER="xxxxx"
QBIT_PASS="xxxxxxxxxxxxxxx"
#STEAM CONFIG
STEAM_API_KEY="xxxxxxxxxxxxxxxxx"
STEAM_ID="xxxxxxxxxxxxxxxxxx"

GAME_LIST=(252490 730)
#252490 = RUST
#730 = CS2 and CS:GO


##############################################################################################################################
#DO NOT CHANGE ANYTHING BELOW THIS POINT#
##############################################################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
# to use color ${RED}

fn_ascii_art (){
    echo -e "${PURPLE}╦  ╔═╗╔═╗╦  ╦  ╔═╗╔═╗╦═╗╦╔═╗╔╦╗╔═╗"
    echo -e "${PURPLE}║  ║  ╚═╗╚╗╔╝  ╚═╗║  ╠╦╝║╠═╝ ║ ╚═╗"
    echo -e "${PURPLE}╩═╝╚═╝╚═╝ ╚╝   ╚═╝╚═╝╩╚═╩╩   ╩ ╚═╝${WHITE}"
    echo -e ""
    echo -e "${scriptname}"
    printf -- '-%.0s' {1..15}
    printf -- ' %.0s\n' 1 2

}


get_cookie(){
	#echo "Geting New Cookie"
	qbitcookie=$(curl -s -i --header "Referer: $QBIT_URL" --data "username=$QBIT_USER&password=$QBIT_PASS" $QBIT_URL/api/v2/auth/login | grep 'set-cookie' | awk -F ':' '{print $2}' | awk -F ';' '{print $1}')
}

start_limit_qbit(){
	#echo "Starting server with torrent limit"
    islimiton=$(curl -s $QBIT_URL/api/v2/transfer/speedLimitsMode --cookie "$qbitcookie")
	if test "$islimiton" -eq 0; then
		curl -X POST $QBIT_URL/api/v2/transfer/toggleSpeedLimitsMode --cookie "$qbitcookie" > /dev/null 2>&1
		echo "limit is now ON (1)"
	else
		echo "limit is already ON (1)"
	fi
}

stop_limit_qbit(){
	#echo "Stoping server and restoring torrent limit"
    islimiton=$(curl -s $QBIT_URL/api/v2/transfer/speedLimitsMode --cookie "$qbitcookie")
	if test "$islimiton" -eq 1; then
		curl -s -X POST $QBIT_URL/api/v2/transfer/toggleSpeedLimitsMode --cookie "$qbitcookie" > /dev/null 2>&1
		echo "limit is now OFF (0)"
	else
		echo "limit is already OFF (0)"
	fi
}

check_server_on(){
    
    ISONLINECURL=$(curl -s "$PTERO_URL/api/client/servers/$PTERO_SERVER_ID/resources" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $PTERO_API_KEY" \
    -X GET | grep current_state)
    ISONLINE=$(echo "$ISONLINECURL" | awk -F '"' '{print$10}')
    #echo "$ISONLINE"

}

print_countdown() {
    local remaining_minutes=$1
    echo "Next check in $remaining_minutes minutes."
}


check_playing_status(){
    STEAM_CURL=$(curl -s -X GET "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=$STEAM_API_KEY&steamids=$STEAM_ID&format=json")
    STEAM_USER=$(echo "$STEAM_CURL" | jq -r '.response.players[0].personaname')
    GAME_ID=$(echo "$STEAM_CURL" | jq -r '.response.players[0].gameid // "NOT_PLAYING"')
    GAME_NAME=$(echo "$STEAM_CURL" | jq -r '.response.players[0].gameextrainfo // "NOT_PLAYING"')
    if [ "$GAME_ID" = "NOT_PLAYING" ]; then
        return 1
    else
        for GAME in "${GAME_LIST[@]}"; do
            if [ "$GAME" -eq "$GAME_ID" ]; then
                echo "$STEAM_USER is playing $GAME_NAME"
                break
            fi
        done
    fi
}



check_and_sleep(){

    get_cookie
    check_server_on
    check_playing_status

    if [ "$ISONLINE" = "offline" ] && [ "$GAME_NAME" = "NOT_PLAYING" ]; then
        echo "server is offline and $STEAM_USER is not playing or game is not on list"
        echo "checking torrent ..."
        stop_limit_qbit
        countdown_timer=$COUNTDOWN_TIMER_SET
        
        while [ $countdown_timer -gt 0 ]; do
            if [ $((countdown_timer % 10)) -eq 0 ]; then
                print_countdown $countdown_timer
            fi
            sleep 60
            ((countdown_timer -= 1))
        done
        check_and_sleep
    elif [ "$ISONLINE" = "offline" ] || [ "$GAME_NAME" != "NOT_PLAYING" ]; then
        echo "server is $ISONLINE but $STEAM_USER is playing $GAME_NAME sleeping for 500s and checking again"
        start_limit_qbit
        sleep 500
        check_and_sleep
    else
        echo "server is $ISONLINE and $STEAM_USER is not playing anything so sleeping for 500s and checking again"
        start_limit_qbit
        sleep 500
        check_and_sleep
    fi 
}

scriptname=start_qbitlimit

fn_ascii_art
check_and_sleep