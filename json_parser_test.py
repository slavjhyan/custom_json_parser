import os
import time
import random
import datetime

from yani_json_parser import update_file, execute_instruction, read_file, k_commands

k_letters = 'abcdefghijklemnopqrstuvwxyz'
k_digits = '0123456789'

random.seed(datetime.datetime.now().timestamp())

def generate_file_name():
    extension = '.gen.txt'
    file_name = random.choices(k_letters + k_digits, k=10)
    file_name += str(time.time_ns())

    return 'gen/' + ''.join(file_name) + extension


def get_last_pos_dict(dict, depth):
    nested_dict = dict
    for key in depth:
        nested_dict = nested_dict[key]
    return nested_dict


def random_new_value():
    b_int_val = random.getrandbits(1)
    if b_int_val:
        new_val = int(''.join(random.choices(k_digits, k=random.randint(1, 20))))
    else:
        new_val = ''.join(random.choices(k_digits + k_letters, k=random.randint(1, 20)))

    return new_val


def random_new_key():
    return ''.join(random.choices(k_letters, k=random.randint(5, 20)))


def generate_json_dict(json_size, ix=0, json_dict={}, curr_depth=[]):
    if ix >= json_size:
        return get_last_pos_dict(json_dict, curr_depth)

    new_key = random_new_key()
    b_dict_value = random.getrandbits(1)
    if not b_dict_value:
        new_val = random_new_value()
    else:
        get_last_pos_dict(json_dict, curr_depth)[new_key] = {}
        curr_depth.append(new_key)
        value_dict_size = random.randint(1, json_size - ix)
        new_val = generate_json_dict(value_dict_size, json_dict=json_dict, curr_depth=curr_depth)
        ix += value_dict_size
        curr_depth.pop()

    curr_pos = get_last_pos_dict(json_dict, curr_depth)
    curr_pos[new_key] = new_val

    generate_json_dict(json_size=json_size, ix=ix+1, json_dict=json_dict, curr_depth=curr_depth)

    return get_last_pos_dict(json_dict, curr_depth)


def random_json_file():
    json_size = random.randint(1, 10)
    json_dict = generate_json_dict(json_size)
    file_path = generate_file_name()
    update_file(json_dict, file_path)
    return [json_dict, file_path]


def generate_json_files(count):
    res = {}
    for i in range(0, count):
        [dict, file_path] = random_json_file()
        res[file_path] = dict

    return res


def generate_instruction(dict: dict):
    command = k_commands[random.randint(0, len(k_commands) - 1)]
    command = random.choice([command, None])
    
    if command:
        key, _ = random.choice(list(dict.items()))
    else:
        key = random_new_key()

    new_val = None
    if command != 'del':
        new_val = random_new_value()

    return [command, [key], new_val]


def delete_generated_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    directory_path = os.path.join(current_dir, 'gen')

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def test_parser():
    delete_generated_files()
    k_test_count = 100
    gen_files = generate_json_files(k_test_count)
    failed_tests = []

    test_num = 1
    for path, dict in gen_files.items():
        instruction_count = 10
    
        for i in range(0, instruction_count):
            gen_instruction = generate_instruction(dict)
            execute_instruction(dict, gen_instruction[0], gen_instruction[1], gen_instruction[2])
    
        update_file(dict, path)
        updated_dict = read_file(path)
        if updated_dict == dict:
            print('Test {}/{} passed.\n'.format(test_num, k_test_count))
        else:
            print('Test {}/{} failed.\n'.format(test_num, k_test_count))
            failed_tests.append(path)
        test_num += 1

    if len(failed_tests) == 0:
        print('\n\n\t\t!!! All tests have passed !!!\n')
    else:
        print('Failed tests`\n')
        for path in failed_tests:
            print('\t{}\n'.format(path))


def __main__():
    test_parser()


__main__()
