import globus_sdk
import os
from getpass import getpass

def get_globus_access_token(client_id, scope):
    """
    Generates a Globus access token for a specified scope, prompting the user to log in
    if necessary.  Uses the Native App authentication flow.

    Args:
        client_id (str): The Globus application's client ID.
        scope (str): The desired Globus auth scope (e.g., a custom scope).

    Returns:
        str: The access token, or None on error.
    """
    client = globus_sdk.NativeAppAuthClient(client_id)
    client.oauth2_start_flow(requested_scopes=[scope])

    #get the most recent token
    #tokens = client.oauth2_token_response.by_resource_server

    authorize_url = client.oauth2_get_authorize_url()
    print("Please go to this URL and login: {0}".format(authorize_url))

    auth_code = input("Please enter the code you get after login here: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)
    print(token_response)

if __name__ == "__main__":
    # Replace with your Globus application's Client ID and desired scope.
    CLIENT_ID = "fe80e738-57a7-4766-b0a7-219c5fa5f909"  #  Replace with your actual Client ID
    CUSTOM_SCOPE = "https://auth.globus.org/scopes/3c5d0e04-cba1-4c39-b098-fb8e9c45c3d2/action_all"  # Replace with your custom scope

    if CLIENT_ID == "YOUR_GLOBUS_CLIENT_ID" or CUSTOM_SCOPE == "YOUR_CUSTOM_SCOPE":
        print("Error: Please update the script with your Globus Client ID and custom scope.")
        exit(1)

    access_token = get_globus_access_token(CLIENT_ID, CUSTOM_SCOPE)

    if access_token:
        print("\nGenerated Access Token:")
        print(access_token)
        print("\nToken generation successful!")
    else:
        print("\nFailed to generate access token.")
