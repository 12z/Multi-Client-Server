to start server:
docker run -ti --rm --name server ipuzankov/client-server python /src/ia1/server.py

to start client:
docker run -ti --link server ipuzankov/client-server python /src/ia1/client.py user server