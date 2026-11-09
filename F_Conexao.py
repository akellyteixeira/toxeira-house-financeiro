import streamlit as st
import paramiko
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os

load_dotenv(override=True)

## DECORADOR QUE GUARDA A CONEXAO EM CACHE
@st.cache_resource
def iniciar_conexao():
    if not hasattr(paramiko, 'DSSKey'):
        paramiko.DSSKey = paramiko.RSAKey
        
    tunnel = SSHTunnelForwarder(
        (os.getenv('SSH_HOST'), 22),
        ssh_username=os.getenv('SSH_USER'),
        ssh_password=os.getenv('SSH_PASSWORD'), 
        remote_bind_address=('127.0.0.1', 3306),
        host_pkey_directories=[]
    )
    tunnel.start()
    
    db_url = f"mysql+pymysql://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASSWORD'))}@127.0.0.1:{tunnel.local_bind_port}/"
    engine = create_engine(db_url)
    
    return engine