class Pile:
    def __init__(self):
        self.elements = []

    def est_vide(self):
        return len(self.elements) == 0

    def empiler(self, element):
        self.elements.append(element)

    def depiler(self):
        if not self.est_vide():
            return self.elements.pop()
        else:
            raise IndexError("La pile est vide, impossible de dépiler.")

    def sommet(self):
        if not self.est_vide():
            return self.elements[-1]
        else:
            raise IndexError("La pile est vide, aucun sommet.")

    def taille(self):
        return len(self.elements)

TOKEN_TYPES = {
    'NUMBER': '0123456789',
    'PLUS': '+',
    'MINUS': '-',
    'MULTIPLY': '*',
    'DIVIDE': '/',
    'LPAREN': '(',
    'RPAREN': ')',
    'VARIABLE': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
    'ASSIGN': '='
}
# Définition de l'arbre binaire pour l'expression
class Node:
    def __init__(self, value):
        self.value = value  # Le contenu du nœud (opérateur ou valeur)
        self.left = None    # Enfant gauche
        self.right = None   # Enfant droit

def get_priority(op):
    if op in ('+', '-'):
        return 1
    elif op in ('*', '/'):
        return 2
    return 0

def construire_arbre(tokens):
    stack = Pile()
    for token in tokens:
        if token.isdigit() or token.isidentifier():  # Si c'est un nombre ou une variable
            stack.empiler(Node(token))
        elif token in ['+', '-', '*', '/']:  # Si c'est un opérateur
            right = stack.depiler()  # Opérande droite
            left = stack.depiler()   # Opérande gauche
            node = Node(token)       # Nœud avec l'opérateur
            node.left = left
            node.right = right
            stack.empiler(node)  # Empiler le sous-arbre
    return stack.depiler()

def tokenisation(expression):
    tokens = []  # Liste des jetons
    stack = Pile()  # Pile pour les opérateurs et parenthèses
    i = 0

    while i < len(expression):
        # Si c'est un espace, on l'ignore
        if expression[i] == " ":
            i += 1
            continue
        
        # Si c'est un nombre, on le prend en entier
        if expression[i] in TOKEN_TYPES['NUMBER']:
            token = ''
            while expression[i] in TOKEN_TYPES['NUMBER']:
                token += expression[i]
                i += 1
            tokens.append(token)

        # Si c'est une variable (lettres ou underscore), on l'ignore
        elif expression[i] in TOKEN_TYPES['VARIABLE']:
            token = ''
            while i < len(expression) and (expression[i] in TOKEN_TYPES['VARIABLE'] or expression[i].isdigit()):
                token += expression[i]
                i += 1
            tokens.append(token)

        # Si c'est un opérateur (+, -, *, /), on gère la priorité
        elif expression[i] in [TOKEN_TYPES['PLUS'], TOKEN_TYPES['MINUS'], TOKEN_TYPES['MULTIPLY'], TOKEN_TYPES['DIVIDE']]:
            while not stack.est_vide() and stack.sommet() != '(' and get_priority(stack.sommet()) >= get_priority(expression[i]):
                tokens.append(stack.depiler())
            stack.empiler(expression[i])
            i += 1
        
        # Si c'est une parenthèse ouvrante
        elif expression[i] == TOKEN_TYPES['LPAREN']:
            stack.empiler('(')
            i += 1
        
        # Si c'est une parenthèse fermante
        elif expression[i] == TOKEN_TYPES['RPAREN']:
            while not stack.est_vide() and stack.sommet() != '(':
                tokens.append(stack.depiler())
            stack.depiler()  # Supprimer la parenthèse ouvrante
            i += 1
        
        # Si c'est une affectation (=), on l'ignore
        elif expression[i] == TOKEN_TYPES['ASSIGN']:
            i += 1
        
        # Si c'est un caractère invalide, on l'ignore (cela ne devrait pas arriver ici)
        else:
            i += 1

    # Vider la pile des opérateurs restants
    while not stack.est_vide():
        tokens.append(stack.depiler())

    return tokens

def afficher_arbre(node, level=0):
    if node:
        afficher_arbre(node.right, level + 1)
        print("   " * level + f"{node.value}")
        afficher_arbre(node.left, level + 1)

# Calcul en mode postfixe (récursif)
def calcul_arbre_postfixe(node):
    if node.value in TOKEN_TYPES['NUMBER']:
        return int(node.value)
    else:
        left = calcul_arbre_postfixe(node.left)
        right = calcul_arbre_postfixe(node.right)
        if node.value == TOKEN_TYPES['PLUS']:
            return left + right
        elif node.value == TOKEN_TYPES['MINUS']:
            return left - right
        elif node.value == TOKEN_TYPES['MULTIPLY']:
            return left * right
        elif node.value == TOKEN_TYPES['DIVIDE']:
            return left / right

# Exemple d'utilisation
expression = "(2 * 2) * (5 - 2)"
tokens = tokenisation(expression)
arbre = construire_arbre(tokens)
print(tokens)
afficher_arbre(arbre)
print(calcul_arbre_postfixe(arbre))
