# Arquivo: database.py
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import config  # <--- Importamos o arquivo novo

Base = declarative_base()

class LeituraDB(Base):
    __tablename__ = 'leituras'
    id = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, default=datetime.now)
    temperatura = Column(Float)
    umidade = Column(Float)

class RepositorioSensor:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.conectado = False
        self._conectar()

    def _conectar(self):
        try:
            # --- MÁGICA AQUI: Montamos a string dinamicamente ---
            # f-string junta tudo: mariadb+driver://user:senha@host:porta/banco
            conn_str = (
                f"mariadb+mariadbconnector://"
                f"{config.DB_USER}:{config.DB_PASS}"
                f"@{config.DB_HOST}:{config.DB_PORT}"
                f"/{config.DB_NAME}"
            )
            
            # Cria a conexão usando a string montada
            self.engine = create_engine(conn_str, echo=False)
            
            # Cria tabelas se não existirem
            Base.metadata.create_all(self.engine)
            
            self.Session = sessionmaker(bind=self.engine)
            self.conectado = True
            print(f"✅ [Database] Conectado em {config.DB_HOST}:{config.DB_PORT}")
            
        except ImportError:
             print("⚠️ Erro: Biblioteca 'mariadb' não encontrada. Instale: pip install mariadb")
             self.conectado = False
        except Exception as e:
            print(f"⚠️ [Database] Erro ao conectar: {e}")
            print("   -> Sistema rodando OFFLINE (Sem salvar histórico).")
            self.conectado = False

    def salvar_leitura(self, temp, umid):
        if not self.conectado: return
        session = self.Session()
        try:
            nova = LeituraDB(temperatura=temp, umidade=umid)
            session.add(nova)
            session.commit()
        except Exception as e:
            print(f"❌ Erro SQL: {e}")
            session.rollback()
        finally:
            session.close()