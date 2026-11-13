module.exports = {
  apps : [
  {
    name   : "financeiro-1",
    script : "/root/Desktop/PROJETOS/SITE_CONTAGEM/CONTAGEM_LOJA/.venv/bin/python",
    args   : "-m streamlit run PAGINA_LOGIN.py",
    watch  : false,
    env: {
      STREAMLIT_SERVER_PORT: "8506",
      STREAMLIT_SERVER_ADDRESS: "0.0.0.0",
      STREAMLIT_SERVER_HEADLESS: "true"
    }
  },
  
  {
    name   : "financeiro-2",
    script : "/root/Desktop/PROJETOS/SITE_CONTAGEM/CONTAGEM_LOJA/.venv/bin/python",
    args   : "-m streamlit run PAGINA_LOGIN..py",
    watch  : false,
    env: {
      STREAMLIT_SERVER_PORT: "8507",
      STREAMLIT_SERVER_ADDRESS: "0.0.0.0",
      STREAMLIT_SERVER_HEADLESS: "true"
    }
  }  
  ]
}

