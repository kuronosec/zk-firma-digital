import subprocess
import os
import random
import string
import uuid

PUBLIC_ENTROPY = "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"


def gen_ptau_file(working_dir):
    return os.path.join(working_dir, str(uuid.uuid4()) + ".ptau")


class PTau:
    """
    Manages creating and contributing to a powers of tau ceremony.

    Args:
        ptau_file (str, optional): Path to a previously generated powers of tau ceremony file.
        working_dir (str, optional): Path that all given file paths are relative to. Defaults to the current directory

    """

    def __init__(self, ptau_file=None, working_dir="./"):
        if ptau_file is None:
            ptau_file = gen_ptau_file(working_dir)
        self.working_dir = working_dir
        self.old_files = []
        self.ptau_file = ptau_file
        # Check what operation system we re running on
        self.snarkjs_command = "snarkjs"
        if os.name == 'nt':
            self.snarkjs_command = "snarkjs.cmd"

    # Begins a power of tau ceremony, curve is the curve to use
    # and constraints is the number of constraints raised to the power of 2
    def start(self, curve='bn128', constraints='12'):
        """Initializes a powers of tau ceremony

        Args:
            curve (str, optional): Curve to use in the powers of tau ceremony. Defaults to the `bn128` curve.
            constraints (str, optional): The number of constraints supported by the powers of tau ceremony raised to the power of 2.
        """
        # snarkjs powersoftau new bn128 14 pot14_0000.ptau -v
        proc = subprocess.run(
            [self.snarkjs_command, 'powersoftau', 'new', curve, constraints, self.ptau_file, "-v"],
            capture_output=True,
            cwd=self.working_dir,
        )
        if proc.returncode != 0:
            raise ValueError(proc.stdout.decode('utf-8'))

    # Contributes randomness (entropy) to power of tau ceremony
    def contribute(self, name="", entropy="", output_file=None):
        """Contributes to the powers of tau ceremony

        Args:
            name (str, optional): Name of the contribution.
            entropy (str, optional): Random text to use as entropy in the contribution. Defaults to random lowercase letters.
            output_file (str, optional): Path of where the ptau file should be outputted to.

        """
        if output_file is None:
            output_file = gen_ptau_file(self.working_dir)
        # If no random text is supplied, generate 100 random characters
        if entropy == "":
            entropy = ''.join(random.choices(string.ascii_lowercase, k=100))
        if entropy[-1] != "\n":
            entropy += "\n"
        proc = subprocess.run(
            [
                self.snarkjs_command,
                "powersoftau",
                "contribute",
                self.ptau_file,
                output_file,
                f'--name="{name}"',
                "-v",
                f'-e={entropy}',
            ],
            capture_output=True,
            check=True,
            cwd=self.working_dir,
        )
        if proc.returncode != 0:
            raise ValueError(proc.stdout.decode('utf-8'))
        self.old_files.append(self.ptau_file)
        self.ptau_file = output_file

    # Handle import / export contributions from 3rd party software
    def export_challenge(self, output_file):
        """Export a challenge that can be sent to third party software.

        Args:
            output_file (str, optional): Path of where the challenge file should be outputted to.
        """
        proc = subprocess.run(
            [self.snarkjs_command, "powersoftau", "export", "challenge", self.ptau_file, output_file],
            capture_output=True,
            check=True,
            cwd=self.working_dir,
        )
        if proc.returncode != 0:
            raise ValueError(proc.stderr.decode('utf-8'))
        return output_file

    def contribute_challenge(self, challenge, output_file, entropy, curve='bn128'):
        """Contribute to a challenge and produce a response.

        Args:
            output_file (str, optional): Path of where the response file should be outputted to.
            entropy (str): Random text to serve as entropy to the contribution
            curve (str, optional): Specifies which cryptographic curve to use. Defaults to the `bn128` curve.
        """
        proc = subprocess.run(
            [self.snarkjs_command, "powersoftau", "challenge", "contribute", curve, challenge, output_file, f"-e={entropy}"],
            capture_output=True,
            check=True,
            cwd=self.working_dir,
        )
        if proc.returncode != 0:
            raise ValueError(proc.stderr.decode('utf-8'))
        return output_file

    def import_response(self, response, output_file=None):
        """Import a response.

        Args:
            response (str, optional): Path to response file to use as input.
            output_file (str, optional): Path of where the response file should be outputted to.
        """
        if output_file is None:
            output_file = gen_ptau_file(self.working_dir)
        proc = subprocess.run(
            [self.snarkjs_command, "powersoftau", "import", "response", self.ptau_file, response, output_file],
            capture_output=True,
            check=True,
            cwd=self.working_dir,
        )
        if proc.returncode != 0:
            raise ValueError(proc.stderr.decode('utf-8'))
        self.old_files.append(self.ptau_file)
        self.ptau_file = output_file

    # Finalizes phase 1 of the power of tau ceremony
    def beacon(self, output_file=None, public_entropy=PUBLIC_ENTROPY, iter=10):
        """Finalize phase 1 of the powers of tau ceremony.

        Args:
            output_file (str, optional): Path of where the ptau file should be outputted to.
            public_entropy (str, optional): Public entropy to use in the beacon. Defaults to `0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f`
            iter (int): Specifies how many iterations to use in the beacon.
        """
        if output_file is None:
            output_file = gen_ptau_file(self.working_dir)
        proc = subprocess.run(
            [self.snarkjs_command, "powersoftau", "beacon", self.ptau_file, output_file, public_entropy, str(iter)],
            capture_output=True,
            check=True,
            cwd=self.working_dir,
        )
        if proc.returncode != 0:
            raise ValueError(proc.stdout.decode('utf-8'))
        self.old_files.append(self.ptau_file)
        self.ptau_file = output_file

    def prep_phase2(self, output_file=None):
        """Prepare for phase 2 of the powers of tau ceremony.

        Args:
            output_file (str, optional): Path of where the ptau file should be outputted to.

        """
        if output_file is None:
            output_file = gen_ptau_file(self.working_dir)
        proc = subprocess.run(
            [self.snarkjs_command, "powersoftau", "prepare", "phase2", self.ptau_file, output_file, "-v"],
            capture_output=True,
            check=True,
            cwd=self.working_dir,
        )
        if proc.returncode != 0:
            raise ValueError(proc.stdout.decode('utf-8'))
        self.old_files.append(self.ptau_file)
        self.ptau_file = output_file

    def verify(self):
        """Verfies the power of tau ceremony is valid."""
        proc = subprocess.run([self.snarkjs_command, "powersoftau", "verify", self.ptau_file], capture_output=True, check=True)
        print(proc.stdout.decode('utf-8'))
        if proc.returncode == 0:
            return True
        else:
            return False

    def cleanup(self):
        """Deletes old/intermediate powers of tau files"""
        for file in self.old_files:
            os.remove(file)


if __name__ == "__main__":
    ptau = PTau(working_dir='./tmp')
    print("Starting powers of tau")
    ptau.start()
    print("Contribute")
    ptau.contribute()
    print("Beacon")
    ptau.beacon()
    print("Phase2")
    ptau.prep_phase2()
    print("Verify")
    ptau.verify()
    print(ptau.ptau_file)
