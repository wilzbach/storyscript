http server as server
    when server listen method: "get" path: "/" as r
        r write content: "Hello world!"
