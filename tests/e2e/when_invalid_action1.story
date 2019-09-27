a = 1
http server
    when a listen path: "/" as r
        r write content: "foobar"
