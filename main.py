from re import findall
from dataclasses import dataclass

@dataclass
class Line:
    text: str;
    index: int;
    indent: int;

@dataclass
class BlockInitiator:
    initiator: str = "";
    index: int = 0;
    condition: any = "";
    enteredCase: bool = False;
    var: str = "";
    stop: any = "";
    step: any = "";

def isInQuotes(s, index):
    return s[:index].count('"') % 2 == 1;

def findLastNonQuotedString(s1: str, s2):
    index = s1.rfind(s2);
    while (index != -1):
        if (not isInQuotes(s1, index)):
            return index;
        index = s1.rfind(s2, 0, index);
    return index;

def findClosingPars(expr : str, openPar):
    levelsDeep = 1;
    i = openPar+1;
    while levelsDeep > 0:
        if (expr[i] == '('):
            levelsDeep += 1;
        elif (expr[i] == ')'):
            levelsDeep -= 1;

        i += 1;
        if (i >= len(expr) and levelsDeep > 0):
            raise Exception("Syntax Error, expected ')'");

    return i-1;

def toBool(s):
    if isinstance(s, bool):
        return s;

    if (s == "true" or s == "True"):
        return True;
    if (s == "false" or s == "False"):
        return False;

    raise Exception("expected a boolean value.");

def floatOrBoolOrString(val : str):
    try:
        try:
            return toBool(val);
        except Exception:
            return roundedFloat(val);
    except:
        return val;

def varOrNot(val : str, variables : dict):
    if ((val[0] == "\"" and val[-1] == "\"") or (val[0] == "'" and val[-1] == "'" and len(val) == 3)):
        return val[1:-1];

    try:
        try:
            return toBool(val);
        except Exception:
            return roundedFloat(val);
    except Exception:
        isValidVarName(val);
        if (val in variables.keys()):
            return variables[val];

        raise Exception("value not assigned.");

def roundedFloat(x):
    return round(float(x), 8);

def evalExpression(expr, variables : dict):
    if (not isinstance(expr, str)):
        return expr;

    expr = expr.strip(' ');

    if expr.startswith('nicht '):
        return not toBool(evalExpression(expr[6:], variables));

    openPar = expr.find('(');
    while (openPar != -1):
        closingPar = findClosingPars(expr, openPar);
        expr = expr[:openPar] + str(evalExpression(expr[openPar+1:closingPar], variables)) + expr[closingPar+1:];
        openPar = expr.find('(');

    connectorGroups = [[' oder ', ' und '], ['==', '!=', '<', '>', '<=', '>='], ['+', '-'], [' div ', ' mod ', '%', '/', '*'], ['^']];

    for group in connectorGroups:
        lastConnector = -1;
        for connector in group:
            lastFound = findLastNonQuotedString(expr, connector);
            if (lastFound >= lastConnector):
                lastConnector = lastFound;
                lastConnectorString = connector;

        if (lastConnector >= 0):
            splits = [expr[:lastConnector], expr[lastConnector+len(lastConnectorString):]];

            match (lastConnectorString):
                case ' und ':
                    return evalExpression(splits[0], variables) and evalExpression(splits[1], variables);

                case ' oder ':
                    return evalExpression(splits[0], variables) or evalExpression(splits[1], variables);

                case '==':
                    return evalExpression(splits[0], variables) == evalExpression(splits[1], variables);

                case '!=':
                    return evalExpression(splits[0], variables) != evalExpression(splits[1], variables);

                case '<':
                    return evalExpression(splits[0], variables) < evalExpression(splits[1], variables);

                case '>':
                    return evalExpression(splits[0], variables) > evalExpression(splits[1], variables);

                case '<=':
                    return evalExpression(splits[0], variables) <= evalExpression(splits[1], variables);

                case '>=':
                    return evalExpression(splits[0], variables) >= evalExpression(splits[1], variables);

                case '^':
                    return evalExpression(splits[0], variables) ** evalExpression(splits[1], variables);

                case ' div ':
                    return int(evalExpression(splits[0], variables)) / int(evalExpression(splits[1], variables));

                case ' mod ' | '%':
                    return evalExpression(splits[0], variables) % evalExpression(splits[1], variables);

                case '/':
                    return evalExpression(splits[0], variables) / evalExpression(splits[1], variables);

                case '*':
                    return evalExpression(splits[0], variables) * evalExpression(splits[1], variables);

                case '+':
                    return evalExpression(splits[0], variables) + evalExpression(splits[1], variables);

                case '-':
                    if (splits[0] == ""):
                        return -evalExpression(splits[1], variables);
                    #else
                    return evalExpression(splits[0], variables) - evalExpression(splits[1], variables);
    
    if (expr.startswith('sqrt ')):
        return varOrNot(expr[5:], variables) ** 0.5;

    return varOrNot(expr, variables);

