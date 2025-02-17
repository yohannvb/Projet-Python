def tokenisation(expression):
    i = 0
    tokens = []
    while i < len(expression):
        if expression[i] != " ":
            tokens.append(expression[i])
        i += 1
    return tokens

expression = "3 * 3 / ( 2 - 4 ) + 5"
print(tokenisation(expression))
