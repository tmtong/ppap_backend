.PHONY: docs

prereq:
	./requirements.sh
	mkdir -p temp log jsonsv002
mongodb:
	sudo systemctl start mongodb


wsbus:
	-pkill -f "python mimo/wsbus.py" > /dev/null 2>&1
	./bin/log.sh wsbus mimo/wsbus.py
autossh:
	./bin/reversessh_vnc1.sh

thinker:
	-pkill -f "python mimo/thinker.py" > /dev/null 2>&1
	./bin/log.sh thinker mimo/thinker.py

extract:
	python mimo/cis.py
action:
	./bin/log.sh action mimo/action.py

broadcast:
	./bin/log.sh broadcast mimo/broadcast.py

gitrcommit:
	git config --global http.sslVerify false
	git config --global credential.helper store
	# git add -u
	git add Makefile README.md
	-git add bin/*
	-git add -f data/*/*
	-git add docs/themes/*
	-git add docs/content/*/*.md
	-git add docs/content/*/*/*.md
	-git add docs/content/*/*/*/*.md
	-git add mimo/*.py tests/*.py
	-git add tmh/*.py
	-git add models/*.py models/*/* models/*/*/* models/*/*/*/* models/*/*/*/*/* models/*/*/*/*/*/*
	-git commit -a -m "`date`"
	git pull
	git push origin HEAD
gitrupdate:
	git config --global http.sslVerify false
	git config --global credential.helper store
	git pull

testweb:
	cd docs && hugo serve -D
publish:
	cd docs && hugo --buildDrafts
	scp -r -P 1512 docs/public/* tmtong@tmhicupc022:/home/tmtong/Documents/www/docs/

permissions:
	chmod 700 sec
	chmod 600 sec/*
	chmod 600 mimo/*.py
	chmod 700 mimo
	chmod 700 tests
	chmod 600 tests/*.py
	chmod 700 bin/requirements.sh
	chmod 700 models
	chmod 700 models/*
	chmod 600 models/*/*
	chmod 700 bin/*
	sudo chown -R tmtong:tmtong ~/.ssh
	sudo chown -R tmtong:tmtong ~/.vnc
	sudo chown -R tmtong:tmtong ~/.config
	chmod 700 ~/.ssh
	chmod 644 ~/.ssh/*.pub
	chmod 600 ~/.ssh/id_rsa
	[ -f ~/.ssh/authorized_keys ]  && chmod 640 ~/.ssh/authorized_keys
	sudo chown tmtong:tmtong ~/.vnc ~/.bashrc ~/.curlrc ~/.icons ~/.npmrc ~/opt
	chmod 700 ~/.vnc
	mkdir -p ~/Documents/www
	mkdir -p ~/Documents/www/doctor
tunnel:
	./bin/reversessh.sh


minify:
	./bin/minify.sh

copyminified:
	scp -r -P 1512 ../mimo_backend-minified tmtong@160.8.97.48:Documents/

binarymakeaction:
	./bin/binaryaction.sh

binarymakethinker:
	./bin/binarythinker.sh

binaryrunaction:
	./dist/action/action.exe

binaryrunthinker:
	./dist/thinker/thinker

copybinary:
	scp -r -P 1512 ../mimo_backend-binary tmtong@160.8.97.48:Documents/

sslkey:
	openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out sec/ssl.crt -keyout sec/ssl.key
jwtkey:
	openssl genrsa -out sec/private.jwt.sec 4096
	openssl rsa -in sec/private.jwt.sec -pubout > sec/public.jwt.sec

updatejsons:
	scp -P 1512 tmtong@tmhicupc022:Documents/mimo_backend/jsonsv002/hn2209* ./jsonsv002/
	scp -P 1512 tmtong@tmhicupc022:Documents/mimo_backend/jsonsv002/hn221* ./jsonsv002/

updatewwwdocs:
	scp -P 1512 ~/Documents/mimo_dashboard/docs/orientation.pdf tmtong@tmhicupc022:Documents/www/docs/
	scp -P 1512 ~/Documents/mimo_dashboard/docs/commandlist.pdf tmtong@tmhicupc022:Documents/www/docs/
	scp -P 1512 ~/Documents/mimo_dashboard/docs/userguide.pdf tmtong@tmhicupc022:Documents/www/docs/
