from searchPlus import *
from collections import namedtuple


line1 = "## ## ## ## ## ## ## ## ##\n"
line2 = "## .. .. .. .. .. .. .. ##\n"
line3 = "## .. .. .. 00 .. .. .. ##\n"
line4 = "## .. .. .. .. .. .. .. ##\n"
line5 = "## .. .. () () () .. .. ##\n"
line6 = "## .. .. .. .. .. .. .. ##\n"
line7 = "## .. .. .. 01 .. .. .. ##\n"
line8 = "## .. .. .. .. .. .. .. ##\n"
line9 = "## ## ## ## ## ## ## ## ##\n"
grid = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9


EstadoPin = namedtuple('EstadoPin','pinguins')

class EstadoPinguins(EstadoPin):
    
    def __hash__(self):
        return hash(tuple(sorted(self.pinguins.items())))
    
    def __lt__(self,other):
        return True
    
    
class PenguinsPairs(Problem):
    
    def process_txt(self, grid):
        """
        Função que processa a grelha em txt e obtém as posições dos icebergues (walls), água e pinguins.
        O output desta função é um dicionário em que as chaves identifica cada tipo de informação a ser 
        guardada. Os pinguins serão um dicionário e os icebergues e água serão um conjunto.
        """
        data = {'walls': set(), 'pinguins': {}, 'water': set()}
        lines = grid.split('\n')[:-1]
        x = 0
        for row in lines:
            ll = row.split()
            y = 0
            for col in ll:
                if col == '##':
                    data['walls'].add((x,y))
                elif col == '()':
                    data['water'].add((x,y))
                elif col != '..':
                    data['pinguins'][col] = (x,y)
                y += 1
            x += 1
        data['dim'] = (len(lines),len(ll))
        return data
    
    
    directions = {"N":(-1, 0), "E":(0, +1), "S":(+1, 0), "O":(0, -1)}  # ortogonais
    
    
    def __init__(self, ice_map=grid):
        initialStatus = self.process_txt(ice_map) # processa o txt e converte num dicionário

        self.initial = EstadoPinguins(initialStatus['pinguins'])  
        # self.initial.pinguins = sorted(self.initial.pinguins)
        
        self.goal = {} # estado vazio
        self.obstacles = initialStatus['walls'] # posições do icebergues
        self.water = initialStatus['water'] # posições da água
        self.dim = initialStatus['dim'] # dimensão do mapa (não precisa de ser quadrado)

    
    def slide(self,state,x,y,d):
        """
        Função que identifica se é possível o pinguim se deslocar numa direção.
        """
        (dx,dy) = self.directions[d]
        if (x+dx,y+dy) in self.obstacles:
            return False
        while (x+dx,y+dy) not in self.obstacles and (x+dx,y+dy) not in state.pinguins.values():
            if (x+dx,y+dy) in self.water:
                return False
            x = x+dx
            y = y+dy
        return True
    
    
    def actions (self, state):
        """
        Devolve uma lista ordenada com todas as ações possíveis para o estado.
        """
        actions_list = []
        for p in state.pinguins.keys():
            x,y = state.pinguins[p] # coordenadas da posição do pinguim 
            if self.slide(state,x,y,"N"): # verifica se o pinguim pode deslocar-se para Norte
                actions_list.append((p,"N"))
            if self.slide(state,x,y,"S"):
                actions_list.append((p,"S"))
            if self.slide(state,x,y,"E"):
                actions_list.append((p,"E"))
            if self.slide(state,x,y,"O"):
                actions_list.append((p,"O"))
        return sorted(actions_list) 
    

    def result (self, state, action):
        """
        Devolve um novo estado resultante de aplicar "action" a "state".
        """
        p,d = action # ação é um tuplo (ID pinguim, direção)
        pinguins = state.pinguins.copy()
        x,y = state.pinguins[p]
        (dx,dy) = self.directions[d]
        # desloca o pinguim até que embata num obstáculo ou noutro pinguim
        while (x+dx,y+dy) not in self.obstacles and (x+dx,y+dy) not in state.pinguins.values():
            x = x+dx
            y = y+dy
        # se o pinguim embateu num obstáculo, atualiza-se a posição do pinguim
        if (x+dx,y+dy) in self.obstacles:
            pinguins[p] = (x,y)
        # se o pinguim embateu noutro pinguim, ambos são removidos do estado
        if (x+dx,y+dy) in state.pinguins.values():
            pinguins.pop(p)
            for key in state.pinguins:
                if state.pinguins[key] == (x+dx,y+dy):
                    pinguins.pop(key)
                    break
        return EstadoPinguins(pinguins)
    

    def goal_test (self, state):
        """
        Verifica se todos os pinguins estão emparelhados, ou seja, se os estado está vazio.
        """
        return state.pinguins == {}
    

    def display (self, state):
        """
        Devolve a grelha em modo txt.
        """
        output = ""
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if (i,j) in state.pinguins.values():
                    for key in state.pinguins:
                        if state.pinguins[key] == (i,j):
                            ch = key
                            break
                elif (i,j) in self.obstacles:
                    ch = "##"
                elif (i,j) in self.water:
                    ch = "()"
                else:
                    ch = ".."
                output += ch + " "
            output += "\n"
        return output
    

    def executa(self, state, actions_list, verbose=False):
        """Executa uma sequência de acções a partir do estado devolvendo o triplo formado pelo estado, 
        pelo custo acumulado e pelo booleano que indica se o objectivo foi ou não atingido. Se o objectivo 
        for atingido antes da sequência ser atingida, devolve-se o estado e o custo corrente.
        Há o modo verboso e o não verboso, por defeito."""
        cost = 0
        for a in actions_list:
            seg = self.result(state,a)
            cost = self.path_cost(cost,state,a,seg)
            state = seg
            obj = self.goal_test(state)
            if verbose:
                print('Ação:', a)
                print(self.display(state),end='')
                print('Custo Total:',cost)
                print('Atingido o objectivo?', obj)
                print()
            if obj:
                break
        return (state, cost, obj)
    
    
    def halfPenguins(self, node):
        """
        Heurística que considera metade do número de pinguins.
        """
        return len(node.state.pinguins)//2
    
    
    def Npairings(self, node):
        
        paired = []
        sortedState = dict(sorted(node.state.pinguins.items(), key=lambda item: item[0]))  #ver com o stor
        
        for penguin, coords in sortedState.items():
            if penguin in paired:
                continue
            for penguin2, coords2 in sortedState.items():
                if penguin2 in paired or penguin == penguin2:
                    continue
                if coords[0] != coords2[0] and coords[1] != coords2[1]:
                    continue
                if coords[0] == coords2[0]:
                    if coords[1] > coords2[1] and self.slide(node.state, coords[0], coords[1], "O"):
                        paired.append(penguin)
                        paired.append(penguin2)
                        break
                    if coords[1] < coords2[1] and self.slide(node.state, coords[0], coords[1], "E"):
                        paired.append(penguin)
                        paired.append(penguin2)
                        break
                if coords[1] == coords2[1]:
                    if coords[0] > coords2[0] and self.slide(node.state, coords[0], coords[1], "N"):
                        paired.append(penguin)
                        paired.append(penguin2)
                        break
                    if coords[0] < coords2[0] and self.slide(node.state, coords[0], coords[1], "S"):
                        paired.append(penguin)
                        paired.append(penguin2)
                        break

        np = len(paired) // 2
        nsp = len(sortedState.keys()) - len (paired)

        return np+nsp 
    
    
    def highestPairings(self, node):
        
        pass
    
