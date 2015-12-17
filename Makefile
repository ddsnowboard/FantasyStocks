.PHONY: vim templates
FILES = fantasyStocks/fantasyStocks/settings.py fantasyStocks/fantasyStocks/urls.py fantasyStocks/stocks/admin.py fantasyStocks/stocks/models.py fantasyStocks/stocks/tests.py fantasyStocks/stocks/views.py fantasyStocks/stocks/stockUrls.py fantasyStocks/stocks/forms.py

all: 
	vim fantasyStocks/stocks/templates/* fantasyStocks/static/* $(FILES)
vim : 
	vim $(FILES)
templates : 
	vim fantasyStocks/stocks/templates/* fantasyStocks/static/*
test : 
	python3 ./fantasyStocks/manage.py test ./fantasyStocks/
	cd ..
