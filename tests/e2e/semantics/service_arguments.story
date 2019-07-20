http server as api
    when api listen method: "get" path: "/" as r
        r write content: msg
