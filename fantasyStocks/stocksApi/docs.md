### Introduction 

This API will allow access to the main models of FantasyStocks: `User`s, `Player`s, `Stock`s, `Floor`s, `Trade`s, and `StockSuggestion`s. They will all allow a set of common actions, and some will have special actions that apply to only that model. To prevent excessive redundancy, this documentation will include just one instance of each common action. For both common and special actions, the URL will be built up as follows:
```
/model_name/action/[id]
```

Not passing an `id` just does the action to all the instances of that model.

So if you want to view the `Player` with key 111, you would use this:

```
fantasystocks.herokuapp.com/api/v1/player/view/111
```

Some models have other models as fields. If those fields were sent as full representations, there would be infinite loops. To counteract this, full model representations will only be sent one level deep. For example, if the server sends a `Player` model to a client, the `floor` field will be an actual JSON object representing a `Floor`, with the `Floor`'s name, its `numStocks`, et cetera, but the array of `Player`s in that `Floor` will instead be an array of `id`s of `Player`s, not actual `Player` objects. Otherwise, since each `Player` has a reference to its `Floor`, and each `Floor` in turn has a list of `Player`s, this would cause an infinite recursion.

Authentication will be handled through the `auth` endpoints. This mechanism will be detaled further below, but put simply, the caller receives a temporary session key, which it passes to the endpoints as a GET parameter. This will be meaningless for some calls, optional for others, and for still others mandatory. POST requests, as a rule, demand a session id. GET requests usually will not, but sometimes the server will be able to supply more information if a session id is passed. Passing an unncessary session id will never cause an error, however, even if the session id is expired.

POST request data is sent as JSON (`content-type: application/json`) in the body of the POST request, not as url-encoded of form data.

### Data Schemas

These schemas detail how each model will be serialized into JSON.

*NB: The descriptions given here will be in a YAML-like format for easy reading, but the actual responses coming across the wire will be in JSON.*

#### User

Note that this differs from a `Player` model in that one `User` maps to one actual human being playing the game. The `Player` model is an instance of a `User` on a particular `Floor`.

```
- id (integer)
- username (string)
- players (array of Players)
```

#### Player

Note that the `isFloor` field tells whether the given `Player` is the "floor player." This is the player that is owned by no actual person but rather holds all the `Stock`s that are available on a `Floor` but that no one currently owns.
Also, `sentTrades` and `receivedTrades` only include `Trade`s that are still alive (ie, have neither been declined or accepted)

```
- id (integer)
- user (User)
- floor (Floor)
- stocks (array of Stocks)
- points (integer)
- isFloor (boolean)
- sentTrades (array of Trades)
- receivedTrades (array of Trades)
- isFloorOwner (boolean)
```

#### Stock

```
- id (integer)
- companyName (string)
- symbol (string)
- lastUpdated (ISO 8601 datetime string)
- price (real)
- change (real)
- StockSuggestions (array of StockSuggestions)
```

#### Floor

Note that `numStocks` is the maximum number of stocks that a `Player` on the floor can have

```
- id (integer)
- name (string)
- stocks (array of Stocks)
- permissiveness (enum: either "Permissive", "Open", or "Closed", as a string)
- owner (User)
- floorPlayer (Player)
- public (boolean)
- numStocks (integer)
```

#### Trade 

Note that `recipientStocks` and `senderStocks` are the stocks that those players would give away in the trade

```
- id (integer)
- recipientPlayer (Player)
- recipientStocks (array of Stocks)
- senderPlayer (integer)
- senderStocks (array of Stocks)
- floor (Floor)
- date (ISO 8601 datetime string)
```

#### StockSuggestion

This is the model that indicates to the owner of a `Floor` that someone wants a certain stock added to a floor. This can only happen when a certain floor has a permissiveness of "permissive;" if the floor is "open", stocks will be automatically added whenever a player wants them to, and if it is "closed", they can never be added by anyone.

```
- id (integer)
- stock (Stock)
- requestingPlayer (Player)
- floor (Floor)
- date (ISO 8601 datetime string)
```

### Common Actions

#### `GET /view/`

This will do nothing more than show the requested object's JSON representation. It just returns a JSON object of the model, or if there is nothing, it returns an error object of the form:

```
{"error": "That object could not be found"}
```

