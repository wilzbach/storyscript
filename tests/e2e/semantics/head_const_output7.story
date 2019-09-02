http server as client
    when client listen method:"post" path:"/foo" as res
        res.body = 2
