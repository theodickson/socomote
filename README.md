TODO
----

- Packaging:
  - Create socomote home
  - Create default config.yaml
  - create mp3 lib (probably in code not config)
  - unix only?
- Configurable keymap
- Infinite retry loop e.g. if network not yet ready?
- Async usage?
- Use timing instead of enter for numbers
  - could then use enter as something else
- Better action handling:
  - Want to be able to skip fast, which means not waiting
    for the URI to play.
  - Not sure this is possible, currently just threading
    actions and they seem to queue server-side.
  - This *may* be to do with the POST requests being long running,
    which means *possibly* if they are cancelled somehow client-side
    this can be done.
    
    