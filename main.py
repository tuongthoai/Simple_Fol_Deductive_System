from FOL_Knowlegde_Base import *

KB = FolKB()

file = open('./01/knowledge.pl', 'r')
# file = open('./02/ShinWorldKnowledge.pl', 'r')
clauses = [x.strip() for x in file.readlines()]
file.close()

queries = []

# to_cnf("((aunt(AuntOrUncle, Person) | uncle(AuntOrUncle, Person)) & female(Person))")


cnt = 0
for clause in clauses:
    cnt = cnt + 1
    if clause.startswith("/*") or clause.endswith("*/"):
        continue

    if clause != '':
        print(cnt)
        KB.learn(toExpression(clause))

file = open("./01/query.pl")
queries = [x.strip() for x in file.readlines()]
for query in queries:
    if query.startswith("/*") or query.endswith("*/"):
        continue

    if query != '':
        result = list(KB.ask_generator(toExpression(query)))
        print(result)
        if len(result) == 0:
            print("False")
        elif len(result) > 0:
            print("True")
        else:
            print(list(result))

file.close()