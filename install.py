import os
import subprocess
import sys
import venv

env_choice_text = \
"""
What kind of installation do you want (or that you already have in order to update):
    1 - (Not Implemented) Using conda (Recommended only if you have an NVIDIA GPU but don't want to manually install CUDA/CUDNN)
    2 - Using a virtual environment
"""
requirements_choice_text_conda = \
"""
What kind of requirements do you want ?:
    1 - RTX nvidia GPU (and want the maximum performance) (automatically install CUDNN)
    2 - Dedicated GPU
    3 - CPU only
"""
requirements_choice_text_venv = \
"""
What kind of requirements do you want ?:
    1 - RTX nvidia GPU (and want the maximum performance) (manually installed CUDNN)
    2 - Dedicated GPU
    3 - CPU only
"""
requirements_choice_text_cuda = \
"""
What is the version of CUDA that you currently have installed ?:
    1 - CUDA 11.8
    2 - CUDA 12.1
    3 - CUDA 12.4
(PS: You can check using the:'nvcc --version', if it's not installed simply use a letter to close the install prompt)
"""

venv_name = ".venv"

def create_virtualenv(env_name):
    """Create a virtual environment."""
    venv.create(env_name, with_pip=True)
    print(f"Virtual environment '{env_name}' created.")

def is_conda_installed():
    try:
        # Run the command 'conda --version' to check if Conda is installed
        result = subprocess.run(['conda', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # If the return code is 0, Conda is installed
        if result.returncode == 0:
            print("Conda is installed:", result.stdout.decode().strip())
        else:
            print("Conda is not installed.")
    except FileNotFoundError:
        print("Conda is not installed.")


def install_miniconda():
    """Install miniconda"""
    miniconda_file = "Miniconda3-latest-Windows-x86_64.exe"
    subprocess.run(["Invoke-WebRequest", 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe', "-OutFile", miniconda_file], check=True)
    subprocess.run(["Start-Process", miniconda_file, "-Wait", "-ArgumentList", "'@('/S', '/InstallationType=JustMe', '/RegisterPython=0', '/D='$Env:UserProfile/miniconda3'')'"], check=True)
    os.remove(miniconda_file)
    print("Conda is now installed")

def does_virtualenv_exists(env_name) -> bool:
    # Define the path to the venv configuration file
    venv_config_path = os.path.join(env_name, 'pyvenv.cfg')

    # Check if the venv configuration file exists
    if os.path.isfile(venv_config_path):
        print(f"A virtual environment exists in: {env_name}")
        return True
    else:
        print(f"No virtual environment found in: {env_name}")
        return False


def conda_main():
    if not is_conda_installed():
        install_miniconda()

def venv_main():
    if not does_virtualenv_exists(venv_name):
        create_virtualenv(venv_name)

    subprocess.run([os.path.join(venv_name, 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)

    choice: str = input(requirements_choice_text_venv)
    if not choice.isnumeric():
        raise ValueError
    choice: int = int(choice)
    match choice:
        case 1:
            requirements_file = "requirements-gpu.txt"
            subprocess.run([os.path.join(venv_name, 'Scripts', 'pip'), 'install', '--upgrade', '-r', requirements_file],
                           check=True)
            cuda_version_choice: str = input(requirements_choice_text_cuda)
            if not cuda_version_choice.isnumeric():
                raise ValueError
            cuda_version_choice: int = int(cuda_version_choice)
            match cuda_version_choice:
                case 1: # 11.8
                    subprocess.run([os.path.join(venv_name, 'Scripts', 'pip'), 'install', 'torch>=2.5.1','torchvision>=0.20.1 ','torchaudio>=2.5.1','xformers','--upgrade', '--index-url', 'https://download.pytorch.org/whl/cu118'],
                           check=True)
                case 2: # 12.1
                    subprocess.run([os.path.join(venv_name, 'Scripts', 'pip'), 'install', 'torch>=2.5.1','torchvision>=0.20.1 ','torchaudio>=2.5.1','xformers','--upgrade', '--index-url', 'https://download.pytorch.org/whl/cu121'],
                           check=True)
                case 3: # 12.4
                    subprocess.run([os.path.join(venv_name, 'Scripts', 'pip'), 'install', 'torch>=2.5.1','torchvision>=0.20.1 ','torchaudio>=2.5.1','xformers','--upgrade', '--index-url', 'https://download.pytorch.org/whl/cu124'],
                           check=True)

        case 2:
            requirements_file = "requirements-gpu.txt"
            subprocess.run([os.path.join(venv_name, 'Scripts', 'pip'), 'install', '--upgrade', '-r', requirements_file],
                           check=True)

        case 3:
            requirements_file = "requirements-cpu.txt"
            subprocess.run([os.path.join(venv_name, 'Scripts', 'pip'), 'install', '--upgrade', '-r', requirements_file],
                           check=True)

        case _:
            raise ValueError

    print("Requirements installed.")

def main():
    choice: str = input(env_choice_text)
    if not choice.isnumeric():
        raise ValueError
    choice: int = int(choice)
    match choice:
        case 1:
            conda_main()
        case 2:
            venv_main()
        case _:
            raise ValueError


if __name__ == "__main__":
    main()
