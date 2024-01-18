set -e

handle_error() {
    echo "An error occurred in the script! See the traceback above."
    # having this here, maybe I had more functionality later
    exit 1
}

clean_up(){
    echo "Executing clean up"
    if [ -d "venv" ]; then
        rm -r venv
    fi
}

# set traps
trap 'handle_error' ERR
trap 'clean_up' EXIT

# setup your dependencies here
echo "Creating a venv"
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt