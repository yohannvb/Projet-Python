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

# Définition de l'arbre binaire de recherche (ABR) pour les variables
class ABRNode:
    def __init__(self, key, value):
        self.key = key      # Nom de la variable
        self.value = value  # Valeur de la variable
        self.left = None    # Sous-arbre gauche
        self.right = None   # Sous-arbre droit

# Classe pour gérer la table des symboles avec un ABR
class TableSymboles:
    def __init__(self):
        self.root = None
    
    def inserer(self, key, value):
        self.root = self._inserer_recursif(self.root, key, value)
    
    def _inserer_recursif(self, node, key, value):
        if node is None:
            return ABRNode(key, value)
        
        if key < node.key:
            node.left = self._inserer_recursif(node.left, key, value)
        elif key > node.key:
            node.right = self._inserer_recursif(node.right, key, value)
        else:  # key == node.key, mise à jour de la valeur
            node.value = value
        
        return node
    
    def rechercher(self, key):
        return self._rechercher_recursif(self.root, key)
    
    def _rechercher_recursif(self, node, key):
        if node is None or node.key == key:
            return node
        
        if key < node.key:
            return self._rechercher_recursif(node.left, key)
        return self._rechercher_recursif(node.right, key)
    
    def get_value(self, key):
        node = self.rechercher(key)
        if node:
            return node.value
        return None
    
    def afficher(self):
        self._afficher_recursif(self.root)
    
    def _afficher_recursif(self, node, level=0):
        if node:
            self._afficher_recursif(node.right, level + 1)
            print("   " * level + f"{node.key}: {node.value}")
            self._afficher_recursif(node.left, level + 1)

def get_priority(op):
    if op in ('+', '-'):
        return 1
    elif op in ('*', '/'):
        return 2
    return 0

# Analyse lexicale améliorée
def analyse_lexicale(code):
    tokens = []
    i = 0
    
    while i < len(code):
        # Ignorer les espaces
        if code[i].isspace():
            i += 1
            continue
            
        # Traitement des nombres
        if code[i].isdigit():
            num = ""
            while i < len(code) and code[i].isdigit():
                num += code[i]
                i += 1
            tokens.append({"type": "NUMBER", "value": num})
            continue
            
        # Traitement des variables
        if code[i].isalpha() or code[i] == '_':
            var = ""
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                var += code[i]
                i += 1
            
            # Vérifier si c'est un mot-clé
            if var == "print":
                tokens.append({"type": "PRINT", "value": var})
            else:
                tokens.append({"type": "VARIABLE", "value": var})
            continue
            
        # Traitement des opérateurs et caractères spéciaux
        if code[i] == '+':
            tokens.append({"type": "OPERATOR", "value": "+"})
        elif code[i] == '-':
            tokens.append({"type": "OPERATOR", "value": "-"})
        elif code[i] == '*':
            tokens.append({"type": "OPERATOR", "value": "*"})
        elif code[i] == '/':
            tokens.append({"type": "OPERATOR", "value": "/"})
        elif code[i] == '=':
            tokens.append({"type": "ASSIGN", "value": "="})
        elif code[i] == '(':
            tokens.append({"type": "LPAREN", "value": "("})
        elif code[i] == ')':
            tokens.append({"type": "RPAREN", "value": ")"})
        elif code[i] == '#':  # Commentaires
            while i < len(code) and code[i] != '\n':
                i += 1
            continue
        
        i += 1
    
    return tokens

# Analyse syntaxique pour construire l'AST
def construire_ast(tokens):
    # Séparer le code en lignes
    lignes = []
    ligne_courante = []
    
    for token in tokens:
        ligne_courante.append(token)
        if token["type"] == "RPAREN" and any(t["type"] == "PRINT" for t in ligne_courante):
            lignes.append(ligne_courante)
            ligne_courante = []
        elif token["type"] == "ASSIGN":
            # On va jusqu'à la fin de l'expression
            i = tokens.index(token) + 1
            while i < len(tokens) and not (tokens[i]["type"] == "VARIABLE" and i+1 < len(tokens) and tokens[i+1]["type"] == "ASSIGN"):
                if tokens[i]["type"] == "PRINT":
                    break
                ligne_courante.append(tokens[i])
                i += 1
            lignes.append(ligne_courante)
            ligne_courante = []
    
    if ligne_courante:
        lignes.append(ligne_courante)
    
    # Construire l'AST pour chaque ligne
    ast_lignes = []
    for ligne in lignes:
        if len(ligne) >= 3 and ligne[0]["type"] == "VARIABLE" and ligne[1]["type"] == "ASSIGN":
            # Cas d'assignation: variable = expression
            variable = ligne[0]["value"]
            expression = ligne[2:]
            ast_lignes.append({"type": "ASSIGN", "variable": variable, "expression": expression})
        elif len(ligne) >= 4 and ligne[0]["type"] == "PRINT" and ligne[1]["type"] == "LPAREN" and ligne[-1]["type"] == "RPAREN":
            # Cas de print: print(expression)
            expression = ligne[2:-1]
            ast_lignes.append({"type": "PRINT", "expression": expression})
    
    return ast_lignes

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
            while i < len(expression) and expression[i] in TOKEN_TYPES['NUMBER']:
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

