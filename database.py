# Arquivo: database.py
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, Boolean # <--- Adicionado Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class LeituraDB(Base):
    __tablename__ = 'leituras'
    id = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, default=datetime.now)
    
    # Dados Ambientais
    temperatura = Column(Float)
    umidade = Column(Float)
    
    # Status dos Equipamentos (Novos campos)
    bomba = Column(Boolean)       # True = Ligado, False = Desligado
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
            conn_str = (
                f"mariadb+mariadbconnector://"
                f"{config.DB_USER}:{config.DB_PASS}"
                f"@{config.DB_HOST}:{config.DB_PORT}"
                f"/{config.DB_NAME}"
            )
            self.engine = create_engine(conn_str, echo=False)
            Base.metadata.create_all(self.engine) # Cria tabela com colunas novas
            self.Session = sessionmaker(bind=self.engine)
            self.conectado = True
            print(f"✅ [Database] Conectado (Tabela 'leituras' atualizada)")
            
        except Exception as e:
            print(f"⚠️ [Database] Erro: {e}")
            self.conectado = False

    def salvar_leitura(self, temp, umid, bomba, fan, luz):
        if not self.conectado: return
        session = self.Session()
        try:
            nova = LeituraDB(
                temperatura=temp, 
                umidade=umid,
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
        if not self.conectado: return []
        session = self.Session()
        try:
            return session.query(LeituraDB).filter(
                LeituraDB.data_hora >= data_inicio,
                LeituraDB.data_hora <= data_fim
            ).order_by(LeituraDB.data_hora.asc()).all()
        finally:
            session.close()