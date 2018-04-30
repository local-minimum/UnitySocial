#Settings

Using JSON should have settings in `settings.json`.

```json
{
  "settings": {
  },
  "games": {
    "mygame": {
      "settings": {
        "type": "raw",
        "delimiter": "\t",
	      "line": "\n",
        "scoresToList": 25,
        "name": "Being Human Fancying Birds"
      },
      "scores": {
        "birding": {
          "sort": "ascending",
          "score": "int",
          "min": 0,
          "max": 1000,
          "name": "Top Birders",
          "scoreName": "Observations",
          "description": "This score is about how good a human you are or how many birds you've seen."
        }
      }
    }
  }
}
```

## Games

Games need scores and can have settings.

### Settings

* `type` indicate what format the api communicates back in.
 * `raw` is a tab delimited format (default, uses keys `delimiter` and `line`)
* `delimiter` what separates the columns for the `raw` format, default is `"\t"` (tab).
* `line` what is a new line in the raw format, default is `"\n"` (newline).
* `scoresToList` is how many scores to be returned on requests as default.
This can be overridden by `?count=XX` in the request.
There's also a global defaults environmental variable for the container which
will be used if this is omitted.
* `name` is the human readable name of the game, if omitted the capitalized key
for the game will be used. 

### Scores

All settings optional. Minimal settings for a score would be:
```JSON
      "scores": {
        "birding": {}
      }
```

* `sort` is either `"ascending"` (default) or `"descending"`.
* `score` can be either `"int"` (default) or `"float"`.
* `min` and `max` are not yet implemented, but will reject posting scores outside their limits.
* `name` a human readable name for display. Else a capitalized version of the `scores` key of the score will be used. (Shown on status page)
* `description` a human readable description of the score. (Shown on status page)
* `scoreName` a human readable name of the score. Will default to `"Score"`.
