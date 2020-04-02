# YouTubeReviewBot
YouTube Review Bot - Wikimedia Commons

Work in progress https://github.com/eatcha-wikimedia/ytrBot/blob/master/release.py

# work in progress

```
Traceback (most recent call last):
  File "main.py", line 332, in <module>
    main()
  File "main.py", line 328, in main
    checkfiles()
  File "main.py", line 228, in checkfiles
    if archived_webpage(archive_url) == None:
  File "main.py", line 92, in archived_webpage
    req = Request(archive_url,headers={'User-Agent': 'User:YouTubeReviewBot on wikimedia commons'})
  File "/usr/local/lib/python3.8/urllib/request.py", line 328, in __init__
    self.full_url = url
  File "/usr/local/lib/python3.8/urllib/request.py", line 354, in full_url
    self._parse()
  File "/usr/local/lib/python3.8/urllib/request.py", line 383, in _parse
    raise ValueError("unknown url type: %r" % self.full_url)
ValueError: unknown url type: 'None'
```

https://repl.it/repls/DamagedCadetblueAlgorithms
