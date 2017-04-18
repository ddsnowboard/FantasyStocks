.PHONY: vim templates test run tags
FILES = fantasyStocks/fantasyStocks/settings.py fantasyStocks/fantasyStocks/urls.py fantasyStocks/stocks/admin.py fantasyStocks/stocks/models.py fantasyStocks/stocks/tests.py fantasyStocks/stocks/views.py fantasyStocks/stocks/stockUrls.py fantasyStocks/stocks/forms.py
API_FILES = fantasyStocks/stocksApi/admin.py fantasyStocks/stocksApi/apps.py fantasyStocks/stocksApi/models.py fantasyStocks/stocksApi/tests.py fantasyStocks/stocksApi/urls.py fantasyStocks/stocksApi/views.py

all: 
	vim fantasyStocks/stocks/templates/* fantasyStocks/static/* $(FILES)
vim : 
	vim $(FILES)

api:
	vim $(API_FILES)
templates : 
	vim fantasyStocks/stocks/templates/* fantasyStocks/static/*
test : fantasyStocks/db.sqlite3
	python3 ./fantasyStocks/manage.py test ./fantasyStocks/ --parallel 4
singleTest : fantasyStocks/db.sqlite3
	python3 ./fantasyStocks/manage.py test ./fantasyStocks/
run : fantasyStocks/db.sqlite3
	python3 ./fantasyStocks/manage.py runserver
tags : 
	zsh -c "ctags -R ./fantasystocks/**/*.c(N) ./fantasystocks/**/*.py(N) ./fantasystocks/**/*.html(N) ./fantasystocks/**/*.js(N) ./fantasystocks/**/*.java(N)"
cloneDB :
	sqlite3 fantasyStocks/db.sqlite3 < db.dump
freezeDB :
	echo ".dump" | sqlite3 fantasyStocks/db.sqlite3 > db.dump

fantasyStocks/db.sqlite3 : 
	$(MAKE) cloneDB

failFast : fantasyStocks/db.sqlite3
	python3 ./fantasyStocks/manage.py test ./fantasyStocks/ --failfast

runFreshDb :
	@rm fantasyStocks/db.sqlite3
	$(MAKE) run
