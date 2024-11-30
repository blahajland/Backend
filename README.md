# UserCreationBackend
The blahaj.land for self-registration
---

# TODO
- Finish support for creating wesbites
  - We need a way to verify ownership, delete them, reset them, manage SFTP passwords
- create_website function in flask_utils.py needs to be slightly reworked to actually send out the correct mails
- mongo needs to add the users tier (by default starter)
- endpoint to manage user tiers
- perhaps we could add additional administration endpoints to create an alternative admin panel which would also manage the db stuff, since yunohost cant do that
- queue system for the tasks since yunohost can only do one thing at a time
- actually send the discord webhooks with an admin role ping
- referral code support (simple code stored in the database after the tier)

---

# Sample JSON requests for the endpoints
## /login 
```JSON
{
    "username": "example_user",
    "password": "example_password"
}
```
Method: POST

Description: Authenticates a user and returns a JWT access token if the credentials are correct

Response Codes:

200 OK: Returns a JSON with the access token

401 Unauthorized: Returns a JSON with a message indicating bad username or password
---

## /create_user
```JSON
{
    "username": "newuser",
    "display_name": "New User",
    "recovery_email": "new_user@example.com",
    "discord_username": "new_username"
}
```
Method: POST

Description: Creates a new user. Requires JWT authentication

Response Codes:

201 Created: Returns a JSON with a success message

432 Conflict: Returns a JSON with an error message indicating the username is already taken

500 Internal Server Error: Returns a JSON with an error message indicating user creation failed

### This endpoint requires an auth bearer JWT token which we get from **/login** 

---

## /request_password_reset
```JSON
{
    "username": "example_user"
}
```

Method: POST

Description: Requests a password reset for a user by sending a reset link to their recovery email saved in the mongo database

Response Codes:

200 OK: Returns a JSON with a message indicating the reset link was sent

404 Not Found: Returns a JSON with an error message indicating the user was not found

---

## /reset_password
```JSON
{
    "token": "example_reset_token"
}
```

Method: GET

Description: Resets the password for a user using a provided reset token

Request Parameters:

token: The reset token provided in the reset link sent via email, contained in the URL

Response Codes:

400 Bad Request: Returns a JSON with an error message indicating the token was not provided

900 Invalid Token: Returns a JSON with an error message indicating the token is invalid or expired

901 Expired Token: Returns a JSON with an error message indicating the token has expired

302 Found: Redirects to the password reset page
---

