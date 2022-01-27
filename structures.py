class Symbols(dict):
    def __init__(self):
        super().__init__()
        self.memory_id = 0
        self.iterators = {}
    
    def add_variable(self, name, f = False):
        #print("add_variable", name)
        #print(self)
        if name in self and f == False:
            raise Exception(f"Ponowna deklaracja {name}")
        self.setdefault(name, Variable(self.memory_id))
        self.memory_id += 1
        #print(self)

    def get_address(self, target):
        if type(target) == str:
            return self.get_variable(target).memory_id
        else:
            return self.get_array_at(target[0], target[1])

    def get_variable(self, name):
        if name in self:
            return self[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise Exception(f"Niezadeklarowana zmienna {name}")
    
    def get_array_at(self, name, index):
        if name in self:
            try:
                return self[name].get_at(index)
            except AttributeError:
                raise Exception(f"Uzycie {name} jako tablicy")
        else:
            raise Exception(f"Niezadeklarowana tablica {name}")
    
    def add_array(self, name, begin, end):
        if name in self:
            raise Exception(f"Ponowna deklaracja of {name}")
        elif begin > end:
            raise Exception(f"Zle parametry tablicy {name}")
        self.setdefault(name, Array(name, self.memory_id, begin, end))
        self.memory_id += (end - begin) + 1

        
class Variable:
    def __init__(self, memory_id):
        self.memory_id = memory_id
        self.initialized = False
    def __repr__(self):
        return f"{'Za' if not self.initialized else 'i'}nicjowana zmienna w komorce pamieci {self.memory_id}"

class Array:
    def __init__(self, name, memory_id, first_index, last_index):
        self.name = name
        self.memory_id = memory_id
        self.first_index = first_index
        self.last_index = last_index
    
    def __repr__(self):
        return f"[{self.memory_id}, {self.first_index}:{self.last_index}]"

    def get_at(self, index):
        if self.first_index <= index <= self.last_index:
            return self.memory_id + index - self.first_index
        else:
            raise Exception(f"Indeks {index} poza zakresem tablicy {self.name}")


