from FOL_Knowlegde_Base import *

"""
For testing BritishRoyalFamily please uncomment from line 7 to line 10 and comment line 13 to line 16
otherwise do the same thing but reverse it.
"""

FOLDER_PATH = 'BritishRoyalFamily'
KB_PATH = "./"+FOLDER_PATH+"/BritishRoyalfamily.pl"
QUERY_PATH = "./"+FOLDER_PATH+"/BritishRoyalfamily_Query.txt"
ANSWER_PATH = "./"+FOLDER_PATH+"/OUTPUT.txt"


# FOLDER_PATH = 'ShinFamily'
# KB_PATH = "./"+FOLDER_PATH+"/ShinWorldKnowledge_c.pl"
# QUERY_PATH = "./"+FOLDER_PATH+"/ShinWorldQueries.txt"
# ANSWER_PATH = "./"+FOLDER_PATH+"/OUTPUT.txt"

KB = FolKB()

# Read KB
file = open(KB_PATH, 'r')
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
        expression = toExpression(query)
        var = []
        for arg in expression.args:
            if is_variable(arg):
                var.append(toExpression(arg.op))

        result = list(KB.ask_generator(expression))
        cnt += 1
        ll = len(result)
        
        if ll == 0:
            output_file.write("{} False\n".format(cnt))
        # elif ll > 1:
        #     output_file.write("{} {}\n".format(cnt, result))
        else:
            if not result[0].keys:
                output_file.write(f"{cnt} {False}\n")
            else:
                if not var:
                    output_file.write(f"{cnt} True\n")
                else:
                    final_result = set()

                    for subs in result:
                        final_result.add(str(dict([(arg, subs.get(arg)) for arg in var])))

                    ans = ','.join(final_result)

                    output_file.write(f"{cnt} {ans}\n")

file.close()
output_file.close()
