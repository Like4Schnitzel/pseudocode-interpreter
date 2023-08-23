"""Interprets pseudocode."""
from re import findall
from dataclasses import dataclass

@dataclass
class Line:
    """Holds information about a line of pseudocode."""
    text: str
    index: int
    indent: int

@dataclass
class BlockInitiator:
    """Holds information about a block initiator"""
    initiator: str = ""
    index: int = 0
    condition: any = ""
    entered_case: bool = False
    var: str = ""
    stop: any = ""
    step: any = ""

def is_in_quotes(string, index):
    """Checks if a char in a string is surrounded by quotes."""
    return string[:index].count('"') % 2 == 1

def find_last_non_quoted_string(string, to_find):
    """Finds last occurrence of a substring in a string that isn't surrounded by quotes.
       Returns -1 if unsuccesful."""
    index = string.rfind(to_find)
    while index != -1:
        if not is_in_quotes(string, index):
            return index
        index = string.rfind(to_find, 0, index)
    return index

def find_closing_pars(expr : str, open_par):
    """Returns end index of a bracket pair."""
    levels_deep = 1
    i = open_par+1
    while levels_deep > 0:
        if expr[i] == '(':
            levels_deep += 1
        elif expr[i] == ')':
            levels_deep -= 1

        i += 1
        if (i >= len(expr) and levels_deep > 0):
            raise SyntaxError("expected ')'")

    return i-1

def to_bool(string):
    """Attempts to typecast a string to a boolean."""
    if isinstance(string, bool):
        return string

    if (string == "true" or string == "True"):
        return True
    if (string == "false" or string == "False"):
        return False

    raise SyntaxError("expected a boolean value.")

def float_or_bool_or_string(val : str):
    """Attempts to automatically typecast a string."""
    try:
        try:
            return to_bool(val)
        except SyntaxError:
            return rounded_float(val)
    except SyntaxError:
        return val

def var_or_not(val : str, variables : dict):
    """Checks if a string is a variable name. If not, returns a typecasted value of the string."""
    if (val[0] == "\"" and val[-1] == "\"") or (val[0] == "'" and val[-1] == "'" and len(val) == 3):
        return val[1:-1]

    try:
        try:
            return to_bool(val)
        except SyntaxError:
            return rounded_float(val)
    except Exception as exc:
        is_valid_var_name(val)
        if val in variables.keys():
            return variables[val]

        raise SyntaxError("value not assigned.") from exc

def rounded_float(num):
    """Typecasts to a float, rounded to 8 decimal places."""
    return round(float(num), 8)

def eval_expression(expr, variables : dict):
    """Evaluates expressions recursively."""
    if not isinstance(expr, str):
        return expr

    expr = expr.strip(' ')

    if expr.startswith('nicht '):
        return not to_bool(eval_expression(expr[6:], variables))

    open_par = expr.find('(')
    while open_par != -1:
        closing_par = find_closing_pars(expr, open_par)
        expr = expr[:open_par] \
               + str(eval_expression(expr[open_par+1:closing_par], variables)) \
               + expr[closing_par+1:]

        open_par = expr.find('(')

    connector_groups = [[' oder ', ' und '], ['==', '!=', '<', '>', '<=', '>='],
                       ['+', '-'], [' div ', ' mod ', '%', '/', '*'], ['^']]

    for group in connector_groups:
        last_connector = -1
        for connector in group:
            last_found = find_last_non_quoted_string(expr, connector)
            if last_found >= last_connector:
                last_connector = last_found
                last_connector_string = connector

        if last_connector >= 0:
            splits = [expr[:last_connector], expr[last_connector+len(last_connector_string):]]

            match (last_connector_string):
                case ' und ':
                    return eval_expression(splits[0], variables) \
                           and eval_expression(splits[1], variables)

                case ' oder ':
                    return eval_expression(splits[0], variables) \
                           or eval_expression(splits[1], variables)

                case '==':
                    return eval_expression(splits[0], variables) \
                           == eval_expression(splits[1], variables)

                case '!=':
                    return eval_expression(splits[0], variables) \
                           != eval_expression(splits[1], variables)

                case '<':
                    return eval_expression(splits[0], variables) \
                           < eval_expression(splits[1], variables)

                case '>':
                    return eval_expression(splits[0], variables) \
                           > eval_expression(splits[1], variables)

                case '<=':
                    return eval_expression(splits[0], variables) \
                           <= eval_expression(splits[1], variables)

                case '>=':
                    return eval_expression(splits[0], variables) \
                           >= eval_expression(splits[1], variables)

                case '^':
                    return eval_expression(splits[0], variables) \
                           ** eval_expression(splits[1], variables)

                case ' div ':
                    return int(eval_expression(splits[0], variables)) \
                           / int(eval_expression(splits[1], variables))

                case ' mod ' | '%':
                    return eval_expression(splits[0], variables) \
                           % eval_expression(splits[1], variables)

                case '/':
                    return eval_expression(splits[0], variables) \
                           / eval_expression(splits[1], variables)

                case '*':
                    return eval_expression(splits[0], variables) \
                           * eval_expression(splits[1], variables)

                case '+':
                    return eval_expression(splits[0], variables) \
                           + eval_expression(splits[1], variables)

                case '-':
                    if splits[0] == "":
                        return -eval_expression(splits[1], variables)
                    #else
                    return eval_expression(splits[0], variables) \
                           - eval_expression(splits[1], variables)

    if expr.startswith('sqrt '):
        return var_or_not(expr[5:], variables) ** 0.5

    return var_or_not(expr, variables)

