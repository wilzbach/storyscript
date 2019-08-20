http server as client
    when client listen path: "/" as request
        id = awesome id
        request write content: "https://{app.hostname}/?id={id}\n"
