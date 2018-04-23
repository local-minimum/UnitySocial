#Settings

Using JSON should have settings in `settings.json`.

```
{
  system: {
  },
  games: {
    mygame: {
      format: {
        type: "raw",
        delimiter: "\t",
	line: "\n"
      },
      scores: { 
        birding: {
	  sort: "ascending",
	  score: "int",
	  min: 0,
	  max: 1000,
	}
      }
    }
  }
}
```

like so
