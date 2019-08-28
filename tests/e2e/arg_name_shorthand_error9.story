http server as client
    when client listen path:"/" :"post" as result
        result write content: "foobar"
