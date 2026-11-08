python -m venv venv
py -3.13 -m venv .venv | Setup python 3.13.15 specific environment
./.venv/Scripts/activate.ps1 | Windows
./venv/bin/activate | Linux \ mac
pip install -r ./project_setup/requirements.txt | Install depencies
python -m pip install "psycopg[binary]"
ollama
ollama pull llama3.2 | LLM
ollama pull mxbai-embed-large | embedding model
ollama list
python -m tests.test_rag |bcz current architectre is packaged based. Instead of: python tests/test_rag.py
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload | start fast api server with mobile interactive extension 
python -m gui.main
uvicorn api.server:app --reaload | start api backend without interactive mobile extension