from kivymd.app import MDApp
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix import snackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock
from timeseriesgraph import TimeSeriesGraph
from kivy_garden.graph import LinePlot
import random
from pyModbusTCP.client import ModbusClient
from time import sleep
from datetime import datetime
from threading import Thread, Lock
from db import Session, Base, engine
from models import DadoCLP
import pickle
from kivy.core.window import Window
from kivymd.uix.card import MDSeparator
from kivymd.uix.picker import MDTimePicker, MDThemePicker, MDDatePicker




class MyWidget(MDScreen):
    """
    Construtor
    """
    _updateThread = None
    _updateWidgets = True
    _tags = {}
    _max_points = 20
    _buscardados = False
    _obj = False
    _obj1 = False
    _numobj = [0,0,0,0]
    _dinicial = None
    _hinicial = None
    _dfinal = None
    _hfinal = None
    _esteira = 5

    def __init__(self, **kwargs):
        super().__init__()
        self._serverIP = kwargs.get('server_ip')
        self._port = kwargs.get('server_port')
        self._scan_time = kwargs.get('scan_time')
        self._modclient = ModbusClient()
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        self._lock = Lock()    

        for key,value in kwargs.get('modbus_addrs').items():
            plot_color = (random.random(),random.random(),random.random(),1)
            self._tags[key] = {'addr': value[0], 'color': plot_color, 'multiplicador': value[1]}
            if self._tags[key]['addr'] < 810 and self._tags[key]['addr'] > 799:
                if key != 'estado_atuador' and key != 'bt_Desliga/Liga':
                    cb = LabeledCheckBoxHistGraph()
                    if key == 'freq_mot' :
                        cb.ids.label.text = 'Frequência'
                        cb.ids.label.font_size = 9
                    elif key == 'tensao' :
                        cb.ids.label.text = 'Tensão'
                    elif key == 'rotacao' :
                        cb.ids.label.text = 'Rotação Motor'
                    elif key == 'pot_entrada' :
                        cb.ids.label.text = 'Pot. Entrada'
                    elif key == 'corrente' :
                        cb.ids.label.text = 'Corrente'
                    elif key == 'temp_estator' :
                        cb.ids.label.text = 'Temp. Estator'
                    elif key == 'vel_esteira' :
                        cb.ids.label.text = 'Vel. Esteira'
                    elif key == 'carga' :
                        cb.ids.label.text = 'Peso Norm.'
                    elif key == 'peso_obj' :
                        cb.ids.label.text = 'Peso Obj.'
                    cb.ids.label.color = plot_color
                    cb.ids.checkbox.group = "hist"
                    cb.id = key
                    self.ids.sensores.add_widget(cb)
                    self.ids.sensores.add_widget(MDSeparator(orientation = 'vertical'))

        cb = LabeledCheckBoxHistGraph()
        cb.ids.label.text = 'Cor Obj.'
        cb.ids.label.color = plot_color
        cb.ids.checkbox.group = "hist"
        cb.id = 'Cor_obj'
        self.ids.sensores.add_widget(cb)

        self._tags['cor_obj_R']['color'] = (1,0,0,1)
        self._tags['cor_obj_B']['color'] = (0,0,1,1)
        self._tags['cor_obj_G']['color'] = (0,1,0,1)

        self.plot1 = LinePlot(line_width=1.5,color= (0,0,1,1))
        self.plot2 = LinePlot(line_width=1.5,color= (0,1,0,1))
        self.plot3 = LinePlot(line_width=1.5,color= (1,0,0,1))
        self.ids.graph1.add_plot(self.plot1)
        self.ids.graph1.add_plot(self.plot2)
        self.ids.graph1.add_plot(self.plot3)
        self.ids.graph1.label_options.color = (0,0,0,1)
 


        self.ids.graph.label_options.color = (0,0,0,1)   
        self.plot = LinePlot(line_width=1.5,color= (0,0,0,1))
        self.ids.graph2.add_plot(self.plot)
        self.ids.graph2.label_options.color = (0,0,0,1)



        

        self.carregaConfig()

        self._session = Session()
        Base.metadata.create_all(engine)

    def show_theme_picker(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()
        

    def show_time_picker(self):
        '''Open time picker dialog.'''

        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.get_time , on_cancel=self.on_cancel)
        time_dialog.open()
        

    def show_time_picker2(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.get_time2 , on_cancel=self.on_cancel)
        time_dialog.open()


    def on_save(self, instance, value, date_range):
  
        self.show_time_picker()
        self._dinicial = value

    def on_save2(self, instance, value, date_range):
  
        self.show_time_picker2()
        self._dfinal = value
    
    def get_time(self, instance, time):
        self.show_date_picker2()
        self._hinicial = time
        
    
    def get_time2(self, instance, time):
        self._hfinal = time
        self.ids.txt_final_time.text = datetime.strftime(self._dfinal, '%d/%m/%Y') + ' ' + str(self._hfinal)
        self.ids.txt_init_time.text = datetime.strftime(self._dinicial, '%d/%m/%Y') + ' ' + str(self._hinicial)

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save , on_cancel=self.on_cancel)
        date_dialog.open()


    def show_date_picker2(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save2, on_cancel=self.on_cancel)
        date_dialog.open()

    
    def criar_objprincipal(self):
        if not self._obj and self._meas['values']['peso_obj']>0:

        
            self.ids.interior.md_bg_color = (self._meas['values']['cor_obj_R']/255,self._meas['values']['cor_obj_G']/255,self._meas['values']['cor_obj_B']/255,1)
            self.ids.caixa.pos_hint = {'x': 0.452, 'y': 0.82}
            self.ids.caixa.size_hint = (0.08,0.1)
            
            self._obj = True
            self._ev = Clock.schedule_interval(self.move_objprincipal,1.0/60.0)

    def mudou(self):
        if self._meas['values']['numObj_est_1'] > self._numobj[0]:
            self._esteira = 1
        elif self._meas['values']['numObj_est_2'] > self._numobj[1]:
            self._esteira = 2
        elif self._meas['values']['numObj_est_3'] > self._numobj[2]:
            self._esteira = 3
        elif self._meas['values']['numObj_est_nc'] > self._numobj[3]:
            self._esteira = 4
        self._numobj = [self._meas['values']['numObj_est_1'],self._meas['values']['numObj_est_2'],self._meas['values']['numObj_est_3'],self._meas['values']['numObj_est_nc']]
            
    
    def move_objprincipal(self,dt):
        if self._obj:

            y = self.ids.caixa.pos_hint['y'] - self._meas['values']['vel_esteira']/1000
            self.ids.caixa.pos_hint = {'y': y}
            if self.ids.caixa.pos_hint['y'] <= 0.41:

                self.ids.caixa.size_hint = (0.0000000001,0.00000000001)

                self._obj = False
                self._ev.cancel()
                self.criar_objsecundario(self.ids.interior.md_bg_color)
    
    def criar_objsecundario(self,color):
        if not self._obj1:

            self.ids.interior1.md_bg_color = color
            
            if self._esteira == 1:
                self.ids.caixa1.pos_hint = {'x': 0.21, 'y': 0.36}
            elif self._esteira == 2:
                self.ids.caixa1.pos_hint = {'x': 0.375, 'y': 0.36}
            elif self._esteira == 3:
                self.ids.caixa1.pos_hint = {'x': 0.536, 'y': 0.36}
            elif self._esteira == 4:
                self.ids.caixa1.pos_hint = {'x': 0.6975, 'y': 0.36}
            
            self.ids.caixa1.size_hint = (0.08,0.1)
            
            self._obj1 = True
            self._ev1 = Clock.schedule_interval(self.move_objsecundario,1.0/60.0)

        
    
    def move_objsecundario(self,dt):
        if self._obj1:

            y = self.ids.caixa1.pos_hint['y'] - self._meas['values']['vel_esteira']/1000
            self.ids.caixa1.pos_hint = {'y': y}
            if self.ids.caixa1.pos_hint['y'] <= 0.07:

                self.ids.caixa1.size_hint = (0.0000000001,0.00000000001)
                self._obj1 = False
                self._ev1.cancel()
    
    
            


    def connect(self):
        if self.ids.bt_con.text == 'CONECTAR':
            self.ids.bt_con.text = 'DESCONECTAR'

            try:
                self._modclient.host = self.ids.hostname.text
                self._modclient.port = int(self.ids.port.text)
                Window.set_system_cursor("wait")
                self._modclient.open()
                Window.set_system_cursor("arrow")
                if self._modclient.is_open()==True:
                    Snackbar(text="Conexão com o Servidor Realizado com Sucesso",bg_color=(0,1,0,1)).open()
                    self.ids.bt_con.icon = 'close-network-outline'
                    self.ids.bt_con.line_color = 'red'
                    self.ids.bt_con.icon_color = 'red'
                    self.ids.bt_con.text_color = 'red'
                    
                    
                    self._buscardados = True
                    self._updateThread = Thread(target=self.updater)
                    self._updateThread.start()

                                     
                    
                    
                elif self._modclient.is_open()==False:
                    self.ids.bt_con.text = 'CONECTAR'
                    Snackbar(text="Erro ao Conectar com o Servidor",bg_color=(1,0,0,1)).open()

            except Exception as e:
                print(f"Erro ao realizar a conexão com o servidor", e.args)
        else:

            self._modclient.close()
            self._lock.acquire()
            self._buscardados = False
            self.ids.bt_con.text = 'CONECTAR'
            self.ids.bt_con.line_color = 'green'
            self.ids.bt_con.icon_color = 'green'
            self.ids.bt_con.text_color = 'green'
            self.ids.bt_con.icon = 'download-network-outline'
            Snackbar(text="Cliente Desconectado",bg_color=(1,0,0,1)).open()
            self._lock.release()


        
    def updater(self):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface e
        inserção dos dados do Banco de dados
        """
        try: 
            self.atualizaConfig()   
            while self._updateWidgets:
                self._lock.acquire()
                self.readData()
                self._lock.release()
                self.updateGUI()
                self.mudou()

                dicdados = {'timestamp':self._meas['timestamp'],
                't_part': self._meas['values']['t_part'],
                'freq_des': self._meas['values']['freq_des'],
                'freq_mot':self._meas['values']['freq_mot'],
                'tensao': self._meas['values']['tensao'],
                'rotacao':self._meas['values']['rotacao'],
                'pot_entrada': self._meas['values']['pot_entrada'],
                'corrente': self._meas['values']['corrente'] ,
                'temp_estator': self._meas['values']['temp_estator'],
                'vel_esteira': self._meas['values']['vel_esteira'],
                'carga': self._meas['values']['carga'],
                'peso_obj': self._meas['values']['peso_obj'],
                'cor_obj_R':self._meas['values']['cor_obj_R'],
                'cor_obj_G': self._meas['values']['cor_obj_G'] ,
                'cor_obj_B':self._meas['values']['cor_obj_B'],
                'numObj_est_1': self._meas['values']['numObj_est_1'],
                'numObj_est_2': self._meas['values']['numObj_est_2'],
                'numObj_est_3': self._meas['values']['numObj_est_3'],
                'numObj_est_nc': self._meas['values']['numObj_est_nc']
                }
                dado = DadoCLP(**dicdados)
                self._lock.acquire()
                self._session.add(dado)
                self._session.commit()
                self._lock.release()

                sleep(self._scan_time/1000)

        except Exception as e:
            self._modclient.close()
            print("Erro2: ",e.args)
    
    def readData(self):
        """
        Método para leitura dos dados por meio do protocolo MODBUS
        """
        if self._buscardados:
            self._meas['timestamp'] = datetime.now()
            for key,value in self._tags.items():
                if key == 'estado_atuador' or key == 'bt_Desliga/Liga':
                    self._meas['values'][key] = self._modclient.read_coils(value['addr'],1)
                else:
                    self._meas['values'][key] = self._modclient.read_holding_registers(value['addr'],1)[0]/value['multiplicador']


    def updateGUI(self):
        """
        Método para a atualização da interface gráfica a partir dos dados lidos
        """
        #atualização dos labels
        for key, value in self._tags.items():
            try:
                self.ids[key].text = str(self._meas['values'][key])
            except:
               pass
            
        self.ids.graph1.updateGraph((self._meas['timestamp'],self._meas['values']['cor_obj_B']),0)
        self.ids.graph1.updateGraph((self._meas['timestamp'],self._meas['values']['cor_obj_G']),1)
        self.ids.graph1.updateGraph((self._meas['timestamp'],self._meas['values']['cor_obj_R']),2)

        self.ids.graph2.updateGraph((self._meas['timestamp'],self._meas['values']['peso_obj']),0)
    

        if self._meas['values']['estado_atuador']==[True]:
            self.ids.estado_atuador.md_bg_color = (0,1,0,1)
        else:
            self.ids.estado_atuador.md_bg_color = "red"
        
        if self._meas['values']['bt_Desliga/Liga']==[True]:
            self.ids.bt_DesligaLiga.md_bg_color = "red"
        else:
            self.ids.bt_DesligaLiga.md_bg_color = (0,1,0,1)

        self.ids.bt_salvar.icon_color = 'blue'
        self.ids.bt_salvar.text_color = 'blue'
        self.ids.bt_con.icon_color = 'red'
        self.ids.bt_con.text_color = 'red'
        if not self._modclient.is_open():
            self.ids.bt_con.icon_color = 'green'
            self.ids.bt_con.text_color = 'green'
        
        self.criar_objprincipal()
        
        

    def stopRefresh(self):
        self._updateWidgets = False
    
    def esteiraAtuar(self):
        
        try:
            self._lock.acquire()
            if self.ids.bt_DesligaLiga.md_bg_color == [0,1,0,1]:

                self._modclient.write_single_coil(self._tags['bt_Desliga/Liga']['addr'],1)
                self.ids.bt_DesligaLiga.md_bg_color = "red"

            else:
                self._modclient.write_single_coil(self._tags['bt_Desliga/Liga']['addr'],0)
                self.ids.bt_DesligaLiga.md_bg_color = (0,1,0,1)
            self._lock.release()

        except Exception as e:
            print("Erro na esteira",e.args)

    def atuadorAtuar(self):
        try:
            self._lock.acquire()
            if self.ids.estado_atuador.md_bg_color == [0,1,0,1]:
                self._modclient.write_single_coil(self._tags['estado_atuador']['addr'],0)
                self.ids.estado_atuador.md_bg_color = "red"
            else:
                self._modclient.write_single_coil(self._tags['estado_atuador']['addr'],1)
                self.ids.estado_atuador.md_bg_color = (0,1,0,1)
            self._lock.release()
        except Exception as e:
            print("Erro no atuador",e.args)

    def getDataDB(self):
        """
        Método que coleta as informações da interface fornecidas
        pelo usuário e requisita a busca no BD
        """
        
        try:
            init_t = datetime.strptime(self.ids.txt_init_time.text,'%d/%m/%Y %H:%M:%S')
            final_t = datetime.strptime(self.ids.txt_final_time.text,'%d/%m/%Y %H:%M:%S')
            cols = []

            
            for sensor in self.ids.sensores.children:
                try:
                    if sensor.ids.checkbox.active:
                        cols.append(sensor.id)
                except:
                    pass

            if init_t is None or final_t is None or len(cols) == 0:
                return
            
            if cols[0] == 'freq_mot' :
                self.ids.graph.ylabel = 'Frequência [Hz]'
            elif cols[0] == 'tensao' :
                self.ids.graph.ylabel = 'Tensão [V]'
            elif cols[0] == 'rotacao' :
                self.ids.graph.ylabel = 'Rotação do Motor [rpm]'
            elif cols[0] == 'pot_entrada' :
                self.ids.graph.ylabel = 'Potência de Entrada [W]'
            elif cols[0] == 'corrente' :
                self.ids.graph.ylabel = 'Corrente [A]'
            elif cols[0] == 'temp_estator' :
                self.ids.graph.ylabel = 'Temperatura do Estator [°C]'
            elif cols[0] == 'vel_esteira' :
                self.ids.graph.ylabel = 'Velocidade da Esteira [m/s]'
            elif cols[0] == 'carga' :
                self.ids.graph.ylabel = 'Peso Normalizado [kg]'
            elif cols[0] == 'peso_obj' :
                self.ids.graph.ylabel = 'Peso do Objeto [kg]'
            elif cols[0] == 'Cor_obj' :
                self.ids.graph.ylabel = 'Cor do Objeto [RGB]'
                cols[0] = 'cor_obj_R'
                cols.append('cor_obj_G')
                cols.append('cor_obj_B')


            cols.append('timestamp')

            self._lock.acquire()
            result1 = self._session.query(DadoCLP).filter(DadoCLP.timestamp.between(init_t,final_t)).all()
            self._lock.release()

            dados = [valores.dadoDicionario() for valores in result1]

            result = dict((sensor,[]) for sensor in cols)

            for i in dados:
                for j in range(0,len(cols)):
                    result[cols[j]].append(i[cols[j]])


            if result is None or len(result['timestamp']) == 0:
                return

            self.ids.graph.clearPlots()

            for key, value in result.items():
                if key == 'timestamp':
                    continue
                p = LinePlot(line_width=1.5, color=self._tags[key]['color'])
                p.points = [(x,value[x]) for x in range(0,len(value))]
                self.ids.graph.add_plot(p)

            
            self.ids.graph.xmax = len(result[cols[0]])
            self.ids.graph.ymax = max(result[cols[0]])*1.1
            self.ids.graph.y_ticks_major = max(result[cols[0]])*1.1/5
            self.ids.graph.x_ticks_major = len(result[cols[0]])*0.1
            self.ids.graph.update_x_labels([x for x in result['timestamp']])

        except Exception as e:
            print("Erro1: ", e.args)
   
    def atualizaConfig(self):
        try:
            configs = {}
            self._scan_time = int(self.ids.scan_time.text)
            configs['scan_time'] = int(self.ids.scan_time.text)
            # passar a frequencia desejada
            self._modclient.write_single_register(self._tags['freq_des']['addr'],int(self.ids.frequenciadesejada.text))
            configs['freq_des'] = int(self.ids.frequenciadesejada.text)

            # passar o tempo  de partida do motor
            self._modclient.write_single_register(self._tags['t_part']['addr'],int(self.ids.tempopartida.text)*10)
            configs['t_part'] = int(self.ids.tempopartida.text)

            self._modclient.write_single_register(self._tags['filtro_massa_1']['addr'],int(self.ids.filtropesoesteira1.text))

            configs['filtro_massa_1'] = int(self.ids.filtropesoesteira1.text)

            self._modclient.write_single_register(self._tags['filtro_massa_2']['addr'],int(self.ids.filtropesoesteira2.text))

            configs['filtro_massa_2'] = int(self.ids.filtropesoesteira2.text)

            self._modclient.write_single_register(self._tags['filtro_massa_3']['addr'],int(self.ids.filtropesoesteira3.text))

            configs['filtro_massa_3'] = int(self.ids.filtropesoesteira3.text)
            
            if self.ids.FiltroPesoest1.active == True:
                self._modclient.write_single_coil(self._tags['filtro_est_1']['addr'],0)
                configs['filtro_est_1'] = 0

            elif self.ids.FiltroCorest1.active == True:
                self._modclient.write_single_coil(self._tags['filtro_est_1']['addr'],1)
                configs['filtro_est_1'] = 1

            if self.ids.FiltroPesoest2.active == True:
                self._modclient.write_single_coil(self._tags['filtro_est_2']['addr'],0)
                configs['filtro_est_2'] = 0

            elif self.ids.FiltroCorest2.active == True:
                self._modclient.write_single_coil(self._tags['filtro_est_2']['addr'],1)
                configs['filtro_est_2'] = 1

            if self.ids.FiltroPesoest3.active == True:
                self._modclient.write_single_coil(self._tags['filtro_est_3']['addr'],0)
                configs['filtro_est_3'] = 0

            elif self.ids.FiltroCorest3.active == True:
                self._modclient.write_single_coil(self._tags['filtro_est_3']['addr'],1)
                configs['filtro_est_3'] = 1




            if self.ids.filtrovermelhoesteira1.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_r_1']['addr'],255)
                configs['filtro_cor_r_1'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_r_1']['addr'],0)
                configs['filtro_cor_r_1'] = 0

            if self.ids.filtroverdeesteira1.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_g_1']['addr'],255)
                configs['filtro_cor_g_1'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_g_1']['addr'],0)
                configs['filtro_cor_g_1'] = 0

            if self.ids.filtroazulesteira1.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_b_1']['addr'],255)
                configs['filtro_cor_b_1'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_b_1']['addr'],0)
                configs['filtro_cor_b_1'] = 0




            if self.ids.filtrovermelhoesteira2.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_r_2']['addr'],255)
                configs['filtro_cor_r_2'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_r_2']['addr'],0)
                configs['filtro_cor_r_2'] = 0
            
            if self.ids.filtroverdeesteira2.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_g_2']['addr'],255)
                configs['filtro_cor_g_2'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_g_2']['addr'],0)
                configs['filtro_cor_g_2'] = 0

            if self.ids.filtroazulesteira2.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_b_2']['addr'],255)
                configs['filtro_cor_b_2'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_b_2']['addr'],0)
                configs['filtro_cor_b_2'] = 0




            if self.ids.filtrovermelhoesteira3.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_r_3']['addr'],255)
                configs['filtro_cor_r_3'] = 255
            else:
                self._modclient.write_single_register(self._tags['filtro_cor_r_3']['addr'],0)
                configs['filtro_cor_r_3'] = 0
            
            if self.ids.filtroverdeesteira3.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_g_3']['addr'],255)
                configs['filtro_cor_g_3'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_g_3']['addr'],0)
                configs['filtro_cor_g_3'] = 0

            if self.ids.filtroazulesteira3.active == True:
                self._modclient.write_single_register(self._tags['filtro_cor_b_3']['addr'],255)
                configs['filtro_cor_b_3'] = 255

            else:
                self._modclient.write_single_register(self._tags['filtro_cor_b_3']['addr'],0)
                configs['filtro_cor_b_3'] = 0


            a_file = open("configs.pkl", "wb")
            pickle.dump(configs, a_file)
            a_file.close()


            Snackbar(text="Configurações Salvas com Sucesso",bg_color=(0,0,1,1)).open()  

        except:
            Snackbar(text="Erro ao Salvar Configurações",bg_color=(1,1,0,1)).open()    


    def carregaConfig(self):
        try:
            a_file = open("configs.pkl", "rb")
            configs = pickle.load(a_file)
            a_file.close()

            
            self.ids.scan_time.text = str(configs['scan_time'])
            # passar a frequencia desejada
 
            self.ids.frequenciadesejada.text = str(configs['freq_des'])

            # passar o tempo  de partida do motor

            self.ids.tempopartida.text = str(configs['t_part'])
           
            self.ids.filtropesoesteira1.text = str(configs['filtro_massa_1'])

            self.ids.filtropesoesteira2.text = str(configs['filtro_massa_2'])

            self.ids.filtropesoesteira3.text = str(configs['filtro_massa_3'])
            
            
            if configs['filtro_est_1'] == 0:
                self.ids.FiltroPesoest1.active = True

            elif configs['filtro_est_1'] == 1:
                self.ids.FiltroCorest1.active = True

            if configs['filtro_est_2'] == 0:
                self.ids.FiltroPesoest2.active = True

            elif configs['filtro_est_2'] == 1:
                self.ids.FiltroCorest2.active = True

            if configs['filtro_est_3'] == 0:
                self.ids.FiltroPesoest3.active = True

            elif configs['filtro_est_3'] == 1:
                self.ids.FiltroCorest3.active = True

            




            if configs['filtro_cor_r_1'] == 255:
                self.ids.filtrovermelhoesteira1.active = True

            else:
                self.ids.filtrovermelhoesteira1.active = False

            if configs['filtro_cor_g_1'] == 255:
                self.ids.filtroverdeesteira1.active = True

            else:
                self.ids.filtroverdeesteira1.active = False

            if configs['filtro_cor_b_1'] == 255:
                self.ids.filtroazulesteira1.active = True

            else:
                self.ids.filtroazulesteira1.active = False




            if configs['filtro_cor_r_2'] == 255:
                self.ids.filtrovermelhoesteira2.active = True

            else:
                self.ids.filtrovermelhoesteira2.active = False

            if configs['filtro_cor_g_2'] == 255:
                self.ids.filtroverdeesteira2.active = True

            else:
                self.ids.filtroverdeesteira2.active = False

            if configs['filtro_cor_b_2'] == 255:
                self.ids.filtroazulesteira2.active = True

            else:
                self.ids.filtroazulesteira2.active = False




            if configs['filtro_cor_r_3'] == 255:
                self.ids.filtrovermelhoesteira3.active = True

            else:
                self.ids.filtrovermelhoesteira3.active = False

            if configs['filtro_cor_g_3'] == 255:
                self.ids.filtroverdeesteira3.active = True

            else:
                self.ids.filtroverdeesteira3.active = False

            if configs['filtro_cor_b_3'] == 255:
                self.ids.filtroazulesteira3.active = True

            else:
                self.ids.filtroazulesteira3.active = False



        except Exception as e:
            print("Erro ao carregar as configurações: ", e.args)
           
    

class LabeledCheckBoxHistGraph(MDBoxLayout):
    pass
