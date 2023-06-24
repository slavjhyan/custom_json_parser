k_update_command = 'upd'
k_delete_command = 'del'
k_exit_command = 'exit'

k_commands = [k_update_command, k_delete_command]

def write_recursive(f, curr_dict: dict, curr_depth_count: int):
    for key, value in curr_dict.items():
        tabs = ''
        for i in range(0, curr_depth_count):
            tabs += '\t'
        line = tabs + '"' + key + '": '

        if type(value) is not dict:
            val = str(value)
            if type(value) == str:
                val = '"' + val + '"'
            line += val
            f.write(line + '\n')
        else:
            line += '{'
            f.write(line + '\n')
            write_recursive(f, curr_dict[key], curr_depth_count + 1)
            f.write(tabs + '}\n')

def update_file(json_dict: dict, file_path):
    with open(file_path, "w") as f:
        f.truncate(0)
        f.write('{\n')
        write_recursive(f, json_dict, 1)
        f.write('}\n')

def execute_instruction(json_dict: dict, command, elem_path: list, new_val):
    nested_dict = json_dict
    for i in range(len(elem_path) - 1):
        if elem_path[i] not in nested_dict:
            print('\nerror: path "{}" is invalid\n\n'.format(elem_path))
            return False
        nested_dict = nested_dict[elem_path[i]]

    key = elem_path[-1]
    if key in nested_dict and not command:
        print('\nkey "{}" is already present\n\n'.format(key))
        return False
    if key not in nested_dict and command:
        print('\nkey "{}" is not found\n\n'.format(key))
        return False
    
    if new_val and str(new_val).isdigit():
        new_val = int(new_val)

    if not command:
        nested_dict[key] = new_val
    elif command == k_update_command:
        nested_dict[key] = new_val
    elif command == k_delete_command:
        del nested_dict[key]
    else:
        print('\ninvalid command "{}"\n\n'.format(command))
        return False

    return True


def valid_key_name(new_key: str):
    for ch in new_key:
        if not ch.isalnum() and ch != '_':
            return False
    return True

def insert_key_value_pair(json_dict: dict, line: str, lineIx: int, curr_depth_pos: list):
    key_end_ix = line.find('"', 1)
    if key_end_ix == -1:
        print('error: syntax error in line {}`\n\t"{}"\n\n'.format(lineIx + 1, line))

    new_key = line[1:key_end_ix]
    if not valid_key_name(new_key):
        print('error: "{}" is not a valid key name in line {}\n\n'.format(new_key, lineIx + 1))
        exit()

    sep_ix = line.find(':', key_end_ix)
    if sep_ix == -1:
        print('error: value not provided for key "{}" in line {}\n\n'.format(new_key, lineIx + 1))
    
    value = line[sep_ix + 1:].strip()

    nested_dict = json_dict
    for key in curr_depth_pos:
        nested_dict = nested_dict[key]

    if value == '{':
        nested_dict[new_key] = {}
        curr_depth_pos.append(new_key)
    elif value[0] == '"' and value[-1] == '"':
        nested_dict[new_key] = value[1:-1]
    elif value.isalnum():
        nested_dict[new_key] = int(value)
    else:
        print('error: invalid value "{}" for key "{}" in line {}\n\n'.format(value, new_key, lineIx + 1))


def parse_instruction(instr: str):
    if instr.strip() == k_exit_command:
        print("\nbye\n")
        exit()

    components = instr.split()

    elem_path_ix = components[0] in k_commands
    elem_path = components[elem_path_ix].split('.')
    command = components[0] if elem_path_ix else None

    ix = elem_path[-1].find('=')
    if ix != -1:
        if elem_path[-1].count('=') != 1 or command == k_delete_command:
            return False
    
        if ix == len(elem_path[-1]) - 1:
            if elem_path_ix != len(components) - 2:
                return False
            new_val = components[-1]
            elem_path[-1] = elem_path[-1][0:-1]
        else:
            new_val = elem_path[-1][ix + 1:]
            elem_path[-1] = elem_path[1][0:ix]
    elif '=' in components:
        if (components.count('=') > 1 or
            components.index('=') != elem_path_ix + 1 or
            components.index('=') != len(components) - 2):
            return False
        new_val = components[-1]
    elif command == k_delete_command:
        if elem_path_ix != len(components) - 1:
            print('\ninvalid instruction\n\n')
        new_val = None
    else:
        if (elem_path_ix != len(components) - 2 or
            components[-1][0] != '='):
            return False
        new_val = components[-1][1:]

    return [command, elem_path, new_val]


def read_file(file_path):
    curr_depth_pos = []
    with open(file_path, 'r') as f:
        if f.readline().strip() != '{':
            print('error: wrong syntax at first line(expected only "{")\n\n')
            exit()

        json_dict = {}
        for i, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue
            if line[0] == '"':
                insert_key_value_pair(json_dict, line, i, curr_depth_pos)
            elif line[0] == '}':
                if curr_depth_pos:
                    curr_depth_pos.pop()
            else:
                print('error: invalid syntax for line {}`\n\t{}\n\n'.format(i + 1, line))
                exit()

    return json_dict


def execute(file_path):
    json_dict = read_file(file_path)
    print('\nfile read successfully!\n\n')

    while True:
        instruction = input()
        parse_result = parse_instruction(instruction)
        if parse_result:
            execute_instruction(json_dict, parse_result[0], parse_result[1], parse_result[2])
            update_file(json_dict, file_path)
        else:
            print('\ninvalid instruction\n\n')
