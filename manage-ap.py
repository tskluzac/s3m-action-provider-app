
import globus_sdk
import argparse

CLIENT_ID = "3c5d0e04-cba1-4c39-b098-fb8e9c45c3d2"
CLIENT_SECRET = "gGe00fDSoAllEForoFKD5yA0EFf2knFiX0wfcBs98Pc="

app = globus_sdk.ClientApp(
    "manage-ap", client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)

client = globus_sdk.AuthClient(app=app)
client.add_app_scope(globus_sdk.AuthClient.scopes.manage_projects)

parser = argparse.ArgumentParser("manage-ap")
parser.add_argument("action", choices=("show-self", "create-scope"))


def main():
    args = parser.parse_args()
    if args.action == "show-self":
        print(client.get_identities(ids=CLIENT_ID))
    elif args.action == "create-scope":
        # we have looked up the scope for Globus Groups for you in this
        # case -- see note below for details
        groups_scope_spec = globus_sdk.DependentScopeSpec(
            "73320ffe-4cb4-4b25-a0a3-83d53d59ce4f", False, False
        )
        print(
            client.create_scope(
                CLIENT_ID,
                "Action Provider 'all'",
                "Access to my action provider",
                "action_all",
                dependent_scopes=[groups_scope_spec],
            )
        )
    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