def getAllTokens(line : str):
    #remove comments
    lineCommentPos = line.find('//');
    if (lineCommentPos != -1):
        line = line[:lineCommentPos];
        lineCommentPos = line.find('//');
    
    blockCommentStartPos = line.find('/*');
    while (blockCommentStartPos != -1):
        line = line[:blockCommentStartPos] + line[line.find('*/')+2:];
        blockCommentStartPos = line.find('/*');

    tokens = [];
    inQuotations = False;
    splitLine = [];
    inQuotes = False;
    lastAppendIndex = 0;
    for i in range(len(line)):
        if line[i] == "\"":
            inQuotations = not inQuotations;
        
        if ((not inQuotations and line[i] == " ") or i == len(line)-1):
            toAppend = line[lastAppendIndex:i+1].strip(" ");
            if (toAppend != ""):
                splitLine.append(toAppend);
            lastAppendIndex = i+1;
    for token in splitLine:
        #turn "foo<=bar>=baz" into ["foo", "<", "=", "bar", ">", "=", "baz"];
        i = 0;
        inQuotations = False;
        while i < len(token):
            if (token[i] == "\""):
                inQuotations = not inQuotations;

            if (not inQuotations):
                if (token[i] in ['<', '>', '=', '!']):
                    if (token[:i] != ''):
                        tokens.append(token[:i]);
                    tokens.append(token[i]);
                    token = token[i+1:];
                    i = -1;
            i += 1;
        if (token != ''):
            tokens.append(token);
        #for tk in [val for pair in zip(token.split('='), ['='] * (token.count('=')+1)) for val in pair][:-1]:
        #    if (tk != ""):
        #        tokens.append(tk);

    return tokens;

def isValidVarName(s : str):
    i = 0;
    for c in s.lower():
        if (((c < 'a' or c > 'z') and (c < '0' or c > '9')) or (i == 0 and c >= '0' and c <= '9')):
            raise Exception(f"'{s}' is not a valid variable name.");
        i += 1;

def getIndentStep(lines):
    for line in lines:
        if (line.indent > 0):
            return line.indent;

    return 0;

def betterJoin(elems : list, c : chr):
    out = "";
    for i in range(len(elems)):
        elem = elems[i];
        out += elem;
        if (i >= len(elems)-1 or (elem + elems[i+1] not in ['<=', '>=', '!=', '=='])):
            out += c;

    return out;

def indentOfLastKey(blockInitiators : dict, key_str : str):
    lastIndent = -1;
    for key in blockInitiators.keys():
        if (blockInitiators[key].initiator == key_str):
            lastIndent = key;

    return lastIndent;

