http server as s/
    when s/ listen path: "/" as r
        r write content: "foobar"
