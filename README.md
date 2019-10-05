Kodi plugin to watch video from the French site Arrêt sur Images.

# protocol
The website has been reworked and reshaped.
This is a try to document the API while porting the plugin.

## login request
URL: https://api.arretsurimages.net/oauth/v2/token
method: POST

Unfortunatly client_id and client_secret are fully exposed in the JS. OAuth doc say it should not.
``` json
{
client_id: "1_1e3dazertyukilygfos7ldzertyuof7pfd"
client_secret: "2r8yd4a8un0fn45d93acfr3efrgthzdheifhrehihidg4dk5kds7ds23"
grant_type: "password"
password: "UserPassword"
username: "user_email@domain.tld"
}
```
