# Small docker service for stuff relating to games

For now only highscores other features may come.

**Please note that this solution only offers moderate security and should not be used in any comercial or higher impact solution but should hopefully be more than enough for jam-games and similar**

## Example `docker-compose.yml`

```yml
version: '3.1'
services:
    highscores:
        container_name: highscores
        ports:
            - "5000:5000"
        build: .
        restart: always
        volumes:
            - ./settings/settings.json:/app/settings/settings.json:ro
            - ./db/:/app/db/
        environment:
            - HIGHSCORE_SECRET=somethingrandomsecret
            - HIGHSCORE_APP_ROOT=/unity
            - HIGHSCORE_MAX_COUNT=50
            - DEFAULT_HIGHSCORES
```            
Note that the external port must be something your gateway redirects to.

### Volumes
* You need to have a `settings.json` mounted (see settings https://github.com/local-minimum/UnitySocial/edit/master/settings/README.md)
* The database directory can be empty.

### Environmental variables
* `HIGHSCORE_SECRET` you need to set something and it should never be commited to github or shared.
* `HIGHSCORE_APP_ROUTE` (optional) if you wish the service to identify with some prefix.
* `HIGHSCORE_MAX_COUNT` (optional) The max number of highscores allowed to get from the api (defaults to 100).
* `DEFAULT_HIGHSCORES` (optional)  The default number of highscores gotten from api (defaults to 20)

## Configurating your gateway
If you're hosting a webgame somewhere like itch.io, you will need to have https setup for the service for browsers to allow communications with the server.
Even if you have standalone game, sending scores in plaintext is probably a bad idea.

You probably also need to configure your gateway service to do some header magic.

For nginx it may look like this:
```
        location /unity {
            proxy_pass highscores:5000;
            proxy_set_header    X-Real-IP       $remote_addr;
            add_header 'Access-Control-Allow-Origin' *;
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Headers' 'Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        }
```
