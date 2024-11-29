# UserCreationBackend
The blahaj.land for self-registration

# TODO
- Finish support for creating wesbites
  - We need a way to verify ownership, delete them, reset them, manage SFTP passwords
- create_website function in flask_utils.py needs to be slightly reworked to actually send out the correct mails
- mongo needs to add the users tier (by default starter)
- endpoint to manage user tiers
- perhaps we could add additional administration endpoints to create an alternative admin panel which would also manage the db stuff, since yunohost cant do that
- queue system for the tasks since yunohost can only do one thing at a time





