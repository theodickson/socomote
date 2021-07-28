TODO
----

- Package it
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
  - Also want to limit action queueing, this could be done by:
    - Returning action processing to be synchronous
      - Probably a bad idea, think we get slightly faster skipping with
        the threads
    - Using a threadpool to limit concurrent action threads
      - This would mean that the action queue can actually get
        backed up since once the pool is all running, nothing
        is popped from the queue until one is finished.
      - 3 & 3 is probably too much, this means 6 skips will get queued.
      - Probably just let 2 concurrent actions so we get the fast skip,
        and then limit queue to 1?
