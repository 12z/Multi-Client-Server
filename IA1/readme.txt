to start server:
docker run -ti --rm --name server 13.92.240.181:5000/ipuzankov/client-server python /src/ia1/server.py

to start client:
docker run -ti --link server 13.92.240.181:5000/ipuzankov/client-server python /src/ia1/client.py user server
