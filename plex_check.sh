#!/bin/bash

#PLEX CONFIG 
container_name=plex
plex_url_local="http://10.10.10.10:32400"
plex_url_remote="https://xxxxxxxxx"
plex_token="xxxxxxxxxxxxxxx"
movie_check="Harry%20Potter%20and%20the%20Sorcerer%27s%20Stone"
attempts=3
sleep_time=20 #sleep in seconds
countdown_timer_set=15 #sleep in minutes
#TELEGRAM CONFIG

TELEGRAM_GROUP_ID=xxxxxxxxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=xxxxxxxxxxxxxxxxxx



##############################################################################################################################
#DO NOT CHANGE ANYTHING BELOW THIS POINT#
##############################################################################################################################

OUTAGE_DATEmonth=$(date +%m )
OUTAGE_DATEd=$(date +%d )
OUTAGE_DATEh=$(date +%H )
OUTAGE_DATEmin=$(date +%M )

TELEGRAM_MESSAGE="🪫 🔌 PLEX OUTAGE Detected at:"$'\n'$'\n'"day:  $OUTAGE_DATEd"$'\n'"Month:  $OUTAGE_DATEmonth"$'\n'"hour:  $OUTAGE_DATEh:$OUTAGE_DATEmin "$'\n'"CHECK Manualy What happen "$'\n'"IPS Checked: "$'\n'"$plex_url_local "$'\n'"$plex_url_remote "

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



fn_check_plex (){
    curl_local=$(curl -s -X GET "$plex_url_local/hubs/search/?X-Plex-Token=$plex_token&query=$movie_check&limit=1")
    curl_remote=$(curl -s -X GET "$plex_url_remote/hubs/search/?X-Plex-Token=$plex_token&query=$movie_check&limit=1")
}

fn_telegram_msg (){
    echo -e "Sending Telegram Notification"
    curl -s --data "text=$TELEGRAM_MESSAGE" --data "chat_id=$TELEGRAM_GROUP_ID" 'https://api.telegram.org/bot'$TELEGRAM_BOT_TOKEN'/sendMessage'
}

print_countdown() {
    local remaining_minutes=$1
    echo "Next check in $remaining_minutes minutes."
}

fn_countdown(){
    countdown_timer="$countdown_timer_set"
    while [ $countdown_timer -gt 0 ]; do
    if [ $((countdown_timer % 2)) -eq 0 ]; then
        print_countdown $countdown_timer
    fi
        sleep 60
        ((countdown_timer -= 1))
    done
        fn_run_check
}

fn_run_check (){
internet=false

while [ "$internet" != true ]; do
    if ping -c 3 1.1.1.1 &> /dev/null; then
        echo "Internet is available."
        internet=true
    else
        echo "No internet connection. Retrying in 20 seconds..."
        sleep 20
    fi
done

    success=false
        for ((i=1; i<=attempts; i++)); do
            echo "Attempt $i"
            fn_check_plex
            if echo "$curl_local" | grep -q 'type="movie"' && echo "$curl_remote" | grep -q 'type="movie"'; then
                success=true
                break
            fi
            sleep $sleep_time
        done

        if [ "$success" = true ]; then
            echo -e "PLEX SEEMS TO BE ${GREEN}UP${WHITE}"
            echo -e "Sleeping for "$countdown_timer_set"m and checking again"
            fn_countdown
        else
            echo -e "PLEX SEEMS TO BE ${RED}DOWN${WHITE}"
            echo -e "RESTARTING Container and Checking again"
            docker restart $container_name
            sleep 60
            for ((i=1; i<=attempts; i++)); do
                echo "Attempt $i"
                if [ "$success" = true ]; then
                    break
                fi
                sleep $sleep_time
            done
            if [ "$success" = true ]; then
                echo -e "PLEX IS BACK ${GREEN}UP${WHITE}"
                echo -e "Sleeping for "$countdown_timer_set"m and checking again"
                fn_countdown
            else
                echo -e "No movie found after $attempts attempts. Exiting."
                fn_telegram_msg
                sleep 20
                exit 1
            fi
        fi
}

        
        


scriptname=check_plex

fn_ascii_art
fn_run_check
