import unittest
from json import dumps
from ddt import ddt, data

import storyscript


@ddt
class Tests(unittest.TestCase):
    maxDiff = None

    def expand_script(self, script):
        """ < line: line; line;
           > line\n\tline\nline
        """
        lines = script.replace(': ', ':\n').replace('; ', ';\n').split('\n')
        script = []
        indent = 0
        for line in lines:
            to = 0
            if line.endswith(':'):
                to = 1
                line = line[:-1]
            elif line.endswith(';'):
                to = -1
                line = line[:-1]
            script.append("".join(("\t"*indent, line)))
            indent = indent + to
        return "\n".join(script)

    @data(("foreach product: pass", {'args': [{'path': 'product'}], 'output': None, 'linenum': '1', 'method': 'foreach', 'parent': None, 'kwargs': None}),
          ("set x to _customer twitter username", {'output': None, 'args': ['x', {'path': '_customer.twitter.username'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to unique product prices", {'output': None, 'args': ['x', {'path': 'prices', 'unique': True, 'figure': 'product'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to random unique myList prices where firstname is 'joe' and lastname like /^andy/ sort by name asc", {'output': None, 'args': ['x', {'figure': 'myList', 'agg': 'random', 'limit': 1, 'sortby': 'name', 'path': 'prices', 'unique': True, 'where': {'values': {'1': {'right': {'regexp': '^andy'}, 'method': 'like', 'left': {'path': 'lastname'}}, '0': {'right': {'value': 'joe'}, 'method': 'is', 'left': {'path': 'firstname'}}}, 'expression': '{0} and {1}'}, 'dir': 'asc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to products where name like 'joe' and price > $10", {'output': None, 'args': ['x', {'where': {'values': {'1': {'path': 'price'}, '0': {'right': {'value': 'joe'}, 'method': 'like', 'left': {'path': 'name'}}}, 'expression': '{0} and {1} > 10.0'}, 'figure': 'products'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to 5 stores order totals where totals > $1000 sort by total for 'last 10 days'", {'output': None, 'args': ['x', {'figure': 'order', 'limit': 5, 'sortby': 'total', 'time': {'value': 'last 10 days'}, 'path': 'totals', 'where': {'values': {'0': {'path': 'totals'}}, 'expression': '{0} > 1000.0'}, 'groupby': 'stores'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to store order totals where totals > 50", {'output': None, 'args': ['x', {'path': 'totals', 'where': {'values': {'0': {'path': 'totals'}}, 'expression': '{0} > 50.0'}, 'groupby': 'store', 'figure': 'order'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to stores where name like 'fef'", {'output': None, 'args': ['x', {'where': {'right': {'value': 'fef'}, 'method': 'like', 'left': {'path': 'name'}}, 'figure': 'stores'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to sum of store order totals where sum of total > $50 for 'last 10 days'", {'output': None, 'args': ['x', {'figure': 'order', 'agg': 'sum', 'time': {'value': 'last 10 days'}, 'path': 'totals', 'where': {'values': {'0': {'agg': 'sum', 'path': 'total'}}, 'expression': '{0} > 50.0'}, 'groupby': 'store'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to random store where order totals > $100", {'output': None, 'args': ['x', {'agg': 'random', 'where': {'values': {'0': {'path': 'order.totals'}}, 'expression': '{0} > 100.0'}, 'limit': 1, 'figure': 'store'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to avg store order totals", {'output': None, 'args': ['x', {'agg': 'avg', 'path': 'totals', 'groupby': 'store', 'figure': 'order'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to first 3 store order totals where avg order tax > $50 sort by tax desc", {'output': None, 'args': ['x', {'figure': 'order', 'limit': 3, 'sortby': 'tax', 'path': 'totals', 'where': {'values': {'0': {'agg': 'avg', 'path': 'order.tax'}}, 'expression': '{0} > 50.0'}, 'groupby': 'store', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to store with most products sold for '2014'", {'output': None, 'args': ['x', {'figure': 'products', 'agg': 'count', 'limit': 1, 'sortby': 'sold', 'time': {'value': '2014'}, 'path': 'sold', 'groupby': 'store', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set x to the customer with most orders at _store for 'this year'", {'output': None, 'args': ['x', {'figure': 'customer', 'agg': 'count', 'limit': 1, 'location': '_store', 'time': {'value': 'this year'}, 'path': 'orders', 'groupby': 'customer', 'dir': 'desc', 'sortby': 'orders'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to lowest 5 products sold for "2014"', {'output': None, 'args': ['x', {'figure': 'products', 'limit': 5, 'sortby': 'sold', 'time': {'value': '2014'}, 'path': 'sold', 'groupby': 'products', 'dir': 'asc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to highest 10% order totals for "2014"', {'output': None, 'args': ['x', {'figure': 'order', 'limit': '10.0%', 'sortby': 'totals', 'time': {'value': '2014'}, 'path': 'totals', 'groupby': 'order', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to average product unit where type is not "item"', {'output': None, 'args': ['x', {'agg': 'average', 'path': 'unit', 'where': {'right': {'value': 'item'}, 'method': 'isnt', 'left': {'path': 'type'}}, 'limit': 1, 'figure': 'product'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to sum of top 10% order totals sort by total desc for "2014"', {'output': None, 'args': ['x', {'figure': 'order', 'agg': 'sum', 'limit': '10.0%', 'sortby': 'total', 'time': {'value': '2014'}, 'path': 'totals', 'groupby': 'order', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to average of store order totals', {'output': None, 'args': ['x', {'agg': 'average', 'path': 'totals', 'groupby': 'store', 'figure': 'order'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the top 20% of customers with most orders for "last 30 days"', {'output': None, 'args': ['x', {'figure': 'customers', 'agg': 'count', 'limit': '20.0%', 'sortby': 'orders', 'time': {'value': 'last 30 days'}, 'path': 'orders', 'groupby': 'customers', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the customer with the most rewards earned for "last 7 days"', {'output': None, 'args': ['x', {'figure': 'rewards', 'agg': 'count', 'limit': 1, 'sortby': 'earned', 'time': {'value': 'last 7 days'}, 'path': 'earned', 'groupby': 'customer', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the employee with the most hours worked for "this week"', {'output': None, 'args': ['x', {'figure': 'hours', 'agg': 'count', 'limit': 1, 'sortby': 'worked', 'time': {'value': 'this week'}, 'path': 'worked', 'groupby': 'employee', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the products with the lowest sales for "2014"', {'output': None, 'args': ['x', {'figure': 'products', 'agg': 'count', 'limit': 1, 'sortby': 'sales', 'time': {'value': '2014'}, 'path': 'sales', 'groupby': 'products', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to customer where average order size > $50', {'output': None, 'args': ['x', {'where': {'values': {'0': {'agg': 'average', 'path': 'order.size'}}, 'expression': '{0} > 50.0'}, 'figure': 'customer'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the number of products', {'output': None, 'args': ['x', {'path': 'count', 'limit': 1, 'figure': 'products'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the number of orders for "2014"', {'output': None, 'args': ['x', {'path': 'count', 'limit': 1, 'figure': 'orders', 'time': {'value': '2014'}}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the oldest order for "January 2014"', {'output': None, 'args': ['x', {'agg': 'oldest', 'limit': 1, 'figure': 'order', 'time': {'value': 'January 2014'}}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set c to customers where email like 'hello'", {'output': None, 'args': ['c', {'where': {'right': {'value': 'hello'}, 'method': 'like', 'left': {'path': 'email'}}, 'figure': 'customers'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set c to true", {'output': None, 'args': ['c', True], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set c to false", {'output': None, 'args': ['c', False], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set c to false; "*3, {'output': None, 'args': ['c', False], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set c to apple.orange[1]; ", {"output": None, "args": ["c", {"path": "apple.orange[1]"} ], "method": "set", "parent": None, "kwargs": None , 'linenum': '1'}),
          ("set c to apple.orange['corey']; ", {"output": None, "args": ["c", {"path": "apple.orange['corey']"} ], "method": "set", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('set c to apple.orange["steve.peak"]; ', {"output": None, "args": ["c", {"path": "apple.orange[\"steve.peak\"]"} ], "method": "set", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('set c to apple.orange[1..2]; ', {"output": None, "args": ["c", {"path": "apple.orange[1..2]"} ], "method": "set", "parent": None, "kwargs": None , 'linenum': '1'}),
          ("# hello; this", {}),
          ("set x to not_me", {"output": None, "args": ["x", {"path": "not_me"} ], "method": "set", "parent": None, "kwargs": None , 'linenum': '1'}),
          ("set x to equals_it", {"output": None, "args": ["x", {"path": "equals_it"} ], "method": "set", "parent": None, "kwargs": None , 'linenum': '1'}),
          ("set x to true_it", {"output": None, "args": ["x", {"path": "true_it"} ], "method": "set", "parent": None, "kwargs": None , 'linenum': '1'}),
          ("append x into y", {'output': None, 'args': [{'path': 'x'}, {'path': 'y'}], 'method': 'append', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("remove x from y", {'output': None, 'args': [{'path': 'x'}, {'path': 'y'}], 'method': 'remove', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if x is not equal to y: pass", {'output': None, 'args': [{'values': {'1': {'path': 'y'}, '0': {'path': 'x'}}, 'expression': '{0} != {1}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if name like /^Steve/: pass", {'output': None, 'args': [{'right': {'regexp': '^Steve'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if name is like /^Steve/: pass", {'output': None, 'args': [{'right': {'regexp': '^Steve'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if name is not like /.*joe$/: pass", {'output': None, 'args': [{'right': {'regexp': '.*joe$'}, 'method': 'notlike', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if name like 'steve': pass", {'output': None, 'args': [{'right': {'value': 'steve'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if name like 'steve with {{this}}': pass", {'output': None, 'args': [{'right': {'values': {'0': {'path': 'this'}}, 'string': 'steve with {0}'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if _c has name: pass", {'output': None, 'args': [{'right': {'path': 'name'}, 'method': 'has', 'left': {'path': '_c'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if 'Hello' == 'George': pass", {'output': None, 'args': [{'values': {'1': {'value': 'George'}, '0': {'value': 'Hello'}}, 'expression': '{0} == {1}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if x < 10 and 50 < 30: pass", {'output': None, 'args': [{'values': {'0': {'path': 'x'}}, 'expression': '{0} < 10.0 and 50.0 < 30.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if 10 == 10: pass", {'output': None, 'args': [{'values': {}, 'expression': '10.0 == 10.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if ((15 * 2) + 10) / 3 * _c age: pass", {'output': None, 'args': [{'values': {'0': {'path': '_c.age'}}, 'expression': '( ( 15.0 * 2.0 ) + 10.0 ) / 3.0 * {0}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if (_c age > 23) and _c name like '{{_c name}} Eric': pass", {'output': None, 'args': [{'values': {'1': {'right': {'values': {'0': {'path': '_c.name'}}, 'string': '{0} Eric'}, 'method': 'like', 'left': {'path': '_c.name'}}, '0': {'path': '_c.age'}}, 'expression': '( {0} > 23.0 ) and {1}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if _c points >= 10 or _c age <= 50: pass", {'output': None, 'args': [{'values': {'1': {'path': '_c.age'}, '0': {'path': '_c.points'}}, 'expression': '{0} >= 10.0 or {1} <= 50.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if cart contains cheezy: pass", {'output': None, 'args': [{'right': {'path': 'cart'}, 'method': 'contains', 'left': {'path': 'cheezy'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if s in 'Hello world!': pass", {'output': None, 'args': [{'right': {'value': 'Hello world!'}, 'method': 'contains', 'left': {'path': 's'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if not s: pass", {"output": None, "args": [{"right": True, "method": "isnot", "left": {"path": "s"} } ], "method": "if", "parent": None, "kwargs": None , 'linenum': '1'}),
          ("if 'Hello world!' contains s: pass", {'output': None, 'args': [{'right': {'value': 'Hello world!'}, 'method': 'contains', 'left': {'path': 's'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to store with highest order totals for "2014"', {'output': None, 'args': ['x', {'figure': 'order', 'agg': 'count', 'limit': 1, 'sortby': 'totals', 'time': {'value': '2014'}, 'path': 'totals', 'groupby': 'store', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the number of orders for "this week"', {'output': None, 'args': ['x', {'path': 'count', 'limit': 1, 'figure': 'orders', 'time': {'value': 'this week'}}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to sum of products sold for "this week"', {'output': None, 'args': ['x', {'agg': 'sum', 'path': 'sold', 'limit': 1, 'figure': 'products', 'time': {'value': 'this week'}}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('set x to the top 5 stores with most orders for "this week"', {'output': None, 'args': ['x', {'figure': 'stores', 'agg': 'count', 'limit': 5, 'sortby': 'orders', 'time': {'value': 'this week'}, 'path': 'orders', 'groupby': 'stores', 'dir': 'desc'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('with _customer: pass', {'output': None, 'args': [{'path': '_customer'}], 'method': 'with', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("method variable, 'Good morning!'", {'output': None, 'args': [{'path': 'variable'}, {'value': 'Good morning!'}], 'method': 'method', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set val to the average customer points", {'output': None, 'args': ['val', {'agg': 'average', 'path': 'points', 'limit': 1, 'figure': 'customer'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set val to the first products sort by price desc", {'output': None, 'args': ['val', {'dir': 'desc', 'limit': 1, 'sortby': 'price', 'figure': 'products'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set val to the last products sort by price desc", {'output': None, 'args': ['val', {'dir': 'desc', 'limit': -1, 'sortby': 'price', 'figure': 'products'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set val to the bottom 4 products sort by price desc", {'output': None, 'args': ['val', {'dir': 'desc', 'limit': -4, 'sortby': 'price', 'figure': 'products'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("set val to the bottom 4 products where price < 10 sort by price desc", {'output': None, 'args': ['val', {'dir': 'desc', 'where': {'values': {'0': {'path': 'price'}}, 'expression': '{0} < 10.0'}, 'limit': -4, 'sortby': 'price', 'figure': 'products'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if 1 < 2: pass; else: pass", {'output': None, 'args': [{'values': {}, 'expression': '1.0 < 2.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if 1 < 2: pass; else if 1 > 2: pass; else: pass", {'output': None, 'args': [{'values': {}, 'expression': '1.0 < 2.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if 1 < 2: pass; else if 1 > 2: pass; else if 1 > 2: pass; else: pass", {'output': None, 'args': [{'values': {}, 'expression': '1.0 < 2.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("unless 1 < 2: pass; else: pass", {'output': None, 'args': [{'values': {}, 'expression': '1.0 < 2.0'}], 'method': 'unless', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ("if _p in customer.favorites and _p not in cart: pass", {'output': None, 'args': [{'values': {'1': {'right': {'path': '_p'}, 'method': 'excludes', 'left': {'path': 'cart'}}, '0': {'right': {'path': 'customer.favorites'}, 'method': 'contains', 'left': {'path': '_p'}}}, 'expression': '{0} and {1}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('''log "string {{v}} string": --status """: {{a}} string 'string'"string'"string\n\t string {{variable variable}} with quotes \'\'\'string \'\'\'"""''', {'output': None, 'args': [{'values': {'0': {'path': 'v'}}, 'string': 'string {0} string'}], 'method': 'log', 'parent': None, 'kwargs': {'status': {'values': {'1': {'path': 'variable.variable'}, '0': {'path': 'a'}}, 'string': '{0} string \'string\'"string\'"string\n\t\t\t string {1} with quotes \'\'\'string \'\'\''}}, 'linenum': '1'}),
          ("""log '''string {{v}}\\n\\n string'''""", {'output': None, 'args': [{'values': {'0': {'path': 'v'}}, 'string': 'string {0}\\n\\n string'}], 'method': 'log', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('log "...{{value}}..."', {'output': None, 'args': [{'values': {'0': {'path': 'value'}}, 'string': '...{0}...'}], 'method': 'log', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('log \\\n "...{{value}}..."', {'output': None, 'args': [{'values': {'0': {'path': 'value'}}, 'string': '...{0}...'}], 'method': 'log', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          ('method arg, arg as result', {'output': 'result', 'args': [{'path': 'arg'}, {'path': 'arg'}], 'method': 'method', 'parent': None, 'kwargs': None, 'linenum': '1'}),
          # testing tokens work
          ('method ontop', {"output": None, "args": [{"path": "ontop"} ], "method": "method", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('method inventory', {"output": None, "args": [{"path": "inventory"} ], "method": "method", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('method fortune', {"output": None, "args": [{"path": "fortune"} ], "method": "method", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('method as result: --kwarg', {'output': 'result', 'args': None, 'method': 'method', 'parent': None, 'kwargs': {'kwarg': True}, 'linenum': '1'}),
          ('method as result: --kwarg blah', {'output': 'result', 'args': None, 'method': 'method', 'parent': None, 'kwargs': {'kwarg': {'path': 'blah'}}, 'linenum': '1'}),
          ('method as result: --kwarg blah; : --kwarg again', {'output': 'result', 'args': None, 'method': 'method', 'parent': None, 'kwargs': {'kwarg': [{'path': 'blah'}, {'path': 'again'}]}, 'linenum': '1'}),
          ('while 10 > 9: pass', {"output": None, "args": [{"values": {}, "expression": "10.0 > 9.0"} ], "method": "while", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('while x < 2: pass', {"output": None, "args": [{"values": {"0": {"path": "x"} }, "expression": "{0} < 2.0"} ], "method": "while", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('while true as ok: pass', {"output": 'ok', "args": [True ], "method": "while", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('unset apples', {"output": None, "args": ["apples"], "method": "unset", "parent": None, "kwargs": None , 'linenum': '1'}),
          ('while sum of products sold for "this weeek" > 10: pass', {"output": None, "args": [{"values": {"0": {"agg": "sum", "path": "sold", "limit": 1, "figure": "products", "time": {"value": "this weeek"} } }, "expression": "{0} > 10.0"} ], "method": "while", "parent": None, "kwargs": None , 'linenum': '1'}),
          )
    def test(self, (script, expected)):
        print "\033[90m%s\033[0m" % self.expand_script(script)
        result = storyscript.parse(self.expand_script(script+"\n")).json()
        print dumps(result['script'].get('1', {}), indent=2)
        print
        print result['script'].get('1')
        self.assertDictEqual(result['script'].get('1', {}), expected)

    @data(
          ('block menu: try: do this; catch: if true: retry; else: pass; ; else: goto menu', {"11": {"linenum": "11", "output": None, "args": [{"path": "menu"} ], "method": "goto", "parent": "10", "kwargs": None }, "10": {"linenum": "10", "output": None, "args": None, "method": "else", "parent": "1", "kwargs": None }, "1": {"linenum": "1", "output": None, "args": [{"path": "menu"} ], "method": "block", "parent": None, "kwargs": None }, "3": {"linenum": "3", "output": None, "args": [{"path": "this"} ], "method": "do", "parent": "2", "kwargs": None }, "2": {"linenum": "2", "output": None, "args": None, "method": "try", "parent": "1", "kwargs": None }, "5": {"linenum": "5", "output": None, "args": [True ], "method": "if", "parent": "4", "kwargs": None }, "4": {"linenum": "4", "output": None, "args": None, "method": "catch", "parent": "1", "kwargs": None }, "7": {"linenum": "7", "output": None, "args": None, "method": "else", "parent": "4", "kwargs": None }, "6": {"linenum": "6", "output": None, "args": None, "method": "retry", "parent": "5", "kwargs": None }, "8": {"linenum": "8", "output": None, "args": None, "method": "pass", "parent": "7", "kwargs": None } } ),
          ('try: pass; catch: pass', {"1": {"linenum": "1", "output": None, "args": None, "method": "try", "parent": None, "kwargs": None }, "3": {"linenum": "3", "output": None, "args": None, "method": "catch", "parent": None, "kwargs": None }, "2": {"linenum": "2", "output": None, "args": None, "method": "pass", "parent": "1", "kwargs": None }, "4": {"linenum": "4", "output": None, "args": None, "method": "pass", "parent": "3", "kwargs": None } }),
          ('if true: pass; else if true: pass', {"1": {"linenum": "1", "output": None, "args": [True ], "method": "if", "parent": None, "kwargs": None }, "3": {"linenum": "3", "output": None, "args": [True ], "method": "elif", "parent": None, "kwargs": None }, "2": {"linenum": "2", "output": None, "args": None, "method": "pass", "parent": "1", "kwargs": None }, "4": {"linenum": "4", "output": None, "args": None, "method": "pass", "parent": "3", "kwargs": None } }),
          ('unless 1=1: pass; else unless 1=0: pass; else: pass', {"1": {"linenum": "1", "output": None, "args": [{"values": {}, "expression": "1.0 == 1.0"} ], "method": "unless", "parent": None, "kwargs": None }, "3": {"linenum": "3", "output": None, "args": [{"values": {}, "expression": "1.0 == 0.0"} ], "method": "unlessif", "parent": None, "kwargs": None }, "2": {"linenum": "2", "output": None, "args": None, "method": "pass", "parent": "1", "kwargs": None }, "5": {"linenum": "5", "output": None, "args": None, "method": "else", "parent": None, "kwargs": None }, "4": {"linenum": "4", "output": None, "args": None, "method": "pass", "parent": "3", "kwargs": None }, "6": {"linenum": "6", "output": None, "args": None, "method": "pass", "parent": "5", "kwargs": None } }),
          )
    def test_full(self, (script, expected)):
        print "\033[90m%s\033[0m" % self.expand_script(script)
        result = storyscript.parse(self.expand_script(script+"\n")).json()
        print dumps(result['script'], indent=2)
        self.assertDictEqual(result['script'], expected)

    @data(("set results to first 6 unique myList prices", SyntaxError),
          ("set results to last 15 unique myList prices", SyntaxError),
          ("set x to last 10 stores where name like 'efe'", SyntaxError),
          ("set x to 'a {{b '", SyntaxError),
          ("set x to 'a", SyntaxError),
          ("if \"a < 10", SyntaxError),
          ('set x to "a {{b "', SyntaxError),
          ("set x to '''a''", SyntaxError),
          ("set x to '''a\n", SyntaxError),
          ("set x to '''{{black-n-white**'''", SyntaxError),
          ('set x to """a""', SyntaxError),
          ('if this; that', SyntaxError),
          ('set x to y sort by z arg', SyntaxError),
          ('set x to sum of w x y z for "1"', SyntaxError)
          )
    def test_errors(self, (script, exception)):
        print "\033[90m%s\033[0m" % self.expand_script(script)
        with self.assertRaisesRegexp(exception, "storyscript Syntax Errors found while compiling"):
            print "\033[92m....\033[0m", storyscript.parse(self.expand_script(script+"\n")).json()

    @data(("begin\n\tif true\npass", [{'text': 'pass', 'message': None, 'lineno': 3, 'offset': 1}]),
          ("wait\n--this", [{'token': 'KWARG', 'lineno': 2, 'value': '--this'}]),
          ("do this\n\t--plus\n\t\t\t\t\thello", [{'token': 'INDENT', 'lineno': 3, 'value': None}]),
          )
    def test_indentation_error(self, (script, error)):
        with self.assertRaisesRegexp(storyscript.ScriptError, "storyscript Syntax Errors found while compiling"):
            try:
                print "\033[90m", script, "\033[0m"
                print storyscript.parse(script).json()
            except storyscript.ScriptError as e:
                self.assertItemsEqual(e.json(), error)
                raise
