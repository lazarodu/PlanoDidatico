from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, JSON, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infra.database import Base

class UsuarioModel(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    tipo = Column(String, nullable=False)  # admin, coordenador, professor

    professor_rel = relationship("ProfessorModel", back_populates="usuario_rel", uselist=False)
    preference_rel = relationship("NotificationPreferenceModel", back_populates="usuario_rel", uselist=False)


class ProfessorModel(Base):
    __tablename__ = "professor"

    usuario_id = Column(Integer, ForeignKey("usuario.id"), primary_key=True)
    matricula = Column(String, nullable=False)
    departamento = Column(String, nullable=False, default="DECOM")

    usuario_rel = relationship("UsuarioModel", back_populates="professor_rel")


class DisciplinaModel(Base):
    __tablename__ = "disciplina"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    natureza = Column(String, default="Obrigatória")
    area_formacao = Column(String, default="Específica")
    departamento = Column(String, default="DECOM")


class PeriodoLetivoModel(Base):
    __tablename__ = "periodo_letivo"

    id = Column(Integer, primary_key=True, index=True)
    ano = Column(Integer, nullable=False)
    semestre = Column(Integer, nullable=False)
    ativo = Column(Boolean, default=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    data_limite_entrega_plano = Column(Date, nullable=False)
    minutos_por_dia_letivo = Column(Integer, default=100)


class AtribuicaoModel(Base):
    __tablename__ = "atribuicao_professor_disciplina"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplina.id"), nullable=False)
    periodo_letivo_id = Column(Integer, ForeignKey("periodo_letivo.id"), nullable=False)
    horario = Column(String, default="")

    dias_letivos = relationship("DiaLetivoModel", back_populates="atribuicao_rel", cascade="all, delete-orphan")


class DiaLetivoModel(Base):
    __tablename__ = "dia_letivo_disciplina"

    id = Column(Integer, primary_key=True, index=True)
    atribuicao_id = Column(Integer, ForeignKey("atribuicao_professor_disciplina.id"), nullable=False)
    data = Column(Date, nullable=False)
    turno = Column(String, default="matutino")

    atribuicao_rel = relationship("AtribuicaoModel", back_populates="dias_letivos")


class DidacticPlanModel(Base):
    __tablename__ = "didactic_plans"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplina.id"), nullable=False)
    periodo_letivo_id = Column(Integer, ForeignKey("periodo_letivo.id"), nullable=False)
    status = Column(String, default="PENDENTE")
    data_entrega = Column(Date, nullable=True)
    campos = Column(JSON, nullable=False, default={})


class CampoFormularioModel(Base):
    __tablename__ = "campo_formulario"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    obrigatorio = Column(Boolean, default=False)
    ordem = Column(Integer, default=0)
    opcoes = Column(JSON, nullable=True)


class NotificationPreferenceModel(Base):
    __tablename__ = "notification_preference"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), unique=True, nullable=False)
    canal_email = Column(Boolean, default=True)
    canal_telegram = Column(Boolean, default=False)
    chat_id_telegram = Column(String, nullable=True)
    horario_preferido = Column(Time, nullable=True)

    usuario_rel = relationship("UsuarioModel", back_populates="preference_rel")


class NotificationLogModel(Base):
    __tablename__ = "notification_log"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    atribuicao_id = Column(Integer, ForeignKey("atribuicao_professor_disciplina.id"), nullable=True)
    canal = Column(String, nullable=False)
    status = Column(String, nullable=False)
    mensagem_erro = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.now)
