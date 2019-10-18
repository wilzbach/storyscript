when http server listen path: "/" as r
  query = r.query_params["query"]
  r redirect url: "https://google.com/search" query: {"q": query}
