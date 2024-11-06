#!  /bin/bash

echo "Installing Requirements on a Linux platform"
echo "Make sure to have python3, recomended 3.10 or higher"


if ! command -v git &> /dev/null
then
    echo "git is not installed. Git is needed for some of the pip installs from source. Exiting..."
    exit 1
fi

echo "git is installed. Proceeding..."
# Your script continues here

# create venv
python3 -m venv .venv

# activate venv
source .venv/bin/activate



# check for if we're running inside a venv
if [[ "$VIRTUAL_ENV" != "" ]]; then
  INVENV=1
else
  INVENV=0
fi

# if we're in a venv install the requirements
if [[ $INVENV -eq 1 ]]; then

  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Running on Linux"
    pip install -r requirements.txt
  
    pip install wheel
    # base torch and xformers are installed in the requirements.txt and we upgrade it to the cuda version here
    # we need to install it later bc installing xformers overwrites it to the base torch
    pip install --upgrade torch==2.2.0 torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121

    pip install git+https://github.com/openai/CLIP.git


  elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Running on macOS"
    pip install -r requirements_mac.txt
    # no xformers
    pip install wheel
    # base torch is installed in the requirements.txt and we upgrade it to the cuda version here
    pip install --upgrade torch==2.2.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

    pip install git+https://github.com/openai/CLIP.git
  else
    echo "Unsupported OS"
  fi
  
  
else
  echo "failed to start virtualenv, do you have python3.xx-venv?"
fi


