### Introduction 

This API will allow access to the main models of FantasyStocks: `Users`, `Players`, `Stocks`, `Floors`, and `Trades`. They will all allow roughly the same actions, although there will be some (documented) exceptions. That said, to prevent excessive redundancy, this documentatioe will include just one instance of each action, and the actions will be built up in the URL. Therefore, if you want to do the `view` action on a `Floor` object with key 32, you'll use this url:

```
/floor/view/32
```

If you want to do the same action on the `Player` with key 111, you would use this one:

```
player/view/111
```

Those two URLs will return similar data payloads, excepting of course the actual data for the requested model instance, which will be in a format detailed below.

Additionally, this API will handle authentication through the `auth` endpoints. This mechanism will be detaled separately from everything else.

### Data Schemas

As stated above, the API responses will be similar across models with the exception, obviously, of the acutal model information. That part of each res[pmse will depend on the model in question and will be described here. 
*NB: The descriptions given here will be in a YAML-like format, but the actual responses coming across the wire will be in JSON.*

#### User

```
- id (integer)
- username (string)
- players (array of Players)
```
