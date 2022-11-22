.PHONY: docs

prereq:
	./bin/requirements.sh
mongodb:
	sudo systemctl start mongodb



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

