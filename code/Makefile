.PHONY: build up down clean
build:
	docker build -t planet:0.0.1 . -f Dockerfile
	docker build -t station:0.0.1 . -f Dockerfile2

up:
	docker network create --subnet=42.42.42.0/24 coreworlds
	docker run --network=coreworlds -d --hostname Alderaan --privileged  --name Alderaan -t planet:0.0.1
	x-terminal-emulator -e 'docker exec -it Alderaan /bin/bash' &
	docker run --network=coreworlds -d --hostname Tatooine --privileged  --name Tatooine -t planet:0.0.1
	x-terminal-emulator -e 'docker exec -it Tatooine /bin/bash' &
	docker run --network=coreworlds -d --hostname Deathstar --privileged  --name Deathstar -t station:0.0.1
	x-terminal-emulator -e 'docker exec -it Deathstar /bin/bash' &

down:
	docker kill Alderaan
	docker rm Alderaan
	docker kill Tatooine
	docker rm Tatooine
	docker kill Deathstar
	docker rm Deathstar
	docker network rm coreworlds

clean:
	docker image rm planet:0.0.1
	docker image rm station:0.0.1