Note that, while some objects are available to anyone, there are some that are private (`Trade`s and `StockSuggestion`s, namely). To access these, you will need to pass a session key that maps to someone who is associated with the requested model instance (ie, the owner of the floor, the sender, or the recipient).

#### `POST /create/`

This creates an instance of the given model. Note that no `id` needs to be passed to this. You do need to pass the session key of a user that is allowed to create the desired model in the GET query string, and the POST data should be the JSON representation of the model just as if it were returned from the API, with the exception of `id` and some other fields, depending on the model. Any fields that would contain models in `/view/` responses must hold `id`s or arrays of `id`s to appropirate models in `/create/` calls. 
Also, `Stock`s can only be created by the system, so a client cannot call `/stock/create`.

 - `User`s
    - `players` must not be passed
    - `email` can be passed optionally, will default to empty 
    - A `password` must be passed
    - NB that no `sessionId` is necessary to create a `User`.
  - `Player`s
    - `stocks` can be passed optionally, will default to empty
    - `points` cannot be passed
    - `isFloor` cannot be passed
    - `sentTrades` cannot be passed
    - `receivedTrades` cannot be passed
    - `isFloorOwner` cannot be passed
 - `Floor`s
    - `stocks` can be passed optionally, defaults to empty if and only if the `Floor` does not have permissiveness "closed," in which case there must be at least one `Stock` on the floor.
    - `owner` is the id of the `User` object who who owns the `Floor`
    - `floorPlayer` cannot be passed
 - `Trade`s
    - `recipientStocks` must be passed, but it can be empty
    - `senderStocks` must be passed, but it can be empty
    - One of `senderStocks` or `recipientStocks` must have something in it.
    - `date` cannot be passed
 - `StockSuggestion`s
    - `date` is optional (and frankly discouraged), defaults to the current time

This returns the created object as if it had been requested at the `/view/` endpoint.

#### `POST /delete/`

Deletes the given object. This also takes a session key, and will return an authentication error if the given key doesn't have the proper permission to delete the given object. If it is successful, returns an object of the form: 

```
{"success": "The object was successfully deleted"}
```

### Special actions

#### `POST /trade/accept/`

Accepts the given trade, automatically moving the stocks where they should go. This needs a session id that belongs to the recipient, or else it will return an auth error. If it is successful, returns an object of the form:

```
{"success": "The trade was successfully accepted"}
```

#### `POST /trade/decline/`

Declines the given trade. This needs a session id that belongs to the recipient, or else it will return an auth error. If it is successful, returns an object of the form:

```
{"success": "The trade was successfully declined"}
```

#### `POST /stockSuggestion/accept/`

Accepts the given `stockSuggestion`. This needs a session id that belongs to the `Floor` owner, or else it will return an auth error. If it is successful, returns an object of the form:

```
{"success": "The stockSuggestion was successfully accepted"}
```

#### `POST /stockSuggestion/reject/`

Rejects (ie, deletes) the given `stockSuggestion`. This needs a session id that belongs to the `Floor` owner, or else it will return an auth error. If it is successful, returns an object of the form:

```
{"success": "The stockSuggestion was successfully rejected"}
```

### Auth

The auth system will work based on logins and session ids. Session ids will be tied to a `User` object and will expire after a time. Except when the session id is meaningless, passing an expired session token will cause an error of the form:

```
{"authError": "The session id you passed is either expired or never existed"}
```

Receiving this error means that you should get another session key.

#### `POST /auth/getKey/`

No id is passed to this endpoint; rather, a `username` and a `password` should be passed in the POST body. If they match a `User` in the database, the server will send a response of the form:

```
{
    "sessionId": "1234567890",
    "user": {// This is a user object}
}
```

Otherwise, it will return an error of the form:

```
{"error": "That (username|password) doesn't exist"}
```

### Android App Compatibility

For the Android app, there is also an endpoint to register a Firebase Cloud Messaging registration token with a `User`.

#### `POST /android/register/`

This endpoint only demands the session id (in the GET querystring) and the `registrationToken`, in the POST data payload. If successful, it returns a message of the form:

```
{"success": "Your registration id was successfully registered with [username]"}
```

#### `POST /android/deregister/`

This endpoint takes the same data as the `/register/` endpoint, but it removes the relation between the `registrationToken` and the `User`.
