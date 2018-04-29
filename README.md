# Small docker service for stuff relating to games

For now only highscores other features may come.

## Example `docker-compose.yml`

```
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
```            
You need to change the secret and you might need another external port.

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

## Planned future features

- [x] Clean up code.
- [x] Allow changing settings without restarting service
- [x] Add a status page for `/highscore/<game>` that lists top X for all scores o the game.
- [x] Add optional score settings support to name the score value (e.g. 'score', 'time', '$$$')
- [ ] Allow request to get any number of scores (within reason).
- [x] Include updated C# code for use in unity to communicate with this service into this repository.
