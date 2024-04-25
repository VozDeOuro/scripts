import requests
import json
import argparse

api_url = "https://xxxx.xxxxx.com.br"
api_key = "xxxxxxxxxxxxxx=" 

green_color = "\033[32m"
red_color = "\033[31m"
reset_color = "\033[0m"
yellow_color='\033[93m'

def get_users():
 # Replace with your actual API key

    # Fetch user IDs
    headers = {"X-Api-Key": api_key}
    response = requests.get(api_url + "/api/v1/user?take=50&skip=0&sort=created", headers=headers)

    try:
        response_data = json.loads(response.content.decode('utf-8'))
        if 'results' in response_data:
            users_limit = response_data['results']
            excluded_user_ids = {1,15}
            users_limit = [user for user in users_limit if user.get("id") not in excluded_user_ids]
            # Extract and print user details
            return users_limit
            for user in users_limit:
                plexUsername = user.get("plexUsername", "N/A")
                email = user.get("email", "N/A")
                movieQuotaLimit = user.get("movieQuotaLimit", "N/A")
                movieQuotaDays = user.get("movieQuotaDays", "N/A")
                tvQuotaLimit = user.get("tvQuotaLimit", "N/A")
                tvQuotaDays = user.get("tvQuotaDays", "N/A")
                plexId = user.get("plexId", "N/A")
                overId = user.get("id", "N/A")
                #print(f"plexUsername: {plexUsername}, Email: {email}, plexId: {plexId}, movieQuotaLimit: {movieQuotaLimit}, movieQuotaDays: {movieQuotaDays}, tvQuotaLimit: {tvQuotaLimit}, tvQuotaDays: {tvQuotaDays}")
                print(f"plexUsername: {plexUsername}, ID: {overId}, movieQuotaLimit: {movieQuotaLimit}, movieQuotaDays: {movieQuotaDays}, tvQuotaLimit: {tvQuotaLimit}, tvQuotaDays: {tvQuotaDays}")
            


    except (ValueError, KeyError) as e:
        print(f"Error: {e}")
        print("Response text:", response.text)


def get_new_quota_limit(prompt):
    try:
        value = input(prompt)
        return int(value) if value else None
    except ValueError:
        return None

def new_quota_limit(users_limit, auto_mode=False):
    if auto_mode:
        movie_quota_limit = 4
        movie_quota_days = 7
        tv_quota_limit = 2
        tv_quota_days = 7
        update_or_check = 'u'  # Auto mode runs the update part directly
    else:
        update_or_check = input(f"Do you want to check {green_color}(c){reset_color} or update the config {red_color}(u){reset_color}? ").lower()
        if update_or_check == 'u':
            movie_quota_limit = get_new_quota_limit("Enter new movie Quota Limit: ")
            movie_quota_days = get_new_quota_limit("Enter new movie Quota Days: ")
            tv_quota_limit = get_new_quota_limit("Enter new tv Quota Limit: ")
            tv_quota_days = get_new_quota_limit("Enter new tv Quota Days: ")

    if update_or_check == 'u':
        headers = {"X-Api-Key": api_key}

        for user in users_limit:
            plexUsername = user.get("plexUsername", "N/A")
            plexId = user.get("plexId", "N/A")
            overId = user.get("id", "N/A")
            #print(f"plexUsername: {plexUsername}, ID: {overId}, movieQuotaLimit: {movieQuotaLimit}, movieQuotaDays: {movieQuotaDays}, tvQuotaLimit: {tvQuotaLimit}, tvQuotaDays: {tvQuotaDays}")
            # Update the user settings
            update_url = f"{api_url}/api/v1/user/{overId}/settings/main"
            update_data = {
                "movieQuotaLimit": movie_quota_limit,
                "movieQuotaDays": movie_quota_days,
                "tvQuotaLimit": tv_quota_limit,
                "tvQuotaDays": tv_quota_days,
            }
            update_response = requests.post(update_url, headers=headers, json=update_data)

            # Check and print the results
            if update_response.status_code == 200:
                print(f"{green_color}[+]{reset_color} {overId}:{plexUsername} Quota updated successfully, to {green_color}{movie_quota_limit}{reset_color} Movie in {green_color}{movie_quota_days}{reset_color} and {green_color}{tv_quota_limit}{reset_color} Seasons in {green_color}{tv_quota_days}{reset_color}.")
            else:
                print(f"{red_color}[-]{reset_color} {overId}:{plexUsername} Failed to update quota. Status code: {update_response.status_code}")

    elif update_or_check == 'c':
        print(f"{green_color}Checking configuration...{reset_color}")
        for user in users_limit:
            plexUsername = user.get("plexUsername", "N/A")
            email = user.get("email", "N/A")
            movieQuotaLimit = user.get("movieQuotaLimit", "N/A")
            movieQuotaDays = user.get("movieQuotaDays", "N/A")
            tvQuotaLimit = user.get("tvQuotaLimit", "N/A")
            tvQuotaDays = user.get("tvQuotaDays", "N/A")
            plexId = user.get("plexId", "N/A")
            overId = user.get("id", "N/A")
            #print(f"plexUsername: {plexUsername}, Email: {email}, plexId: {plexId}, movieQuotaLimit: {movieQuotaLimit}, movieQuotaDays: {movieQuotaDays}, tvQuotaLimit: {tvQuotaLimit}, tvQuotaDays: {tvQuotaDays}")
            print(f"{overId}:{plexUsername} Movie Request Limit:{green_color}{movieQuotaLimit}{reset_color} Reset in:{green_color}{movieQuotaDays}{reset_color} Days || TV Request Limit:{green_color}{tvQuotaLimit}{reset_color} Reset in:{green_color}{tvQuotaDays}{reset_color} Days")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", help="Run in auto mode", action="store_true")
    parser.add_argument("--u", help="Update the configuration", action="store_true")
    parser.add_argument("--c", help="Check the configuration", action="store_true")
    args = parser.parse_args()

    users_limit = get_users()
    new_quota_limit(users_limit, args.auto)



