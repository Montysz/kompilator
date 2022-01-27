from structures import Variable

class Code:
    def __init__(self, commands, symbols):
        self.commands = commands
        self.symbols = symbols
        self.code = []
        self.iterators = []
        self.for_counter = 0

    def generate_code(self):
        self.make(self.commands)
        self.code.append("HALT")

    def make(self, commands):
        #print("comm", commands)
        #print(type(commands))
          
        for command in commands:
            #print("command[0]", command[0])
            if command[0] == "read":
                target = command[1]
                register = 'a'
                register1 = 'b'
                if type(target) == tuple:
                    if target[0] == "undeclared":
                        if target[1] in self.symbols.iterators:
                            raise Exception(f"READ iterator {target[1]} error")
                        else:
                            raise Exception(
                                f"READ niezadeklarowana zmienna {target[1]}")
                    elif target[0] == "array":
                        self.load_array_address_at(
                            target[1], target[2], register, register1)
                else:
                    self.var_address(target, register)
                    self.symbols[target].initialized = True
                self.code.append(f"SWAP e")
                self.code.append(f"GET")
                self.code.append(f"STORE e")

            
            elif command[0] == "write":
                #self.code.append("(WRITE)")
                value = command[1]
                register = 'a'
                register1 = 'b'
                if value[0] == "load":
                    if type(value[1]) == tuple:
                        if value[1][0] == "undeclared":
                            var = value[1][1]
                            self.var_address(
                                var, register, declared=False)
                            self.code.append(f"LOAD {register}")
                            self.code.append("PUT")
                        elif value[1][0] == "array":
                            self.load_array_address_at(
                                value[1][1], value[1][2], register, register1)
                            self.code.append(f"LOAD {register}")
                            self.code.append("PUT")

                    else:
                        if self.symbols[value[1]].initialized or value[1] in self.iterators:
                            self.var_address(value[1], register1)
                            self.code.append(f"LOAD {register1}")
                            self.code.append("PUT")

                        else:
                            raise Exception(
                                f"Uzycie niezainicjowanej zmiennej {value[1]}")
                elif value[0] == "const":
                        #print("address", address)
                        #print("WRITE")
       
                        self.const_make(value[1], register)
                        self.code.append(f"PUT")
                        #self.code.append("RESET a")

            elif command[0] == "assign":
                #print("make assign")
                self.exp_make(command[2])
                
                #if command[2][0] == 'mul':
                #    self.code.append("SWAP b")
                #    self.code.append("PUT")
                #    self.code.append("SWAP c")
                #    self.code.append("SWAP f")

                
                if type(command[1]) == tuple:
                    #print("ASIGN ARRAY")
                    if command[1][0] == "undeclared":
                        if command[1][1] in self.iterators:
                            raise Exception( f"Przypisanie do iteratora{command[1][1]}")
                        else:
                            raise Exception( f"Przypisanie do niezadeklarowanej zmiennej {command[1][1]}")
                    elif command[1][0] == "array":


                        self.code.append("RESET d")
                        self.code.append("SWAP d")
                        self.load_array_address_at(
                            command[1][1], command[1][2], 'b', 'c')
                        
                        self.code.append("SWAP b")
                        self.code.append("SWAP d")
                        #self.code.append("PUT")

                else:
                    if type(self.symbols[command[1]]) == Variable:
                        #print("assign to Variable")
                        self.var_address(command[1], 'b')
                        self.symbols[command[1]].initialized = True
                    else:
                        raise Exception(f"Przypisanie do tablicy {command[1]} z zlym indeksem")
                
                #if command[2][0] == 'mul':

                #    self.code.append("SWAP f")
                #    self.code.append("PUT")
                
                self.code.append(f"STORE {'b'}")
                
                #self.code.append(f"PUT")

            elif command[0] == "if":
                start_if = len(self.code)
                #print("command", command)
                self.condition(command[1])
                start = len(self.code)

                self.make(command[2])

                for i in range(start_if,len(self.code)):
                    ##print(self.code[i])
                    if self.code[i] == "JUMP finish":
                        #print("finish = ",str(len(self.code) - start + 1))
                        self.code[i]= str("JUMP ")+  str(len(self.code) - start + 1)
                    if self.code[i] == "JZERO finish":
                        #print("finish = ",str(len(self.code) - start + 1))
                        self.code[i]= str("JZERO ")+  str(len(self.code) - start + 1)

            elif command[0] == "ifelse":
                start_if = len(self.code)
                #print("command", command)
                self.condition(command[1])
                start = len(self.code)

                self.make(command[2])
                self.code.append(f"JUMP efinish")

                for i in range(start_if,len(self.code)):
                    ##print(self.code[i])
                    if self.code[i] == "JUMP finish":
                        #print("finish = ",str(len(self.code) - start + 1))
                        self.code[i]= str("JUMP ")+  str(len(self.code) - start + 1)
                    if self.code[i] == "JZERO finish":
                        #print("finish = ",str(len(self.code) - start + 1))
                        self.code[i]= str("JZERO ")+  str(len(self.code) - start + 1)
                
                start = len(self.code)

                self.make(command[3])

                for i in range(len(self.code)):
                    ##print(self.code[i])
                    if self.code[i] == "JUMP efinish":
                        #print("efinish = ",str(len(self.code) - start + 1))
                        self.code[i]= str("JUMP ")+  str(len(self.code) - start + 1)
            
            elif command[0] == "forup":
                #print("comm", command)
                self.iterators.append(command[1][0])
                self.exp_make(command[3], "a")
                self.code.append("RESET b")
                self.code.append("SWAP b")
                self.for_counter = self.for_counter + 1
                fc = self.for_counter
                self.const_make((abs(self.for_counter * 1024)))
                self.code.append("SWAP b")
                self.code.append("STORE b")
                self.code.append("RESET b")

                #f for counter
                if not str(command[2][1]).isdigit():
                    address = self.symbols.get_address(command[1])
                    #print(address)
                    
                    self.code.append("RESET a")
                    for i in range(address):
                        self.code.append("INC a")
                    self.code.append("RESET b")
                    self.code.append("SWAP b")
                    self.exp_make(command[2], 'a')
                    self.code.append("DEC a")
                    self.code.append("STORE b")
                else:
                    i_counter = int(command[2][1]) - 1
                    maker = tuple(((tuple((('assign'),(command[1]),(command[2][0],i_counter))),(command[1]),(command[2]))))
                    #print("MAKER", maker)
                    #print(type(maker))
                    self.make(maker)
                    
                srt = len(self.code)
                #self.code.append("RESET a")
                #self.code.append("ADD f")
                #self.code.append("JNEG doKOnca")
                #self.make(command[4])
                #self.code.append("DEC f")
                self.code.append("RESET h")
                self.code.append("RESET a")
                self.const_make((abs(self.for_counter * 1024)))
                self.code.append("LOAD a")
                self.code.append("SWAP h")
                
                address = self.symbols.get_address(command[1])
                #print(address)
                
                self.code.append("RESET a")
                for i in range(address):
                    self.code.append("INC a")
                self.code.append("RESET b")
                self.code.append("SWAP b")
                self.code.append("LOAD b")
                self.code.append("INC a")
                self.code.append("STORE b")

                self.code.append("SUB h")

                srt2 = len(self.code)
                self.code.append("JPOS doKOnca")
                self.make(command[4])

                self.code.append("RESET a")
                self.code.append("RESET b")

                self.code.append("JUMP -"+str(len(self.code) -srt))
                ent = len(self.code)
                for i in range(srt, ent):
                    if self.code[i] == "JPOS doKOnca":
                        self.code[i] = "JPOS "+str((ent - srt2))

            elif command[0] == "fordown":
                #print("comm", command)
                self.iterators.append(command[1][0])
                
                self.exp_make(command[3])
                self.code.append("RESET b")
                self.code.append("SWAP b")
                self.for_counter = self.for_counter + 1
                fc = self.for_counter
                self.const_make((self.for_counter * 1024))
                self.code.append("SWAP b")
                self.code.append("STORE b")
                self.code.append("RESET b")

                #f for counter
                if not str(command[2][1]).isdigit():
                    address = self.symbols.get_address(command[1])
                    #print(address)
                    
                    self.code.append("RESET a")
                    for i in range(address):
                        self.code.append("INC a")
                    self.code.append("RESET b")
                    self.code.append("SWAP b")
                    self.exp_make(command[2], 'a')
                    #self.code.append("PUT")
                    self.code.append("INC a")
                    self.code.append("STORE b")
                else:
                    i_counter = int(command[2][1]) + 1
                    ##print("i_counter = int(command[2][1]) - 1", i_counter = int(command[2][1]) - 1)
                    maker = tuple(((tuple((('assign'),(command[1]),(command[2][0],i_counter))),(command[1]),(command[2]))))
                    #print("MAKER", maker)
                    #print(type(maker))
                    self.make(maker)
                    
                srt = len(self.code)
                #self.code.append("RESET a")
                #self.code.append("ADD f")
                #self.code.append("JNEG doKOnca")
                #self.make(command[4])
                #self.code.append("DEC f")
                self.code.append("RESET h")
                self.code.append("RESET a")
                self.const_make((fc* 1024))
                self.code.append("LOAD a")
                self.code.append("SWAP h")
                address = self.symbols.get_address(command[1])
                #print(address)
                
                self.code.append("RESET a")
                for i in range(address):
                    self.code.append("INC a")
                self.code.append("RESET b")
                self.code.append("SWAP b")
                self.code.append("LOAD b")
                self.code.append("DEC a")
                self.code.append("STORE b")

                self.code.append("SUB h")

                srt2 = len(self.code)
                self.code.append("JNEG doKOnca")
                self.make(command[4])

                self.code.append("RESET a")
                self.code.append("RESET b")

                self.code.append("JUMP -"+str(len(self.code) -srt))
                ent = len(self.code)
                for i in range(srt, ent):
                    if self.code[i] == "JNEG doKOnca":
                        self.code[i] = "JNEG "+str((ent - srt2))
            
            elif command[0] == "while":
                #self.code.append("(while)")
                startwhile = len(self.code)
                #print("command", command[1])
                self.condition(command[1])
                start = len(self.code)

                self.make(command[2])
                for i in range(startwhile, len(self.code)):
                    ##print(self.code[i])
                    if self.code[i] == "JUMP finish":
                        #print("finish = ",str(len(self.code) - start + 2))
                        self.code[i]= str("JUMP ")+  str(len(self.code) - start + 2)
                    if self.code[i] == "JZERO finish":
                        #print("finish = ",str(len(self.code) - start + 2))
                        self.code[i]= str("JZERO ")+  str( ((len(self.code) - start + 2)) )
                self.code.append(("JUMP -" + str(len(self.code) - startwhile+ 1)))
            
            elif command[0] == "until":
                #self.code.append("(until)")
                self.make(command[2])
                startuntil = len(self.code)
                #print("command", command[1])
                #print("dffd",command[1][0])
                
                if command[1][0] == "eq":
                    c = "neq"
                
                elif command[1][0] == "neq":
                    c = "eq"
                
                elif command[1][0] == "leq":
                    c= "geq"
                
                elif command[1][0] == "geq":
                    c= "leq"
                
                elif command[1][0] == "le":
                    c= "ge"
               
                elif command[1][0] == "ge":
                    c= "le"
                
                cond = (c,command[1][1],command[1][2] )
                #print("COND",cond)
                self.condition(cond)
                start = len(self.code)

                self.make(command[2])
                for i in range(startuntil, len(self.code)):
                    ##print(self.code[i])
                    if self.code[i] == "JUMP finish":
                        #print("finish = ",str(len(self.code) - start + 2))
                        self.code[i]= str("JUMP ")+  str(len(self.code) - start + 2)
                    if self.code[i] == "JZERO finish":
                        #print("finish = ",str(len(self.code) - start + 2))
                        self.code[i]= str("JZERO ")+  str(len(self.code) - start + 2)
                self.code.append(("JUMP -" + str(len(self.code) - startuntil+ 1)))               

    def exp_make(self, 
                            expression, 
                            target_reg='a', 
                            ):
        #print("exp", expression)
        
        if expression[0] == "const":
            #self.code.append("SWAP a")
            self.const_make(expression[1], 'a')
            #self.code.append("SWAP a")

        elif expression[0] == "load":
            if type(expression[1]) == tuple:
                if expression[1][0] == "undeclared":
                    self.var_load(expression[1][1], target_reg, declared=False)
                elif expression[1][0] == "array":
                    self.load_array_at(expression[1][1], expression[1][2], 'a', 'e')
                    #self.code.append("PUT")
            else:
                if self.symbols[expression[1]].initialized or expression[1] in self.iterators:
                    self.var_load(expression[1], target_reg)
                else:
                    raise Exception(f"Uzycie niezainicjowanej zmiennej {expression[1]}")

        elif expression[0] == "add": 
            #print(expression)

            if expression[1][0] == expression[2][0] == "const":
                self.const_make(expression[1][1] + expression[2][1], 'a')

            else:
                self.exp_make(expression[2])
                self.code.append("RESET c")
                self.code.append("SWAP c")
                self.exp_make(expression[1])
                self.code.append("ADD c")

        elif expression[0] == "sub": 
            #print("sub", expression)    
            if expression[1][0] == expression[2][0] == "const":
                #print("sub-const", expression[1][0])
                self.const_make(expression[1][1] - expression[2][1], 'a')
            else:
                self.exp_make(expression[2])
                self.code.append("RESET b")
                self.code.append("SWAP b")
                self.exp_make(expression[1])
                self.code.append("SUB b")
                
        elif expression[0] == "mul1":
            negative1 = False
            negative2 = False
            negative = False
            if expression[1][0] == expression[2][0] == "const":
                self.const_make(expression[1][1] * expression[2][1], target_reg)
                
            else:
                self.code.append("RESET a") 
                self.code.append("RESET b") 
                self.code.append("RESET c") 
                self.exp_make(expression[1], 'a')
                s0 = len(self.code)
                self.code.append("JZERO 1")
                self.code.append("JPOS 4")
                self.code.append("SWAP b")
                self.code.append("SUB b")
                self.code.append("RESET b")
                self.code.append("SWAP c") 
                self.exp_make(expression[2], 'a')
                s1 = len(self.code)
                self.code.append("JZERO 1")
                self.code.append("JPOS 4")
                self.code.append("SWAP b")
                self.code.append("SUB b")
                self.code.append("RESET b")
                self.code.append("SUB c")
                start = len(self.code)
                #self.code.append("PUT")
                self.code.append("JPOS koniec")



               
                self.code.append("RESET c") 
                self.exp_make(expression[1], 'a')
                self.code.append("JNEG 3")
                self.code.append("INC c")
                self.code.append("JUMP 2")
                self.code.append("DEC c")
                self.exp_make(expression[2], 'a')
                self.code.append("JPOS 8")
                #SECOND NEG
                self.code.append("SWAP c")
                self.code.append("JPOS 4")
                self.code.append("SWAP c")
                self.code.append("INC c")
                self.code.append("JUMP 4")
                self.code.append("SWAP c")
                self.code.append("DEC c")
                self.code.append("DEC c")
                self.code.append("JUMP 8")
                #SECOND POS
                self.code.append("SWAP c")
                self.code.append("JPOS 5")
                self.code.append("SWAP c")
                self.code.append("DEC c")
                self.code.append("DEC c")
                self.code.append("JUMP 2")
                self.code.append("SWAP c")
                

                #FLAG
                #self.code.append("SWAP c")
                #self.code.append("PUT")
                #self.code.append("SWAP c")

            
                #both pos
                self.code.append("RESET a")                   
                self.code.append("RESET b")                   
                #self.code.append("RESET c") 
                self.code.append("RESET d")                   
                self.code.append("RESET e")                   
                self.code.append("RESET f") 
                #find log
                self.exp_make(expression[2], 'a')

                self.code.append("JPOS 4")
                self.code.append("SWAP b")
                self.code.append("SUB b")
                self.code.append("RESET b")
                #self.code.append("PUT")

                self.code.append("SWAP e")
                #first number in e
                self.code.append("INC d")
                self.code.append("RESET a") 
                self.code.append("INC a")
                self.code.append("SHIFT d")
                self.code.append("SUB e")
                self.code.append("JPOS 2")
                self.code.append("JUMP -6")    
                self.code.append("ADD e")
                self.code.append("DEC a")
                self.code.append("DEC d")

                #self.code.append("SWAP d")
                #self.code.append("PUT")
                #self.code.append("SWAP d")
                #log in d
                self.code.append("RESET a")
                self.code.append("INC a")
                self.code.append("SHIFT d")
                #self.code.append("PUT")
                self.code.append("SWAP f")
        

                #2^d in f
                self.code.append("ADD e")
                self.code.append("SUB f")
                self.code.append("RESET f")
                #self.code.append("PUT")
                self.code.append("SWAP f")
                
                #e - f in f
                self.exp_make(expression[1], 'a')
                #self.code.append("PUT")
                self.code.append("JPOS 4")
                self.code.append("RESET e")            
                self.code.append("SWAP e")
                self.code.append("SUB e")
                self.code.append("RESET e")
                self.code.append("SWAP e")
                
                self.code.append("ADD e")
                #self.code.append("PUT")
                self.code.append("SHIFT d")
                #self.code.append("PUT")
                self.code.append("SWAP b")
                #second number in e
                self.code.append("SWAP f")
                #self.code.append("PUT")
                self.code.append("JZERO 10")#to ADD b
                self.code.append("SWAP f")


                self.code.append("RESET a")
                self.code.append("DEC f")
                self.code.append("ADD e")
                self.code.append("SWAP f")
                self.code.append("JZERO 3")
                self.code.append("SWAP f")
                self.code.append("JUMP -5")
                #self.code.append("PUT")
                self.code.append("SWAP f")
                #self.code.append("PUT")
                self.code.append("ADD b")

                #check flag
                self.code.append("SWAP c")
                self.code.append("JZERO 4")
                self.code.append("RESET a")
                self.code.append("SUB c")
                self.code.append("JUMP 2")
                self.code.append("SWAP c")
                start2 = len(self.code)
                self.code.append("JUMP koniec2")
                koniec = len(self.code)
                for i in range(start, koniec):
                    if self.code[i] == "JPOS koniec":
                        self.code[i] = "JPOS "+ str(koniec - start)
                
                self.code.append("RESET c") 
                self.exp_make(expression[1], 'a')
                self.code.append("JNEG 3")
                self.code.append("INC c")
                self.code.append("JUMP 2")
                self.code.append("DEC c")
                self.exp_make(expression[2], 'a')
                self.code.append("JPOS 8")
                #SECOND NEG
                self.code.append("SWAP c")
                self.code.append("JPOS 4")
                self.code.append("SWAP c")
                self.code.append("INC c")
                self.code.append("JUMP 4")
                self.code.append("SWAP c")
                self.code.append("DEC c")
                self.code.append("DEC c")
                self.code.append("JUMP 8")
                #SECOND POS
                self.code.append("SWAP c")
                self.code.append("JPOS 5")
                self.code.append("SWAP c")
                self.code.append("DEC c")
                self.code.append("DEC c")
                self.code.append("JUMP 2")
                self.code.append("SWAP c")
                

                #FLAG
                #self.code.append("SWAP c")
                #self.code.append("PUT")
                #self.code.append("SWAP c")

            
                #both pos
                self.code.append("RESET a")                   
                self.code.append("RESET b")                   
                #self.code.append("RESET c") 
                self.code.append("RESET d")                   
                self.code.append("RESET e")                   
                self.code.append("RESET f") 
                #find log
                self.exp_make(expression[1], 'a')

                self.code.append("JPOS 4")
                self.code.append("SWAP b")
                self.code.append("SUB b")
                self.code.append("RESET b")
                #self.code.append("PUT")

                self.code.append("SWAP e")
                #first number in e
                self.code.append("INC d")
                self.code.append("RESET a") 
                self.code.append("INC a")
                self.code.append("SHIFT d")
                self.code.append("SUB e")
                self.code.append("JPOS 2")
                self.code.append("JUMP -6")    
                self.code.append("ADD e")
                self.code.append("DEC a")
                self.code.append("DEC d")

                #self.code.append("SWAP d")
                #self.code.append("PUT")
                #self.code.append("SWAP d")
                #log in d
                self.code.append("RESET a")
                self.code.append("INC a")
                self.code.append("SHIFT d")
                #self.code.append("PUT")
                self.code.append("SWAP f")
        

                #2^d in f
                self.code.append("ADD e")
                self.code.append("SUB f")
                self.code.append("RESET f")
                #self.code.append("PUT")
                self.code.append("SWAP f")
                
                #e - f in f
                self.exp_make(expression[2], 'a')
                #self.code.append("PUT")
                self.code.append("JPOS 4")
                self.code.append("RESET e")            
                self.code.append("SWAP e")
                self.code.append("SUB e")
                self.code.append("RESET e")
                self.code.append("SWAP e")
                
                self.code.append("ADD e")
                #self.code.append("PUT")
                self.code.append("SHIFT d")
                #self.code.append("PUT")
                self.code.append("SWAP b")
                #second number in e
                self.code.append("SWAP f")
                #self.code.append("PUT")
                self.code.append("JZERO 10")#to ADD b
                self.code.append("SWAP f")


                self.code.append("RESET a")
                self.code.append("DEC f")
                self.code.append("ADD e")
                self.code.append("SWAP f")
                self.code.append("JZERO 3")
                self.code.append("SWAP f")
                self.code.append("JUMP -5")
                #self.code.append("PUT")
                self.code.append("SWAP f")
                #self.code.append("PUT")
                self.code.append("ADD b")

                #check flag
                self.code.append("SWAP c")
                self.code.append("JZERO 4")
                self.code.append("RESET a")
                self.code.append("SUB c")
                self.code.append("JUMP 2")
                self.code.append("SWAP c")
                koniec2 = len(self.code)
                for i in range(start2, koniec2):
                    if self.code[i] == "JUMP koniec2":
                        self.code[i] = "JUMP "+ str(koniec2 - start2)
                k0 = len(self.code)
                self.code[s0] = "JZERO "+ str(k0 - s0)
                self.code[s1] = "JZERO "+ str(k0 - s1)

        elif expression[0] == "mod":

            self.code.append("RESET a")
            self.code.append("RESET b")
            self.code.append("RESET c")
            self.code.append("RESET d")
            self.code.append("RESET e")
            self.code.append("RESET f")

            self.code.append("RESET h")
            #flag in rg
            self.exp_make(expression[1], 'a')
            s_1 = len(self.code)
            self.code.append("JZERO end1")

            self.code.append("JPOS 6")
            self.code.append("INC d")
            self.code.append("DEC c")
            self.code.append("SWAP b")  
            self.code.append("RESET a")
            self.code.append("SUB b")
            self.code.append("SWAP b") 
            self.code.append("RESET a")   
            #first number in b

            self.exp_make(expression[2], 'a')

            self.code.append("SWAP d")
            self.code.append("SWAP h")
            self.code.append("SWAP d")
            self.code.append("RESET d")


            self.code.append("RESET g")
            self.code.append("SWAP c")
            self.code.append("SWAP g")
            self.code.append("SWAP c")


            s_2 = len(self.code)
            self.code.append("JZERO end2")
            
            self.code.append("JPOS 13")
            self.code.append("DEC h")
            self.code.append("DEC h")
            self.code.append("SWAP c")
            self.code.append("SUB c")

            self.code.append("SWAP g")
            self.code.append("JNEG 3")
            self.code.append("DEC a")
            self.code.append("JUMP 4")
            self.code.append("INC a")
            self.code.append("SWAP g")
            self.code.append("JUMP 2")
            self.code.append("SWAP g")


            self.code.append("SWAP c")   
            #second number in c
            #self.code.append("SWAP g") 
            #self.code.append("PUT") 
            #self.code.append("SWAP g") 

            



        #LOOP:
            start_loop = len(self.code) 
            self.code.append("ADD c")
            #self.code.append("INC d")

            #self.code.append("SWAP d")
            #self.code.append("PUT")
            #self.code.append("SWAP d")

            self.code.append("SHIFT d")
            self.code.append("SWAP f")
            #rf = 2^k*b
            self.code.append("RESET a")
            self.code.append("ADD b")
            self.code.append("SUB f")

            #ra = a - 2^k * b
            k_correct_s = len(self.code)
            self.code.append("JNEG 4")#find(k_+1)")
            
            self.code.append("RESET a")
            self.code.append("INC d")
            to_loop = len(self.code)            
            self.code.append("JUMP "+str(-(to_loop - start_loop)))
            #JNEG find(k_+1)
            
            self.code.append("SWAP d")
            #self.code.append("PUT")
            self.code.append("JZERO 12") 
            self.code.append("DEC a")
            #self.code.append("PUT")
            self.code.append("SWAP d")
            #correct k in d
            
            
            #self.code.append("RESET a")
            #self.code.append("ADD d")

            self.code.append("RESET a")
            self.code.append("INC a")
            self.code.append("SHIFT d")

            self.code.append("ADD e")
            self.code.append("SWAP e")
            self.code.append("RESET a")

            self.code.append("SWAP d")

            self.code.append("JZERO 2") 
            self.code.append("DEC d") 
            #self.code.append("PUT")
            s_last = len(self.code)
            self.code.append("JZERO final")
            self.code.append("SWAP d")

            #jump to find next k
            #self.code.append("SWAP e")
            #self.code.append("PUT")
            #self.code.append("SWAP e")

            self.code.append("RESET a")
            self.code.append("ADD c")

            self.code.append("SHIFT d")
            self.code.append("SWAP b")
            self.code.append("SUB b")
            self.code.append("SWAP b")
            self.code.append("RESET f")
            self.code.append("RESET a")
            #a(rb) = a - 2^k *b

            
            self.code.append("RESET d")
            #self.code.append("INC d")
            
            k_next = len(self.code)
            self.code.append("JUMP "+str(-(k_next - start_loop )))
            final = len(self.code)
            self.code[s_last] = "JZERO " + str(final - s_last)
            self.code.append("SWAP b")
            self.code.append("SUB c")
            self.code.append("JNEG 2")
            self.code.append("JUMP 2")
            self.code.append("ADD c")

            
            self.code.append("SWAP g")
            #self.code.append("PUT")
            
            self.code.append("JZERO 2")
            self.code.append("JUMP 2")
            e = len(self.code)
            self.code.append("JUMP g0")
            
            #g-1
            self.code.append("SWAP h")

            hp = len(self.code)
            self.code.append("JPOS g1h1")
            
            #g1h-2

            #-b-W
            self.code.append("SWAP c")
            self.code.append("SUB g")
            self.code.append("SWAP d")
            self.code.append("RESET a")
            self.code.append("SUB d")


            e1 = len(self.code)
            self.code.append("JUMP end1")
            #g1h1
            g1h1 = len(self.code)
            
            #b-W
            self.code.append("SWAP c")
            self.code.append("SUB g")


            e2 = len(self.code)
            self.code.append("JUMP end2")
            self.code[hp] =  "JPOS " + str(g1h1 - hp)

            #g0
            g0 = len(self.code)
            self.code.append("SWAP h")
            self.code.append("JZERO 2")
            self.code.append("JUMP 3")
            self.code.append("SWAP g")
            g0h0 = len(self.code)
            self.code.append("JUMP end")#g0h0

            

            #g0h-1
            self.code.append("RESET a")
            self.code.append("SUB g")#-W
            self.code.append("JUMP 2")


            end_div = len(self.code)


            self.code.append("RESET a")
            end_div2 = len(self.code)

            self.code[s_1] =  "JZERO " + str(end_div2 - s_1)
            self.code[s_2] =  "JZERO " + str(end_div2 - s_2)

            self.code[e] =  "JUMP " + str(g0 - e)
            self.code[e1] =  "JUMP " + str(end_div2 - e1)
            self.code[e2] =  "JUMP " + str(end_div2 - e2)
            self.code[g0h0] =  "JUMP " + str(end_div2 - g0h0)

        elif expression[0] == "mul":
            self.code.append("RESET a")
            self.code.append("RESET b")
            self.code.append("RESET c")
            self.code.append("RESET d")
            self.code.append("RESET e")
            self.code.append("RESET f")

            #flag in rg
            self.exp_make(expression[1], 'a')
        
            s_1 = len(self.code)
            self.code.append("JZERO end1")

            self.code.append("JPOS 5")
            self.code.append("DEC c")
            self.code.append("SWAP b")  
            self.code.append("RESET a")
            self.code.append("SUB b")
            self.code.append("SWAP b") 
            self.code.append("RESET a")   
            #first number in b
        
            self.exp_make(expression[2], 'a')
            self.code.append("RESET g")
            self.code.append("SWAP c")
            self.code.append("SWAP g")
            self.code.append("SWAP c")

            s_2 = len(self.code)
            
            self.code.append("JZERO end2")
            
            self.code.append("JPOS 11")
            self.code.append("SWAP c")
            self.code.append("SUB c")

            self.code.append("SWAP g")
            self.code.append("JNEG 3")
            self.code.append("DEC a")
            self.code.append("JUMP 4")
            self.code.append("INC a")
            self.code.append("SWAP g")
            self.code.append("JUMP 2")
            self.code.append("SWAP g")

            self.code.append("SUB b")
            self.code.append("JNEG 4")
            self.code.append("ADD b")
            self.code.append("SWAP c")
            self.code.append("JUMP 4")
            self.code.append("ADD b")
            self.code.append("SWAP b")
            self.code.append("SWAP c")



            
            #second number in c
            #self.code.append("SWAP c") 
            #self.code.append("PUT") 
            #self.code.append("SWAP c")

            self.code.append("RESET d")
            self.code.append("RESET e")
            self.code.append("RESET f")

        #LOOP:


        
            start_loop = len(self.code) 
            #self.code.append("ADD c")
            self.code.append("INC a")

            #self.code.append("SWAP d")
            #self.code.append("PUT")
            #self.code.append("SWAP d")

            self.code.append("SHIFT d")
            self.code.append("SWAP f")
            #rf = 2^k
            self.code.append("RESET a")
            self.code.append("ADD b")
            self.code.append("SUB f")
            #ra = a - 2^k
            k_correct_s = len(self.code)
            self.code.append("JNEG 4")#find(k_+1)")
            
            self.code.append("RESET a")
            self.code.append("INC d")
            to_loop = len(self.code)            
            self.code.append("JUMP "+str(-(to_loop - start_loop)))
            #JNEG find(k_+1)
            
            self.code.append("SWAP d")
            #self.code.append("PUT")
            self.code.append("JZERO 12") 
            self.code.append("DEC a")
            self.code.append("SWAP d")
            #correct k in d
            
            
            self.code.append("RESET a")
            self.code.append("ADD c")
            self.code.append("SHIFT d")


            self.code.append("ADD e")
            self.code.append("SWAP e")
            self.code.append("RESET a")

            self.code.append("SWAP d")

            self.code.append("JZERO 2") 
            self.code.append("DEC d") 
            #self.code.append("PUT")
            s_last = len(self.code)
            self.code.append("JZERO final")
            self.code.append("SWAP d")

            #jump to find next k
            #self.code.append("SWAP e")
            #self.code.append("PUT")
            #self.code.append("SWAP e")

            self.code.append("RESET a")
            self.code.append("INC a")

            self.code.append("SHIFT d")
            self.code.append("SWAP b")
            self.code.append("SUB b")
            self.code.append("SWAP b")
            self.code.append("RESET f")
            self.code.append("RESET a")
            #a(rb) = a - 2^k *b

            self.code.append("RESET d")
            #self.code.append("INC d")
            
            k_next = len(self.code)
            self.code.append("JUMP "+str(-(k_next - start_loop )))
            final = len(self.code)
            self.code[s_last] = "JZERO " + str(final - s_last)

    
            
            self.code.append("SWAP e")
            

            self.code.append("SWAP g")
            self.code.append("JZERO 5")
            self.code.append("RESET a")
            self.code.append("SUB g")
            self.code.append("RESET g")
            self.code.append("JUMP 2")
            self.code.append("SWAP g")
            self.code.append("JUMP 2")
            end_div = len(self.code)
            self.code[s_1] =  "JZERO " + str(end_div - s_1)
            self.code[s_2] =  "JZERO " + str(end_div - s_2)

    

            self.code.append("RESET a")
            


        elif expression[0] == "div":
            self.code.append("RESET a")
            self.code.append("RESET b")
            self.code.append("RESET c")
            self.code.append("RESET d")
            self.code.append("RESET e")
            self.code.append("RESET f")

            #flag in rg
            self.exp_make(expression[1], 'a')
            s_1 = len(self.code)
            self.code.append("JZERO end1")

            self.code.append("JPOS 5")
            self.code.append("DEC c")
            self.code.append("SWAP b")  
            self.code.append("RESET a")
            self.code.append("SUB b")
            self.code.append("SWAP b") 
            self.code.append("RESET a")   
            #first number in b

            self.exp_make(expression[2], 'a')
            self.code.append("RESET g")
            self.code.append("SWAP c")
            self.code.append("SWAP g")
            self.code.append("SWAP c")

            s_2 = len(self.code)
            self.code.append("JZERO end2")
            
            self.code.append("JPOS 11")
            self.code.append("SWAP c")
            self.code.append("SUB c")

            self.code.append("SWAP g")
            self.code.append("JNEG 3")
            self.code.append("DEC a")
            self.code.append("JUMP 4")
            self.code.append("INC a")
            self.code.append("SWAP g")
            self.code.append("JUMP 2")
            self.code.append("SWAP g")

            self.code.append("SWAP c")   
            #second number in c
            #self.code.append("SWAP g") 
            #self.code.append("PUT") 
            #self.code.append("SWAP g")
        #LOOP:
            start_loop = len(self.code) 
            self.code.append("ADD c")
            #self.code.append("INC d")

            #self.code.append("SWAP d")
            #self.code.append("PUT")
            #self.code.append("SWAP d")

            self.code.append("SHIFT d")
            self.code.append("SWAP f")
            #rf = 2^k*b
            self.code.append("RESET a")
            self.code.append("ADD b")
            self.code.append("SUB f")

            #ra = a - 2^k * b
            k_correct_s = len(self.code)
            self.code.append("JNEG 4")#find(k_+1)")
            
            self.code.append("RESET a")
            self.code.append("INC d")
            to_loop = len(self.code)            
            self.code.append("JUMP "+str(-(to_loop - start_loop)))
            #JNEG find(k_+1)
            
            self.code.append("SWAP d")
            #self.code.append("PUT")
            self.code.append("JZERO 12") #14
            self.code.append("DEC a")
            #self.code.append("PUT")
            self.code.append("SWAP d")
            #correct k in d
            
            
            #self.code.append("RESET a")
            #self.code.append("ADD d")

            self.code.append("RESET a")
            self.code.append("INC a")
            self.code.append("SHIFT d")

            self.code.append("ADD e")
            self.code.append("SWAP e")
            self.code.append("RESET a")

            self.code.append("SWAP d")

            self.code.append("JZERO 2") 
            self.code.append("DEC d") 
            #self.code.append("PUT")
            s_last = len(self.code)
            self.code.append("JZERO final")
            self.code.append("SWAP d")

            #jump to find next k
            #self.code.append("SWAP e")
            #self.code.append("PUT")
            #self.code.append("SWAP e")

            self.code.append("RESET a")
            self.code.append("ADD c")

            self.code.append("SHIFT d")
            self.code.append("SWAP b")
            self.code.append("SUB b")
            self.code.append("SWAP b")
            self.code.append("RESET f")
            self.code.append("RESET a")
            #a(rb) = a - 2^k *b

            self.code.append("RESET d")
            #self.code.append("INC d")
            
            k_next = len(self.code)
            self.code.append("JUMP "+str(-(k_next - start_loop )))
            final = len(self.code)
            self.code[s_last] = "JZERO " + str(final - s_last)
            self.code.append("SWAP e")
            
            self.code.append("SWAP g")
            self.code.append("JZERO 6")
            self.code.append("RESET a")
            self.code.append("SUB g")
            self.code.append("DEC a")
            self.code.append("RESET g")
            self.code.append("JUMP 2")
            self.code.append("SWAP g")
            self.code.append("JUMP 2")
            end_div = len(self.code)
            self.code[s_1] =  "JZERO " + str(end_div - s_1)
            self.code[s_2] =  "JZERO " + str(end_div - s_2)

    

            self.code.append("RESET a")

        elif expression[0] == "div1":
            #print("div", expression)
            if expression[1][1] == int(0) or expression[2][1] == int(0):
                self.code.append("RESET a")
            elif  expression[2][1] == int(2):
                print("usage")
                self.exp_make(expression[1], 'a')
                self.code.append("RESET b")
                self.code.append("DEC b")
                self.code.append("SHIFT b")

            else:
                self.code.append("RESET a")
                self.code.append("RESET b")
                self.code.append("RESET c")
                self.code.append("RESET d")
                self.code.append("RESET e")
                self.code.append("RESET f")
                
                
                self.exp_make(expression[1], 'a')
                start_div = len(self.code)
                self.code.append(f"JZERO koniec")
                self.exp_make(expression[2], 'a')
                start_div1 = len(self.code)
                self.code.append(f"JZERO koniec1")

                self.exp_make(expression[1], 'a')
                self.code.append("JPOS 4")
                #first negative
                self.code.append("INC d")
                
                self.code.append("SWAP b")
                self.code.append("SUB b")

                self.code.append("SWAP b")

                self.exp_make(expression[2], 'a')
                self.code.append("JPOS 4")
                #second negative
                self.code.append("DEC d")

                self.code.append("SWAP c")
                self.code.append("SUB c")

                self.code.append("SWAP c")

                self.code.append("RESET a")
                self.code.append("SWAP b")
                self.code.append("SUB c")
                self.code.append("INC e")    
                self.code.append("JNEG 3")
                self.code.append("JZERO 3")
                self.code.append("JUMP -4")

                self.code.append("DEC e")

                #positive result
                self.code.append("RESET a")
                self.code.append("SWAP d")
                self.code.append("JZERO 4")

                self.code.append("RESET a")
                self.code.append("SUB e")
                self.code.append("JUMP 4")

                self.code.append("SWAP e")



                koniec_div = len(self.code)
                for i in range(start_div,koniec_div):
                    if self.code[i] == "JZERO koniec":
                        self.code[i] = "JZERO "+str(koniec_div-start_div)
                for i in range(start_div1,koniec_div):
                    if self.code[i] == "JZERO koniec1":
                        self.code[i] = "JZERO "+str(koniec_div-start_div1) 
                     

        elif expression[0] == "mod1":
            if expression[1][1] == int(0) or expression[2][1] == int(0):
                self.code.append("RESET a") 
            self.code.append("RESET a")
            self.code.append("RESET b")
            self.code.append("RESET c")
            self.exp_make(expression[1], 'a')
            self.code.append("SWAP c")
            self.exp_make(expression[2], 'a')
            self.code.append("SUB c")
            exp = (expression[0]+str(1), expression[2], expression[1])
            exp2 = (expression[0]+str(1), expression[1], expression[2])
            s = len(self.code)
            self.code.append("JPOS k")
            self.exp_make(exp2, 'a')
            s1 = len(self.code)
            self.code.append("JUMP k1")
            e = len(self.code)
            for i in range(s,e):
                if self.code[i] == "JPOS k":
                    self.code[i] = "JPOS "+str(e-s)
            #JPOS
            self.exp_make(exp, 'a')
            e1 = len(self.code)
            for i in range(s1,e1):
                if self.code[i] == "JUMP k1":
                    self.code[i] = "JUMP "+str(e1-s1)

        elif expression[0] == "mod2":
            if expression[1][1] == int(0) or expression[2][1] == int(0):
                self.code.append("RESET a")
            if  expression[2][1] == int(2):
                print("usage mod 2")
                self.exp_make(expression[1], 'a')
                self.code.append("RESET c")
                self.code.append("SWAP c")
                self.code.append("ADD c")
                self.code.append("SWAP c")

                self.code.append("RESET b")
                self.code.append("DEC b")
                self.code.append("SHIFT b")
                self.code.append("INC b")
                self.code.append("INC b")
                self.code.append("SHIFT b")
                self.code.append("SUB c")
                #self.code.append("PUT")
                self.code.append("JZERO 4")
                self.code.append("RESET a")
                self.code.append("INC a")
                self.code.append("JUMP 2")
                self.code.append("RESET a")
            
            
            else:               
                self.exp_make(expression[1], 'a')
                start = len(self.code)
                self.code.append("JZERO koniec")
                self.exp_make(expression[2], 'a')
                start1 = len(self.code)
                self.code.append("JZERO koniec1")


                self.code.append("RESET a")
                self.code.append("RESET b")
                self.code.append("RESET c")
                self.code.append("RESET d")
                self.code.append("RESET e")
                self.code.append("RESET f")

                
                self.exp_make(expression[1], 'a')
                self.code.append("JPOS 4")
                #first negative
                self.code.append("INC d")
                
                self.code.append("SWAP b")
                self.code.append("SUB b")

                self.code.append("SWAP b")

                self.exp_make(expression[2], 'a')
                self.code.append("JPOS 4")
                #second negative
                self.code.append("DEC d")

                self.code.append("SWAP c")
                self.code.append("SUB c")

                self.code.append("SWAP c")

                self.code.append("RESET a")
                self.code.append("SWAP b")
                self.code.append("SUB c")
                self.code.append("JZERO 12")
                
                self.code.append("JNEG 2")
                self.code.append("JUMP -3")

                self.code.append("ADD c")
            
                self.code.append("SWAP e")


                #positive result
                self.code.append("RESET a")
                self.code.append("SWAP d")
                self.code.append("JZERO 4")

                self.code.append("RESET a")
                self.code.append("SUB e")
                self.code.append("JUMP 2")
                
                self.code.append("SWAP e")

                koniec = len(self.code)
                for i in range(start,koniec):
                    if self.code[i] == "JZERO koniec":
                        self.code[i] = "JZERO "+str(koniec-start)
                for i in range(start1,koniec):
                    if self.code[i] == "JZERO koniec1":
                        self.code[i] = "JZERO "+str(koniec-start1)

        else:
            print("bad expression")
    


    def const_make_old(self, const, reg='a'):
        #print("conts", const)
        self.code.append(f"RESET {reg}")
        self.code.append("RESET g")
        self.code.append("RESET h")
        #elif const > 0:
        #    for i in range(const):
        #        self.code.append(f"INC {reg}")
                
        if const < 0:
            #print("dec")
            for i in range(abs(const)):
                self.code.append(f"DEC {reg}")


        
        if const > 0:
            for i in range(abs(const)):
                self.code.append(f"INC {reg}")
    def const_make(self, const, reg='a'):
        #self.const_make_old(const, reg='a')
        #print("gen conts", const)
        #print("reg", reg)
        #"""
        self.code.append(f"SWAP {reg}")
        self.code.append(f"RESET g")
        self.code.append(f"RESET h")
        if const > 0:
            bits = (bin(const)[2:])
            bits = bits[::-1]
            #print("bits", bits)
            a = 1
            self.code.append("RESET a")
            self.code.append("INC a")
            for bit in bits[1:]:
                #print("bit", bit)
                self.code.append(f"INC g")
                if bit == '1':
                    #print("jeden", a)
                    self.code.append("SHIFT g")
                    self.code.append("ADD h")
                    self.code.append("SWAP h")
                    self.code.append("RESET a")
                    self.code.append("INC a")   
                a = a + 1   
        
            self.code.append("SWAP h")
            #print(bits, "XD")
            if bits[0] == '1':
                #print("first bit", bits[-1])
                self.code.append(f"INC a")
            self.code.append("RESET g")
            self.code.append("RESET h")
            #self.code.append(f"PUT")
            self.code.append(f"SWAP {reg}")
            if reg != 'a':
                #print("gen const not in reg a")
                self.code.append("RESET a")

        elif const < 0:
            const = abs(const)
            bits = (bin(const)[2:])
            bits = bits[::-1]
            #print("bits", bits)
            a = 1
            self.code.append("RESET a")
            self.code.append("RESET g")
            self.code.append("RESET h")
            self.code.append("INC a")
            for bit in bits[1:]:
                #print("bit", bit)
                if bit == '1':
                    #print("jeden", a)
                    for i in range(a):
                        self.code.append("INC g")
                    self.code.append("SHIFT g")
                    self.code.append("RESET g")
                    self.code.append("ADD h")

                    self.code.append("SWAP h")
                    self.code.append("RESET a")
                    self.code.append("INC a")   
                a = a + 1   
        
            self.code.append("SWAP h")
            #print(bits, "XD")
            if bits[0] == '1':
                #print("first bit", bits[-1])
                self.code.append("INC a")
            self.code.append("RESET g")
            self.code.append("RESET h")
            #self.code.append(f"PUT")
            self.code.append("SWAP h")
            self.code.append("SUB h")
            self.code.append(f"SWAP {reg}")
            self.code.append("RESET g")
            self.code.append("RESET h")
            if reg != 'a':
                self.code.append("RESET a")
 
        else:
             self.code.append(f"RESET {reg}")
        #"""  
    def var_address(self, name, reg, declared=True):
        #print(self.iterators)
        if declared or name in self.iterators:
            address = self.symbols.get_address(name)
            #print("var_address", name, address, reg)
            self.code.append(f"RESET {reg}")
            self.code.append(f"SWAP {reg}")
            self.const_make(address, 'a')
            self.code.append(f"SWAP {reg}")
        else:
            raise Exception(f"Niezainicjowana zmienna {name}")
 
    def var_load(self, name, r, declared=True):
            self.var_address(name, r, declared)
            self.code.append(f"LOAD {r}")

    def load_array_at(self, array, index, r1, r2):
        self.load_array_address_at(array, index, r1, r2)
        self.code.append(f"LOAD {r1}")

    def load_array_address_at(self, array, index, r1, r2):
        if type(index) == int:
            address = self.symbols.get_address((array, index))
            #print("ADRESS", address)
            self.const_make(address, 'a')
        elif type(index) == tuple:
            #print("load_array_address_at")
            if type(index[1]) == tuple:
                self.var_load(index[1][1], r1, declared=False)
            else:
                #print("here")
                if not self.symbols[index[1]].initialized and index[1] not in self.iterators:
                    raise Exception(f"Uzycie {array}({index[1]}) gdzie  {index[1]} nie zostala zainicjowana")
                self.var_load(index[1], r1)
                #self.code.append(f"PUT")
            var = self.symbols.get_variable(array)
            #print("var", var, index)
            #self.code.append("PUT")
            self.code.append(f"RESET {r2}")
            self.code.append(f"SWAP {r2}")


            self.const_make(var.first_index, 'a')
            self.code.append(f"SWAP {r2}")
            self.code.append(f"SUB {r2}")
            self.code.append(f"SWAP {r2}")
            self.const_make(var.memory_id, 'a')
            self.code.append(f"SWAP {r2}")
            self.code.append(f"ADD {r2}")
            #self.code.append(f"PUT")

    def condition(self, condition):
        #print("condition", condition)
        self.exp_make(condition[1])
        self.code.append("SWAP b")
        
        self.exp_make(condition[2])

        if condition[0] == "eq":
            self.code.append("SUB b")
            self.code.append("JZERO 2")
            self.code.append("JUMP finish")
        
        if condition[0] == "neq":
            self.code.append("SUB b")
            self.code.append("JZERO finish")

        if condition[0] == "ge":
            self.code.append("SUB b")
            self.code.append("JNEG 2")
            self.code.append("JUMP finish")

        if condition[0] == "geq":
            self.code.append("SUB b")
            self.code.append("JNEG 3")
            self.code.append("JZERO 2")
            self.code.append("JUMP finish")
        
        if condition[0] == "le":
            self.code.append("SWAP b")
            self.code.append("SUB b")
            self.code.append("JNEG 2")
            self.code.append("JUMP finish")

        if condition[0] == "leq":
            self.code.append("SWAP b")
            self.code.append("SUB b")
            self.code.append("JNEG 3")
            self.code.append("JZERO 2")
            self.code.append("JUMP finish")
    