def get_all_tokens(line : str):
    """Indexes all 'tokens' of a line."""
    #remove comments
    line_comment_pos = line.find('//')
    if line_comment_pos != -1:
        line = line[:line_comment_pos]
        line_comment_pos = line.find('//')

    block_comment_start_pos = line.find('/*')
    while block_comment_start_pos != -1:
        line = line[:block_comment_start_pos] + line[line.find('*/')+2:]
        block_comment_start_pos = line.find('/*')

    tokens = []
    in_quotations = False
    split_line = []
    last_append_index = 0
    for (i, char) in enumerate(line):
        if char == "\"":
            in_quotations = not in_quotations

        if (not in_quotations and char == " ") or i == len(line)-1:
            to_append = line[last_append_index:i+1].strip(" ")
            if to_append != "":
                split_line.append(to_append)
            last_append_index = i+1
    for token in split_line:
        #turn "foo<=bar>=baz" into ["foo", "<", "=", "bar", ">", "=", "baz"]
        i = 0
        in_quotations = False
        while i < len(token):
            if token[i] == "\"":
                in_quotations = not in_quotations

            if not in_quotations:
                if (token[i] in ['<', '>', '=', '!']):
                    if token[:i] != '':
                        tokens.append(token[:i])
                    tokens.append(token[i])
                    token = token[i+1:]
                    i = -1
            i += 1
        if token != '':
            tokens.append(token)

    return tokens

def is_valid_var_name(string):
    """Checks if a variable name breaks conventions."""
    for (i, char) in enumerate(string.lower()):
        if (((char < 'a' or char > 'z') and (char < '0' or char > '9'))\
            or (i == 0 and char >= '0' and char <= '9')):
            raise SyntaxError(f"'{string}' is not a valid variable name.")

def get_indent_step(lines):
    """Gets amount of spaces per indent in the input file."""
    for line in lines:
        if line.indent > 0:
            return line.indent

    return 0

def better_join(elems : list, char : chr):
    """To be used instead of str.join()"""
    out = ""
    for (i, elem) in enumerate(elems):
        out += elem
        if (i >= len(elems)-1 or (elem + elems[i+1] not in ['<=', '>=', '!=', '=='])):
            out += char

    return out

def indent_of_last_key(block_initiators : dict, key_str : str):
    """Returns indent of most recent block initiator key."""
    last_indent = -1
    for key in block_initiators.keys():
        if block_initiators[key].initiator == key_str:
            last_indent = key

    return last_indent

