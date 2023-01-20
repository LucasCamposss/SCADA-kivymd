from kivy.utils import get_hex_from_color
from kivymd.app import MDApp
from kivy.core.window import Window
from mainwidget import MyWidget
from kivy.lang.builder import Builder
import pickle

class MainApp(MDApp):
    """
    Classe com o aplicativo
    """
    def rgb_to_hex(self,rgb):
        return "%02x%02x%02x" % rgb

    def build(self):    
        
        try:
            a_file = open("configs.pkl", "rb")
            configs = pickle.load(a_file)
            a_file.close()
            color1 = self.rgb_to_hex((int(configs['primary_color'][0]*255),int(configs['primary_color'][1]*255),int(configs['primary_color'][2]*255)))
            color2 = self.rgb_to_hex((int(configs['accent_color'][0]*255),int(configs['accent_color'][1]*255),int(configs['accent_color'][2]*255)))
            
            self.theme_cls.colors['Teal'] = {
            "50": color1 ,
            "100": color1 ,
            "200": color1 ,
            "300": color1 ,
            "400": color1 ,
            "500": color1 ,
            "600": color1 ,
            "700": color1 ,
            "800": color1 ,
            "900": color1 ,
            "A100": color1 ,
            "A200": color1 ,
            "A400": color1,
            "A700": color1,
            }
            
            self.theme_cls.colors['Lime'] = {
            "50": color2,
            "100": color2 ,
            "200":color2,
            "300": color2,
            "400": color2,
            "500": color2,
            "600": color2,
            "700": color2,
            "800": color2,
            "900": color2,
            "A100": color2,
            "A200": color2,
            "A400": color2,
            "A700": color2,
            }

    
            self.theme_cls.primary_palette = "Teal"
            self.theme_cls.primary_hue = "500"
            self.theme_cls.accent_palette = "Lime"
            self.theme_cls.accent_hue = "500"
            self.theme_cls.theme_style = configs['theme_style']
        except Exception as e:
            print("Erro nos temas", e.args)
        
        
        self._widget = MyWidget(scan_time=1000, server_ip='127.0.0.1',server_port=502,
        modbus_addrs = {
            'estado_atuador':[801,1],
            'bt_Desliga/Liga': [802,1],
            't_part':[798,10],
            'freq_des':[799,1],
            'freq_mot':[800,10],
            'tensao':[801,1],
            'rotacao':[803,1],
            'pot_entrada':[804,10],
            'corrente':[805,100],
            'temp_estator':[806,10],
            'vel_esteira':[807,100],
            'carga':[808,100],
            'peso_obj':[809,100],
            'cor_obj_R':[810,1],
            'cor_obj_G':[811,1],
            'cor_obj_B':[812,1],
            'numObj_est_1':[813,1],
            'numObj_est_2':[814,1],
            'numObj_est_3':[815,1],
            'numObj_est_nc':[816,1],
            'filtro_est_1':[901,1],
            'filtro_est_2':[902,1],
            'filtro_est_3':[903,1],
            'filtro_cor_r_1':[1001,1],
            'filtro_cor_g_1':[1002,1],
            'filtro_cor_b_1':[1003,1],
            'filtro_massa_1':[1004,1],
            'filtro_cor_r_2':[1011,1],
            'filtro_cor_g_2':[1012,1],
            'filtro_cor_b_2':[1013,1],
            'filtro_massa_2':[1014,1],
            'filtro_cor_r_3':[1021,1],
            'filtro_cor_g_3':[1022,1],
            'filtro_cor_b_3':[1023,1],
            'filtro_massa_3':[1024,1]
        }
        )
        
        return self._widget

    

    def on_stop(self):
        """
        Método executado quando a aplicação é fechada
        """
        a_file = open("configs.pkl", "rb")
        configs = pickle.load(a_file)
        a_file.close()
        configs['primary_color'] = self.theme_cls._get_primary_color()
        configs['accent_color'] = self.theme_cls._get_accent_color()
        configs['theme_style'] = self.theme_cls._get_theme_style(not self)
        a_file = open("configs.pkl", "wb")
        pickle.dump(configs, a_file)
        a_file.close()

        self._widget.stopRefresh()



# if __name__=='__main__':
    # Builder.load_string(open("mainwidget.kv",encoding="utf-8").read(),rulesonly=True)
#     Builder.load_string(open("popups.kv",encoding="utf-8").read(),rulesonly=True)    
#     MainApp().run()

if __name__=='__main__': 
    Window.size = (1200,720)
    Builder.load_string(open("mainwidget.kv",encoding="utf-8").read(),rulesonly=True)

    # Window.fullscreen = True
    MainApp().run()