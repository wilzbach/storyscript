twitter stream
    when tweet as t
        break
    when tweet track: "storyscript"
        break
    when tweet track: "storyscript" as t
        break

twitter stream as s
    when s tweet
        break
    when s tweet as t
        break
    when s tweet track: "storyscript"
        break
    when s tweet track: "storyscript" as t
        break
