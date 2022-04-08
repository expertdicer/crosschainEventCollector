## Create environment
python3 -m venv .venv

## Install requirements
pip3 install -r requirements.txt

## Run
python3 ethereumetl.py

python3 ethereumetl.py stream_event_collector -l "last_synced_block_file" -n "rinkeby" -cn "all" -b 100 -B 500 -o "mongodb://localhost:27017/"