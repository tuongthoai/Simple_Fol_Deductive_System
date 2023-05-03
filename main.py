from FOL_Knowlegde_Base import *

KB_PATH = "./04/BritishRoyalfamily.pl"
QUERY_PATH = "./04/BritishRoyalfamily_Query.txt"
ANSWER_PATH = "./04/OUTPUT.txt"

KB = FolKB()

# Read KB
file = open(KB_PATH, 'r')
# file = open('./02/ShinWorldKnowledge.pl', 'r')
clauses = [x.strip() for x in file.readlines()]
file.close()

queries = []

cnt = 0
for clause in clauses:
    # cnt = cnt + 1
    if clause.startswith("/*") or clause.endswith("*/"):
        continue

    if clause != '':
        # print(cnt)
        KB.learn(toExpression(clause))

# Read Query and Answer them
file = open(QUERY_PATH, 'r')
output_file = open(ANSWER_PATH, 'w')
queries = [x.strip() for x in file.readlines()]
for query in queries:
    if query.startswith("/*") or query.endswith("*/"):
        continue

    if query != '':
        result = list(KB.ask_generator(toExpression(query)))
        cnt += 1
        ll = len(result)

        res = []
        for ans in result:
            res.append(str(ans).replace("{", "").replace("}", ""))

        if ll == 0:
            output_file.write("{} False\n".format(cnt))
        elif ll > 1:
            output_file.write("{} {}\n".format(cnt, res))
        else:
            tmp = str(res[0])
            if len(tmp) == 2:
                output_file.write(f"{cnt} True\n")
            else:
                output_file.write(f"{cnt} {res}\n")

file.close()
output_file.close()
