import os
import uuid


def gen_rand_filename():
    return str(uuid.uuid4())


def gen_rand_zkey_file():
    return gen_rand_filename() + ".zkey"


def get_basename(file):
    return os.path.basename(file).split('.')[0]


def get_r1cs_file_base(circ_file):
    return get_basename(circ_file) + ".r1cs"


def get_sym_file_base(circ_file):
    return get_basename(circ_file) + ".sym"


def get_js_dir_base(circ_file):
    return get_basename(circ_file) + "_js"


def get_wasm_file_base(circ_file):
    return os.path.join(get_js_dir_base(circ_file), get_basename(circ_file) + ".wasm")


def add_output_dir(output_dir, file_path):
    return os.path.join(output_dir, file_path)


def get_r1cs_file(circ_file, output_dir):
    return add_output_dir(output_dir, get_r1cs_file_base(circ_file))


def get_sym_file(circ_file, output_dir):
    return add_output_dir(output_dir, get_sym_file_base(circ_file))


def get_js_dir(circ_file, output_dir):
    return add_output_dir(output_dir, get_js_dir_base(circ_file))


def get_wasm_file(circ_file, output_dir):
    return add_output_dir(output_dir, get_wasm_file_base(circ_file))


def exists(file):
    return os.path.isfile(file)