def mainThread(lines):
    variables = {};
    blockInitiators = {};
    output = "";
    indentStep = getIndentStep(lines);
    maxIndent = 0;
    lineIndex = 0;

    try:
        while True:
            while lineIndex < len(lines):
                line = lines[lineIndex];
                tokens = getAllTokens(line.text);
                if (len(tokens) == 0 or line.indent > maxIndent):
                    lineIndex += 1;
                    continue;

                if (line.indent < maxIndent):
                    beginIndent = max(indentOfLastKey(blockInitiators, "solange"), indentOfLastKey(blockInitiators, "für"));

                    if ((tokens[0] != "solange" and tokens != ["wiederhole"]) or beginIndent >= line.indent):
                        if (beginIndent > -1):
                            if (line.indent <= beginIndent and lineIndex > blockInitiators[beginIndent].index):
                                lineIndex = blockInitiators[beginIndent].index;
                                continue;

                        maxIndent = line.indent;
                        
                        for key in list(blockInitiators.keys()):
                            if (key > maxIndent):
                                blockInitiators.pop(key);

                #get index of token that ends with a colon, if there is one
                colonIndex = -1;
                i = 0;
                while (i < len(tokens)):
                    if (tokens[i].endswith(':')):
                        colonIndex = i;
                    i += 1

                index = 1;
                afterText = False;
                match (tokens[0]):
                    case "lies":
                        tokens[1:] = ''.join(tokens[1:]).split(',');

                        while (index < len(tokens)):
                            isValidVarName(tokens[index]);
                            variables[tokens[index]] = floatOrBoolOrString((input("Enter a value for " + tokens[index] + ": ")));

                            tempOut = variables[tokens[index]];
                            if (type(tempOut) == float):
                                    if ((int(tempOut) == tempOut)):
                                        tempOut = int(tempOut);
                                    else:
                                        tempOut = round(tempOut, 8);

                            output += f"Enter a value for {tokens[index]}: {tempOut}\n";
                            index += 1;

                    case "schreibe":
                        tokens[1:] = findall(r'(?:[^,"]|"[^"]*")+', betterJoin(tokens[1:], " "));

                        while (index < len(tokens)):
                            tokens[index] = tokens[index].strip();

                            if (tokens[index].startswith("\"") and tokens[index].endswith("\"")):
                                tempOut = tokens[index][1:-1].replace("\\n", "\n")
                                output += tempOut;
                                print(tempOut, end="");
                                afterText = True;

                            else:
                                tempOut = evalExpression(tokens[index], variables);
                                if (type(tempOut) == float):
                                    if ((int(tempOut) == tempOut)):
                                        tempOut = int(tempOut);
                                    else:
                                        tempOut = round(tempOut, 8);
                                if (afterText):
                                    output += str(tempOut);
                                    print(str(tempOut), end="");
                                    afterText = False;
                                else:
                                    tempOut = f"The value of '{tokens[index]}' is \"{tempOut}\"\n";
                                    output += tempOut;
                                    print(tempOut, end="");

                            index += 1;

                    case "falls":
                        condition = evalExpression(betterJoin(tokens[1:], ' '), variables);
                        blockInitiators[line.indent] = BlockInitiator(initiator="falls", condition=condition, enteredCase=False);
                        maxIndent += indentStep;

                    case "dann":
                        if ((not (line.indent - indentStep) in blockInitiators) or blockInitiators[line.indent - indentStep].initiator != "falls"):
                            raise Exception("expected 'falls' before 'dann'.");

                        if (len(tokens) > 1):
                            lines.insert(lineIndex+1, Line(betterJoin(tokens[1:], ' ')), line.index, line.indent + indentStep);
                            lines[lineIndex].text = (' ' * line.indent) + tokens[0];

                        if (blockInitiators[line.indent - indentStep].condition):
                            maxIndent += indentStep;
                        else:
                            #find next 'sonst' at the correct indent, otherwise move to end
                            i = lineIndex;
                            while ((i < len(lines)) and (len(lines[i].text) - len(lines[i].text.lstrip(' ')) >= line.indent)):
                                if (lines[i].text.lstrip(" ").startswith("sonst")):
                                    break;

                                i += 1;
                            lineIndex = i-1;

                    case "sonst":
                        if ((not (line.indent - indentStep) in blockInitiators) or blockInitiators[line.indent - indentStep].initiator != "falls"):
                            raise Exception("expected 'falls' before 'sonst'.");

                        if (len(tokens) > 1):
                            lines.insert(lineIndex+1, Line(betterJoin(tokens[1:], ' '), line.index, line.indent + indentStep));
                            line.text = (' ' * line.indent) + tokens[0];

                        if (not blockInitiators[line.indent - indentStep].condition):
                            maxIndent += indentStep;

                    case other if (colonIndex != -1):    #case
                        if ((not (line.indent - indentStep) in blockInitiators) or blockInitiators[line.indent - indentStep].initiator != "falls"):
                            raise Exception("expected 'falls' before case.");

                        initiator = blockInitiators[line.indent - indentStep];

                        if (len(tokens) > 1):
                            lines.insert(lineIndex+1, Line(betterJoin(tokens[colonIndex+1:], ' '), line.index, line.indent + indentStep));
                            line.text = (' ' * line.indent) + betterJoin(tokens[:colonIndex+1], ' ');
                            tokens = getAllTokens(line.text);

                        expression = [tokens[i] for i in range(len(tokens)-1)];
                        expression.append(tokens[-1][:-1]);

                        sonst = False;
                        if (tokens[0] == "sonst:"):
                            if (initiator.enteredCase):
                                lineIndex += 1;
                                continue;
                            
                            sonst = True;

                        if (sonst or initiator.condition == evalExpression(betterJoin(expression, ' '), variables)):
                            maxIndent += indentStep;
                            initiator.enteredCase = True;

                    case "solange":
                        if (tokens[-1] == "wiederhole"):
                            expression = betterJoin(tokens[1:-1], ' ');
                        else:
                            expression = betterJoin(tokens[1:], ' ');
                        condition = evalExpression(expression, variables);

                        if (tokens[-1] != "wiederhole"):
                            if (blockInitiators[line.indent].initiator != "wiederhole"):
                                raise Exception("expected 'wiederhole' at the end of the line.");
                            elif (condition):
                                lineIndex = blockInitiators[line.indent].index;
                                maxIndent -= indentStep;
                                continue;

                        if (condition):
                            blockInitiators[line.indent] = BlockInitiator(initiator="solange", condition=condition, index=lineIndex);
                            maxIndent += indentStep;
                        elif (line.indent in blockInitiators):
                            blockInitiators.pop(line.indent);

                    case "wiederhole":
                        maxIndent += indentStep;
                        blockInitiators[line.indent] = BlockInitiator(initiator="wiederhole", index=lineIndex);

                    case "für":
                        #only do this the first time
                        if (not line.indent in blockInitiators):
                            if (tokens[-1] != "wiederhole"):
                                raise Exception("expected 'wiederhole' at the end of the line.");
                            
                            if (len(tokens) < 3):
                                raise Exception("expected variable after 'für'.");
                            var = tokens[1];
                            if (len(tokens) < 4 or tokens[2] != 'von'):
                                raise Exception("expected 'von' after variable.");

                            if (not "bis" in tokens):
                                raise Exception("expected 'bis' after value.");
                            
                            bis_index = tokens.index('bis');
                            start = tokens[3:bis_index];
                            if (len(start) < 1):
                                raise Exception("expected a start value.");
                            variables[var] = evalExpression(betterJoin(start, ' '), variables);

                            if ("mit" in tokens):
                                mit_index = tokens.index("mit");
                            else:
                                mit_index = -1;

                            stop = tokens[bis_index+1:mit_index];
                            if (len(stop) < 1):
                                raise Exception("expected a stop value.");

                            if (mit_index != -1):
                                step = tokens[mit_index+1:-1];
                            else:
                                step = ["1"];

                            blockInitiators[line.indent] = BlockInitiator(initiator="für", var=var, stop=stop, step=step, index=lineIndex);
                        #on repeats
                        else:
                            variables[blockInitiators[line.indent].var] += evalExpression(betterJoin(blockInitiators[line.indent].step, ' '), variables);

                        if (variables[blockInitiators[line.indent].var] <= evalExpression(betterJoin(blockInitiators[line.indent].stop, ' '), variables)):
                            maxIndent = line.indent + indentStep;
                        else:
                            blockInitiators.pop(line.indent);

                    case other if (tokens[1].strip() == '='):
                        isValidVarName(tokens[0]);
                        variables[tokens[0]] = evalExpression(betterJoin(tokens[2:], ' '), variables);

                lineIndex += 1;

            if (sum([l.initiator for l in blockInitiators.values()].count(s) for s in ("solange", "für")) > 0):
                beginIndent = max(indentOfLastKey(blockInitiators, "solange"), indentOfLastKey(blockInitiators, "für"));
                lineIndex = blockInitiators[beginIndent].index;
                continue;
            #else
            break;

    except Exception as e:
        tempOut = f"Line {line.index}: {e}";
        print(tempOut);
        output += tempOut;
        return output;

    return output;

def main():
    inFile = open("in.txt", 'r');
    outFile = open("out.txt", 'w');

    allLines = [];
    i = 1;
    for line in inFile:
        line = line.rstrip('\n').rstrip(' ');
        indent = len(line) - len(line.lstrip(' '));
        line = line[indent:];
        if (line.endswith(';')):
            line = line[:-1];
        if (line != ""):
            allLines.append(Line(line, i, indent));
        i += 1;
    outputText = mainThread(allLines);

    outFile.write(outputText);
    inFile.close();
    outFile.close();

main();