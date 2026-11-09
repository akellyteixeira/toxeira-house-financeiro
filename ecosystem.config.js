module.exports = {
  apps : [
  {
    name   : "denuncias-dc-1",
    script : "/root/Desktop/PROJETOS/SITE_CONTAGEM/CONTAGEM_LOJA/.venv/bin/python",
    args   : "-m streamlit run APP_PAGES_USU.py",
    watch  : false,
    env: {
      STREAMLIT_SERVER_PORT: "8504",
      STREAMLIT_SERVER_ADDRESS: "0.0.0.0",
      STREAMLIT_SERVER_HEADLESS: "true"
    }
  },
  
  {
    name   : "denuncias-dc-2",
    script : "/root/Desktop/PROJETOS/SITE_CONTAGEM/CONTAGEM_LOJA/.venv/bin/python",
    args   : "-m streamlit run APP_PAGES_USU.py",
    watch  : false,
    env: {
      STREAMLIT_SERVER_PORT: "8505",
      STREAMLIT_SERVER_ADDRESS: "0.0.0.0",
      STREAMLIT_SERVER_HEADLESS: "true"
    }
  }  
  ]
}

