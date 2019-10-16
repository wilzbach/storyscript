http server as client
    when client listen method:"get" path:"/" as request
        a = (request get_header key:"foo-url") + (request get_header key:"bar-url")
