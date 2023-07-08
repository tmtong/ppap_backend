.PHONY: docs mongodump

wsbus:
	-pkill -f "python ppap/wsbus.py" > /dev/null 2>&1
	./bin/log.sh wsbus ppap/wsbus.py

gitrcommit:
	rm -rf .git/hooks/pre-push .git/hooks/post-push
	rm -rf .git/hooks/post-commit
	rm -rf .git/hooks/post-merge .git/hooks/post-checkout
	git config --global http.sslVerify false
	git config --global credential.helper store
	# git add -u
	git add Makefile README.md
	-git add bin/*
	-git rm data/selfdiagnostics
	-git add docs/themes/*
	-git add docs/content/*/*.md
	-git add docs/content/*/*/*.md
	-git add docs/content/*/*/*/*.md
	-git add mimo/*.py tests/*.py
	-git add tmh/*.py
	-git add models/*.py models/*/* models/*/*/* models/*/*/*/* models/*/*/*/*/* models/*/*/*/*/*/*
	-git commit -a -m "`date`"
	git pull --no-rebase
	git push origin HEAD
	mkdir -p data/selfdiagnostics
	cp -r data/selfdiagnostics_backup/* data/selfdiagnostics/

gitrupdate:
	git config --global http.sslVerify false
	git config --global credential.helper store
	git pull --no-rebase

