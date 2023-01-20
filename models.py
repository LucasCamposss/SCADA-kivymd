from db import Base
from sqlalchemy import Column, Integer, DateTime

class DadoCLP(Base):
    """
    Modelo dos dados do CLP
    """ 
    __tablename__='dadosclp'
    id = Column(Integer,primary_key=True,autoincrement=True)
    timestamp = Column(DateTime)
    t_part = Column(Integer)
    freq_des = Column(Integer)
    freq_mot = Column(Integer)
    tensao = Column(Integer)
    rotacao = Column(Integer)
    pot_entrada = Column(Integer)
    corrente = Column(Integer)
    temp_estator = Column(Integer)
    vel_esteira = Column(Integer)
    carga = Column(Integer)
    peso_obj = Column(Integer)
    cor_obj_R = Column(Integer)
    cor_obj_G = Column(Integer)
    cor_obj_B = Column(Integer)
    numObj_est_1 = Column(Integer)
    numObj_est_2 = Column(Integer)
    numObj_est_3 = Column(Integer)
    numObj_est_nc = Column(Integer)
    

    def dadoDicionario(self):
        
            dic = {'timestamp':self.timestamp,
            't_part': self.t_part,
            'freq_des': self.freq_des,
            'freq_mot':self.freq_mot,
            'tensao': self.tensao,
            'rotacao':self.rotacao,
            'pot_entrada': self.pot_entrada,
            'corrente': self.corrente ,
            'temp_estator': self.temp_estator,
            'vel_esteira': self.vel_esteira,
            'carga': self.carga,
            'peso_obj': self.peso_obj,
            'cor_obj_R':self.cor_obj_R,
            'cor_obj_G': self.cor_obj_G ,
            'cor_obj_B':self.cor_obj_B,
            'numObj_est_1': self.numObj_est_1,
            'numObj_est_2': self.numObj_est_2,
            'numObj_est_3': self.numObj_est_3,
            'numObj_est_nc': self.numObj_est_nc
            }
            return dic