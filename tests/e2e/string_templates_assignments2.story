b = yaml parse data:"b"
d = yaml parse data:"d"
a1  = "0" + "a{yaml format data:b}c{yaml format data: d}"
a2  = "a{yaml format data:b}c{yaml format data:b}" + "0"
a3  = "0" + "a{yaml format data:b}c{yaml format data:b}" + "0"
a4  = "0" + "{yaml format data:b}" + "0"
a5  = "0" + "{yaml format data:b}"
a6  = "{yaml format data:b}" + "0"
a7  = "0" + "a{yaml format data:b}"
a7  = "a{yaml format data:b}" + "0"
a8  = "0" + "a{yaml format data:b}" + "0"
a9  = "a{yaml format data:b}c" + "0"
a10 = "0" + "a{yaml format data:b}c"
a11 = "0" + "a{yaml format data:b}c" + "0"
a12 = "a{yaml format data:b}c{yaml format data:b}" + "0"
a13 = "0" + "a{yaml format data:b}c{yaml format data:b}"
a14 = "0" + "a{yaml format data:b}c{yaml format data:b}" + "0"
