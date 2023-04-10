## Cloud Foundry MSAL Flask Template
Template for a WSGI Flask app running on Cloud Foundry using a DBaaS and MSAL authentication

### Steps I won't cover here:
  1. Creating your database (your `DB_CONNECTION_STRING` and `DB_NAME` environment variables are up to you to provide)
  2. Creating your Cloud Foundry account
  3. Creating your Active Directory tenant (your tenant may have already been created by your company if you work somewhere using AD)
  4. GitHub runner/action for automatic CF staging (there is an example in `.github/workflows/main.yml`)

## Setup

### Generate a secret
  ```
  > python3
  >>> import secrets
  >>> secrets.token_urlsafe(32)
  ```
  Your `SECRET_KEY` is the output from that last command
  
### Create your registered app
  1. Go to: https://portal.azure.com/
  2. Open the Azure Active Directory service page
  3. Note your "Tenant ID". Your `AZ_AUTHORITY` variable will be `https://login.microsoftonline.com/<Tenant ID>`
  4. Add -> App registration
  5. Completing step 4 took you to the app registration once it was created. If you left that page, find your app here:
    b. Navigate to https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
    c. Select your app
  6. Your `CLIENT_ID` is the item noted "Application (client) ID"
  7. Go to the Certificates & secrets page → Client secrets, and select "New client secret"
  8. Create the secret and copy the "Value" somewhere safe. This is your `CLIENT_SECRET`
  9. Go to the App roles page → Create app role
  10. Create a role with the Value "MyApp.ReadAccess". Make sure "MyApp" is simple (probably just letters). You will need this value when modifying `index.py`
  11. Go to Authentication → Add a platform
  12. Append "get-azure-authentication-token" and "logout" to your app's URI get your authentication path and logout path, e.g. `https://cfmft.my-org/`:
  ```
    https://cfmft.my-org/get-azure-authentication-token
    https://cfmft.my-org/logout
  ```
  13. Hint: you might want to add a localhost authentication path as well for local debug. You can add it to the list *after* you've submitted the previous addition.
  ```
    https://localhost:5000/get-azure-authentication-token
  ```

### Modify index.py
  \# TODO: this should be an ENV variable instead
  In `index.py` change `MyApp.ReadAccess` to `<your MSAL app name>.ReadAccess`
  
### Add a platform in your registered app
  https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
  

### Push the app
  ```
  git clone https://github.com/szofar/cf-msal-flask-template
  cd cf-msal-flask-template
  cf api $CF_API
  cf login
  cf target -o "$CF_ORG" -s "$CF_SPACE"
  cf set-env "$CF_APP_NAME" DB_NAME "$DB_NAME"
  cf set-env "$CF_APP_NAME" DB_CONNECTION_STRING "$DB_CONNECTION_STRING"
  cf set-env "$CF_APP_NAME" AUTHORITY "$AZ_AUTHORITY"
  cf set-env "$CF_APP_NAME" CLIENT_ID "$AZ_CLIENT_ID"
  cf set-env "$CF_APP_NAME" CLIENT_SECRET "$AZ_CLIENT_SECRET"
  cf set-env "$CF_APP_NAME" SECRET_KEY "$SECRET_KEY"
  cf push "$CF_APP_NAME" -b "$CF_BUILDPACK"
  ```
  
### Check the streaming logs for your app
  - Python version error? Modify your runtime.txt
  
### Visit your app
  https://cfmft.my-org