def afficher_arbre(node, level=0):
    if node:
        afficher_arbre(node.right, level + 1)
        print("   " * level + f"{node.value}")
        afficher_arbre(node.left, level + 1)

# Fonction d'évaluation d'expressions avec variables
def evaluer_expression(node, table_symboles):
    if node is None:
        return 0
    
    # Si c'est une feuille (nombre ou variable)
    if node.left is None and node.right is None:
        if node.value.isdigit():  # Si c'est un nombre
            return int(node.value)
        else:  # Si c'est une variable
            valeur = table_symboles.get_value(node.value)
            if valeur is not None:
                return valeur
            raise ValueError(f"Variable '{node.value}' non définie")
    
    # Évaluer récursivement les enfants
    left_val = evaluer_expression(node.left, table_symboles)
    right_val = evaluer_expression(node.right, table_symboles)
    
    # Appliquer l'opération
    if node.value == '+':
        return left_val + right_val
    elif node.value == '-':
        return left_val - right_val
    elif node.value == '*':
        return left_val * right_val
    elif node.value == '/':
        if right_val == 0:
            raise ZeroDivisionError("Division par zéro")
        return left_val / right_val

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

# Fonction pour l'assignation des variables
def assignation(variable, table_symboles):
    if variable in globals():
        valeur = globals()[variable]
        table_symboles[variable] = valeur
    return table_symboles

def interpreter_code(code):
    # Analyse lexicale
    tokens = analyse_lexicale(code)
    
    # Analyse syntaxique
    ast = construire_ast(tokens)
    
    # Table des symboles (ABR)
    table_symboles = TableSymboles()
    
    # Exécution du code
    for instruction in ast:
        if instruction["type"] == "ASSIGN":
            # Cas d'assignation
            variable = instruction["variable"]
            expression_tokens = []
            
            # Convertir les tokens d'expression en format pour tokenisation
            for token in instruction["expression"]:
                if token["type"] == "NUMBER":
                    expression_tokens.append(token["value"])
                elif token["type"] == "VARIABLE":
                    expression_tokens.append(token["value"])
                elif token["type"] == "OPERATOR":
                    expression_tokens.append(token["value"])
                elif token["type"] == "LPAREN":
                    expression_tokens.append("(")
                elif token["type"] == "RPAREN":
                    expression_tokens.append(")")
            
            # Convertir en expression et tokeniser
            expression = " ".join(expression_tokens)
            tokens_postfixe = tokenisation(expression)
            
            # Construire l'arbre et évaluer
            arbre = construire_arbre(tokens_postfixe)
            valeur = evaluer_expression(arbre, table_symboles)
            
            # Stocker dans la table des symboles
            table_symboles.inserer(variable, valeur)
            
        elif instruction["type"] == "PRINT":
            # Cas de print
            expression_tokens = []
            
            # Convertir les tokens d'expression
            for token in instruction["expression"]:
                if token["type"] == "NUMBER":
                    expression_tokens.append(token["value"])
                elif token["type"] == "VARIABLE":
                    # Pour une variable, on récupère sa valeur
                    var_node = table_symboles.rechercher(token["value"])
                    if var_node:
                        expression_tokens.append(str(var_node.value))
                    else:
                        raise ValueError(f"Variable '{token['value']}' non définie")
            
            # Afficher le résultat
            print("".join(expression_tokens))
    
    return table_symboles

# Exemple d'utilisation
if __name__ == "__main__":
    print("\n=== Test de l'expression mathématique ===")
    expression = "(2 * 2) * (5 - 2)"
    tokens = tokenisation(expression)
    arbre = construire_arbre(tokens)
    print("Tokens:", tokens)
    print("Arbre:")
    afficher_arbre(arbre)
    print("Résultat:", calcul_arbre_postfixe(arbre))
    
    print("\n=== Test de la table des symboles avec ABR ===")
    symboles = TableSymboles()
    symboles.inserer("x", 8)
    symboles.inserer("y", 10)
    symboles.inserer("z", 5)
    symboles.inserer("a", 20)
    symboles.inserer("x", 15)  # Mise à jour de x
    print("Table des symboles:")
    symboles.afficher()
    
    print("\n=== Test de l'interpréteur du mini-langage ===")
    code_test = """
    x = 5 + 3
    y = x * 2
    print(y)  # Devrait afficher 16
    z = y - x
    print(z)  # Devrait afficher 8
    """
    
    table_finale = interpreter_code(code_test)
    print("\nTable des symboles finale:")
    table_finale.afficher()