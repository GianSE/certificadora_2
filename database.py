# Arquivo: database.py
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class LeituraDB(Base):
    __tablename__ = 'leituras'
    id = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, default=datetime.now)
    
    # Grandezas Físicas
    temperatura = Column(Float)
    umidade = Column(Float)
    luminosidade = Column(Integer)  # <--- NOVO: Valor bruto do LDR
    
    # Status dos Atuadores
    bomba = Column(Boolean)
    fan = Column(Boolean)
    luz_painel = Column(Boolean)

class RepositorioSensor:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.conectado = False
        self._conectar()

    def _conectar(self):
        try:
            conn_str = f"mariadb+mariadbconnector://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
            self.engine = create_engine(conn_str, echo=False)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.conectado = True
            print(f"✅ [Database] Conectado.")
        except Exception as e:
            print(f"⚠️ [Database] Erro: {e}")

    def salvar_leitura(self, temp, umid, lum, bomba, fan, luz): # <--- Adicionado lum
        if not self.conectado: return
        session = self.Session()
        try:
            nova = LeituraDB(
                temperatura=temp, 
                umidade=umid,
                luminosidade=lum, # <--- Salva no banco
                bomba=bomba,
                fan=fan,
                luz_painel=luz
            )
            session.add(nova)
            session.commit()
        except Exception as e:
            print(f"❌ Erro SQL: {e}")
            session.rollback()
        finally:
            session.close()

    def buscar_historico(self, data_inicio, data_fim):
        # (Mesma lógica, não muda nada aqui, o objeto já vem com o campo novo)
        if not self.conectado: return []
        session = self.Session()
        try:
            return session.query(LeituraDB).filter(
                LeituraDB.data_hora >= data_inicio,
                LeituraDB.data_hora <= data_fim
            ).order_by(LeituraDB.data_hora.asc()).all()
        finally:
            session.close()