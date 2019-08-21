a = {"foo": {"bar": ""}}
{ b, c } = a.get(key:"foo" default:{} as Map[string,string])
