# Documentation

> StoryScript is a language designed to orchestrate micro-services in a algorithmic program.


### Principles
> Inspired by [Zen of Python](https://en.wikipedia.org/wiki/Zen_of_Python)

1. Readability first.
1. Less is more.
1. Simple is better than complex.
1. Sparse is better than dense.
1. Transparency is better than secrecy.
1. Simple enough for your mother to understand it.

The goal is to write high-level logic into a **StoryScript** which orchestrates containers. These containers (typically micro-services or functions) execute low-level functions passing the output back into the Story.

- [Syntax](#syntax)
  - [Functions](#functions)
  - [Run Microservice](#run-microservice)
  - [Strings](#strings)
  - [Arrays](#arrays)
  - [Objects](#objects)
  - [Comments](#comments)
  - [Context Variables](#context-variables)
  - [If, Else, Unless, and Conditional Assignment](#if-else-unless-and-conditional-assignment)
  - [Loops and Comprehensions](#loops-and-comprehensions)
  - [Array Slicing and Splicing with Ranges](#array-slicing-and-splicing-with-ranges)
  - [Operations and Aliases](#operations-and-aliases)
  - [Comparisons Order and Grouping](#comparisons-order-and-grouping)
- [Features](#features)
- [Variable Assumptions](#variable-assumptions)
- [Deriving Contextual Variables](#deriving-contextual-variables)
- [Object and Array Searching](#object-and-array-searching)

## Syntax

### Functions
There is **no function syntax** in StoryScript. Functions create abstraction and complexity.
Create a micro-service that executes your functions.

### Run Microservice
The primary purpose of the StoryScript is to execute containers that act as microservices.

```sh
run owner/repo arg1 arg2
```

The command above will pull the container `owner/repo` from a registry (default Docker).
Arguments after the container name are the equivalent of running `docker run owner/repo arg1 arg2`.

The output from the container is assigned to a special keywords.

```
email arg1 arg2
```
The command `email` is an alias for `run asyncy/service_email`.
Aliases are for readability and may be define in a [Table of Contents](#) of your repository.

### Strings

StoryScript supports strings as delimited by the `"` or `'` characters.
To set a variable there are multiple acceptable aliases to readability: `is`, `=`, `equals`, `are`, `set X to Y`.
All the following are equivalent in their outcome.

```py
color is "blue"
color = 'blue'
set color = "blue"
set color to "blue"
color equals "blue"
color are "blue"
```

String may have placeholders. Placeholders do not get rendered until the string is used.
```py
message = "Cast: {spell}"
spell = 'alohomora'
# at this time {spell} does NOT get replaced with alohomora.
print message
>>> "Cast: alohomora"

# let's adjust the variable spell
spell = 'accio'
print message
>>> "Cast: accio"
```

Multiline strings are allowed. The statement is stripped of whitespace and joined with new line characters.

```sh
set dialog to "
  Greetings {author},

  What day do classes resume next semester?

  Wishes,
  Harry
"
```

The long string above results in the following:

```hbs
Greetings {author},

What day do classes resume next semester?

Wishes,
Harry
```
> Notice how the tabs/spaces are reduced.

### Integers and Floats

Same concepts outlined in [strings](#string) above, but with integers and floating point numbers.

```rb
size is 25
weight = 15.21
```

### Arrays

Define a list simply by appending a list of values delimited by a single comma.

```py
colors are "red", "green", "blue"
a is 1
b is "Hello"
c equals {Jagger: "Rock", Elvis: "Roll"}

mixed_list is a, b, c, colors
print mixed_list
>>> [1, "Hello", {"Jagger": "Rock", "Elvis": "Roll"}, ["red", "green", "blue"]]
```
> Brackets and commas are optional.

Multiline lists are acceptable too. Each item is a new line.

```coffee
count = [
  1
  2
  3
]
```

Accessing array values is by brackets, periods and keywords.
**Important** using list indexes will access a lists items in `[0, 1, ...]` notation.
When using keywords the words are literal and the list items are retrieved in `[first, second, ...]` notation.

```py
colors are "red", "green", "blue"
print colors[0], colors.2, second color
>>> "red", "blue", "green"
```

### Objects

Objects are defined in a `json` format.

```coffee
fruits =
  apple:
    color: "red"
  kiwi:
    color: "green"

print fruits.apple.color
>>> "red"
```
> See [Object Searching](#object-searching) to quickly find object details.

### Comments

In StoryScript, comments are denoted by the `#` character to the end of a line, or from `###` to the next appearance of `###`. Comments are ignored by the compiler.

```coffee
# Inline comment

###
Multiline Comment
###

apple = "red"  # just a color
```

### Context Variables

In StoryScript you may want to use a variable in the context of preceding operation. The keyword for setting a new context is `with` or `using`.

```py
kids = [
  {name: "Max", age: 11}
  {name: "Ida", age: 9}
]
with the first kids
  print name
>>> "Max"
```

### If, Else, Unless, and Conditional Assignment

`if` / `else` statements can be written without the use of parentheses and curly brackets. As with functions and other block expressions, multi-line conditionals are delimited by indentation.

```coffee

if happy and knowsIt
  run clapsHands
  run chaChaCha
else
  run showIt

date = if friday then sue else jill

if this
  ...
else if this
  ...
else
  ...

unless this
  ...
```

### Loops and Comprehensions

Looping through a list or object is done by `for` loops.
`for each` and `for every` are acceptable aliases.

```py
for kid in children
  ...

for each colors
  print color  # the "color" value is assumed by the variable "colors"
```

`While` loops are behave like many popular software languages. It's an infinite loop that stops when the associated condition is false.

```py
while var1 equals 10
  ...
```

### Array Slicing and Splicing with Ranges

```py
colors are "red", "green", "blue", "yellow", "purple"
print colors[..2]
>>> "red", "green"
print colors[2..4]
>>> "blue", "yellow"
print colors[-1]
>>> "purple"
print colors[-2..]
>>> "yellow", "purple"
```

### Operations and Aliases

Because the `==` operator frequently causes undesirable coercion, is intransitive, and has a different meaning than in other languages. Other keyword alias apply: `equals`, `is`, `isnt`, `not equal`, and `doesnt equal`.

Instead of a newline or semicolon, `then` can be used to separate conditions from expressions, in `while`, `if`/`else`, and `when` statements.

As in YAML, `on` and `yes` are the same as boolean `true`, while `off` and `no` are boolean `false`.

For comparing numbers you may use keywords such as `greater than`, `less than`, and `less than or equal to`.

`unless` can be used as the inverse of `if`.

### Comparisons Order and Grouping

You may use parentheses to chain comparisons.

```py
if (a > 1 and b > 1) or color is "blue"
   ...
```


## Features
StoryScript includes a number of features that are consolidated operations into simple logic or help the readability of the StoryScript.

### Variable Assumptions
The naming of variables are typically nouns. Nouns are plural or singular.

```py
colors are "red", "green", "blue"
for every colors
  print color
>>> "red"
>>> "green"
>>> "blue"
```

As seen above, the variable `color` is derived from the word `colors` in it's singular form.

### Deriving Contextual Variables
The StoryScript can make assumptions on variable references when not explicitly defined.

```py
after customer-signup
  if customer.twitter
    tweet "@{customer.twitter} thanks for signing up. You are cool!"
```
The object `customer` is derive from the result of `after signup` which, when triggered, is passed information to use in the StoryScript.

```py
{"customer": {...}}
```

### Object and Array Searching

Objects can be quickly searched.

```py
kids = [
  {name: "Max", age: 11}
  {name: "Ida", age: 9}
]

find child in kids where name equals "Max"
print child.age
>>> 11
```
