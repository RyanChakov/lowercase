# state-grb-3-back-end
the central repository for completed and combined back-end code

## ToDo
**all tasks are due by team meeting Sunday**

### Metadata Engine

**TEAM: David Jeffrey Ellinore Ryan Chris**

Put the metadata functions into a class named **metadata_engine()**

functions to include: 

	init
		html = ''
		text= ''	

	prime_engine(HTML)
		html = HTML
		text = get_text(HTML)

	get_dates(text)-> dates
	get_entities(text)-> entities
	get_sentiment(text)-> sentiment
	get_hyperlinks(html)-> hyperlinks
	get summary(text)-> summary


put the final file in state-grb-3-back-end/metadata_engine.py 
https://github.com/state-grb-3/state-grb-3-back-end/blob/main/metadata_engine.py

### GDELT_Driver:

**TEAM: Jacob Adam**

Rework the driver, using new class and file definitions from metadata_engine and DatabaseAPI
https://github.com/state-grb-3/state-grb-3-back-end/blob/main/gdelt_driver.py

### DatabaseAPI:

**TEAM: Dennis**

Rework the database and the DatabaseIPI ssentences input to provide a connection between each sentence and its particular named entities (this may require a new table)


Ensure all changes are pushed to this repo