def main_thread(lines):
    """Function to handle interpretation of input file."""
    variables = {}
    block_initiators = {}
    output = ""
    indent_step = get_indent_step(lines)
    max_indent = 0
    line_index = 0

    try:
        while True:
            while line_index < len(lines):
                line = lines[line_index]
                tokens = get_all_tokens(line.text)
                if (len(tokens) == 0 or line.indent > max_indent):
                    line_index += 1
                    continue

                if line.indent < max_indent:
                    begin_indent = max(indent_of_last_key(block_initiators, "solange")
                                  , indent_of_last_key(block_initiators, "für"))

                    if (tokens[0] != "solange" and tokens != ["wiederhole"]) \
                       or begin_indent >= line.indent:

                        if begin_indent > -1:
                            if (line.indent <= begin_indent \
                                and line_index > block_initiators[begin_indent].index):

                                line_index = block_initiators[begin_indent].index
                                continue

                        max_indent = line.indent

                        for key in list(block_initiators.keys()):
                            if key > max_indent:
                                block_initiators.pop(key)

                #get index of token that ends with a colon, if there is one
                colon_index = -1
                i = 0
                while i < len(tokens):
                    if tokens[i].endswith(':'):
                        colon_index = i
                    i += 1

                index = 1
                after_text = False
                match (tokens[0]):
                    case "lies":
                        tokens[1:] = ''.join(tokens[1:]).split(',')

                        while index < len(tokens):
                            is_valid_var_name(tokens[index])
                            variables[tokens[index]] = float_or_bool_or_string((input(
                                "Enter a value for " + tokens[index] + ": ")))

                            temp_out = variables[tokens[index]]
                            if isinstance(temp_out, float):
                                if int(temp_out) == temp_out:
                                    temp_out = int(temp_out)
                                else:
                                    temp_out = round(temp_out, 8)

                            output += f"Enter a value for {tokens[index]}: {temp_out}\n"
                            index += 1

                    case "schreibe":
                        tokens[1:] = findall(r'(?:[^,"]|"[^"]*")+', better_join(tokens[1:], " "))

                        while index < len(tokens):
                            tokens[index] = tokens[index].strip()

                            if (tokens[index].startswith("\"") and tokens[index].endswith("\"")):
                                temp_out = tokens[index][1:-1].replace("\\n", "\n")
                                output += temp_out
                                print(temp_out, end="")
                                after_text = True

                            else:
                                temp_out = eval_expression(tokens[index], variables)
                                if isinstance(temp_out, float):
                                    if int(temp_out) == temp_out:
                                        temp_out = int(temp_out)
                                    else:
                                        temp_out = round(temp_out, 8)
                                if after_text:
                                    output += str(temp_out)
                                    print(str(temp_out), end="")
                                    after_text = False
                                else:
                                    temp_out = f"The value of '{tokens[index]}' is \"{temp_out}\"\n"
                                    output += temp_out
                                    print(temp_out, end="")

                            index += 1

                    case "falls":
                        condition = eval_expression(better_join(tokens[1:], ' '), variables)
                        block_initiators[line.indent] = \
                            BlockInitiator(initiator="falls",condition=condition,entered_case=False)
                        max_indent += indent_step

                    case "dann":
                        if ((not line.indent - indent_step in block_initiators) or \
                            block_initiators[line.indent - indent_step].initiator != "falls"):
                            raise SyntaxError("expected 'falls' before 'dann'.")

                        if len(tokens) > 1:
                            lines.insert(\
                                line_index+1,\
                                Line(\
                                    better_join(tokens[1:],' '),line.index,line.indent+indent_step\
                                )\
                            )
                            lines[line_index].text = (' ' * line.indent) + tokens[0]

                        if block_initiators[line.indent - indent_step].condition:
                            max_indent += indent_step
                        else:
                            #find next 'sonst' at the correct indent, otherwise move to end
                            i = line_index
                            while (\
                                i < len(lines) and\
                                len(lines[i].text) - len(lines[i].text.lstrip(' ') >= line.indent)\
                                ):

                                if lines[i].text.lstrip(" ").startswith("sonst"):
                                    break

                                i += 1
                            line_index = i-1

                    case "sonst":
                        if (not line.indent - indent_step in block_initiators) or\
                            block_initiators[line.indent - indent_step].initiator != "falls":

                            raise SyntaxError("expected 'falls' before 'sonst'.")

                        if len(tokens) > 1:
                            lines.insert(\
                                line_index+1,\
                                Line(better_join(tokens[1:], ' '),\
                                line.index,\
                                line.indent + indent_step)\
                                )
                            line.text = (' ' * line.indent) + tokens[0]

                        if not block_initiators[line.indent - indent_step].condition:
                            max_indent += indent_step

                    case other if colon_index != -1:    #case
                        if (not line.indent - indent_step in block_initiators) or\
                            block_initiators[line.indent - indent_step].initiator != "falls":
                            raise SyntaxError("expected 'falls' before case.")

                        initiator = block_initiators[line.indent - indent_step]

                        if len(tokens) > 1:
                            lines.insert(line_index+1,\
                                Line(better_join(tokens[colon_index+1:], ' '),\
                                line.index,\
                                line.indent + indent_step))
                            line.text = (' '*line.indent) + better_join(tokens[:colon_index+1], ' ')
                            tokens = get_all_tokens(line.text)

                        expression = [tokens[i] for i in range(len(tokens)-1)]
                        expression.append(tokens[-1][:-1])

                        sonst = False
                        if tokens[0] == "sonst:":
                            if initiator.entered_case:
                                line_index += 1
                                continue

                            sonst = True

                        if sonst or initiator.condition == \
                            eval_expression(better_join(expression, ' '), variables):

                            max_indent += indent_step
                            initiator.entered_case = True

                    case "solange":
                        if tokens[-1] == "wiederhole":
                            expression = better_join(tokens[1:-1], ' ')
                        else:
                            expression = better_join(tokens[1:], ' ')
                        condition = eval_expression(expression, variables)

                        if tokens[-1] != "wiederhole":
                            if block_initiators[line.indent].initiator != "wiederhole":
                                raise SyntaxError("expected 'wiederhole' at the end of the line.")
                            if condition:
                                line_index = block_initiators[line.indent].index
                                max_indent -= indent_step
                                continue

                        if condition:
                            block_initiators[line.indent] = BlockInitiator(\
                                initiator="solange",\
                                condition=condition,\
                                index=line_index)

                            max_indent += indent_step
                        elif line.indent in block_initiators:
                            block_initiators.pop(line.indent)

                    case "wiederhole":
                        max_indent += indent_step
                        block_initiators[line.indent] = \
                            BlockInitiator(initiator="wiederhole", index=line_index)

                    case "für":
                        #only do this the first time
                        if not line.indent in block_initiators:
                            if tokens[-1] != "wiederhole":
                                raise SyntaxError("expected 'wiederhole' at the end of the line.")

                            if len(tokens) < 3:
                                raise SyntaxError("expected variable after 'für'.")
                            var = tokens[1]
                            if (len(tokens) < 4 or tokens[2] != 'von'):
                                raise SyntaxError("expected 'von' after variable.")

                            if "bis" not in tokens:
                                raise SyntaxError("expected 'bis' after value.")

                            bis_index = tokens.index('bis')
                            start = tokens[3:bis_index]
                            if len(start) < 1:
                                raise SyntaxError("expected a start value.")
                            variables[var] = eval_expression(better_join(start, ' '), variables)

                            if "mit" in tokens:
                                mit_index = tokens.index("mit")
                            else:
                                mit_index = -1

                            stop = tokens[bis_index+1:mit_index]
                            if len(stop) < 1:
                                raise SyntaxError("expected a stop value.")

                            if mit_index != -1:
                                step = tokens[mit_index+1:-1]
                            else:
                                step = ["1"]

                            block_initiators[line.indent] = BlockInitiator(\
                                initiator="für",var=var, stop=stop, step=step, index=line_index)
                        #on repeats
                        else:
                            variables[block_initiators[line.indent].var] += \
                                eval_expression(\
                                    better_join(block_initiators[line.indent].step, ' '), variables\
                                )

                        if variables[block_initiators[line.indent].var] <= \
                            eval_expression(\
                                better_join(block_initiators[line.indent].stop, ' '), variables\
                            ):

                            max_indent = line.indent + indent_step
                        else:
                            block_initiators.pop(line.indent)

                    case other if tokens[1].strip() == '=':
                        is_valid_var_name(tokens[0])
                        variables[tokens[0]]=eval_expression(better_join(tokens[2:],' '),variables)

                line_index += 1

            if sum([l.initiator for l in block_initiators.values()].count(s) \
                for s in ("solange", "für")) > 0:

                begin_indent = max(indent_of_last_key(block_initiators, "solange"),\
                    indent_of_last_key(block_initiators, "für"))
                line_index = block_initiators[begin_indent].index
                continue
            #else
            break

    except SyntaxError as error:
        temp_out = f"Line {line.index}: {error}"
        print(temp_out)
        output += temp_out
        return output

    return output

def main():
    """main()"""
    with open("in.txt", 'r', encoding="UTF-8") as in_file,\
         open("out.txt", 'w', encoding="UTF-8") as out_file:
        all_lines = []
        i = 1
        for line in in_file:
            line = line.rstrip('\n').rstrip(' ')
            indent = len(line) - len(line.lstrip(' '))
            line = line[indent:]
            if line.endswith(';'):
                line = line[:-1]
            if line != "":
                all_lines.append(Line(line, i, indent))
            i += 1
        output_text = main_thread(all_lines)

        out_file.write(output_text)
        out_file.close()

if __name__ == "__main__":
    main()
