from storyscript.compiler.semantics.functions.MutationBuilder import \
    mutation_builder

mutations = """
List[A] length -> int
List[A] append item:A -> List[A]
List[A] prepend item:A -> List[A]
List[A] random -> A
List[A] reverse -> List[A]
List[A] sort -> List[A]
List[A] min -> A
List[A] max -> A
List[A] sum -> A
List[A] contains item:A -> boolean
List[A] unique -> List[A]
List[A] remove item:A -> A
List[A] index of:A -> int
List[A] replace item:A by:A -> List[A]

Map[K,V] length -> int
Map[K,V] keys -> List[K]
Map[K,V] values -> List[V]
Map[K,V] pop key:K -> V
Map[K,V] flatten -> List[List[any]]
Map[K,V] contains key:K -> boolean
Map[K,V] contains value:V -> boolean
Map[K,V] get key:K default:V -> V

string length -> int
string replace item:string by:string -> string
string replace pattern:regexp by:string -> string
string contains pattern:regexp -> boolean
string contains item:string -> boolean
string split by:string -> List[string]
string uppercase -> string
string lowercase -> string
string capitalize -> string
string trim -> string
string startswith prefix:string -> boolean
string endswith suffix:string -> boolean
string substring start:int -> string
string substring start:int end:int -> string
string substring end:int -> string

int is_odd -> boolean
int is_even -> boolean
int absolute -> int
int increment -> int
int decrement -> int

float round -> int
float ceil -> int
float floor -> int
float sin -> float
float cos -> float
float tan -> float
float asin -> float
float acos -> float
float atan -> float
float log -> float
float log2 -> float
float log10 -> float
float exp -> float
float abs -> float
float is_nan -> boolean
float is_infinity -> boolean
# approx_equal?
float sqrt -> float
"""


class Hub:
    """
    A representation of a Storyscript Engine and Hub.
    Assumed to be Asyncy Engine for now.
    """
    def __init__(self):
        self._mutations = []
        for m in mutations.split('\n'):
            if len(m.strip()) == 0 or m.startswith('#'):
                continue
            self._mutations.append(mutation_builder(m))

    def mutations(self):
        """
        Return all mutations supported by this hub.
        """
        return self._mutations


hub = Hub()
