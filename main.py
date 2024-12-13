from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from functions import (audios_animais, verificar_fala, sigaotracejado, emocoes_jogo, ouvir_frase, logar, registrar,
                       falar_resposta, associacao_jogo, AssociacaoJogo)

Window.size = (400, 750)


class Login(Screen):
    def logar(self):
        logar(self)


class Register(Screen):
    def registrar(self):
        registrar(self)


class Inicio(Screen):
    pass


class Voz(Screen):
    def falar(self):
        verificar_fala(self)

    def ouvir(self):
        ouvir_frase()

    def titulo(self, texto):
        falar_resposta(texto)


class Associacao(Screen):
    def sons(self, animal):
        audios_animais(animal)

    def titulo(self, texto):
        falar_resposta(texto)


class Associacao_jogo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.associacaojogo)

    def associacaojogo(self, dt):
        layout = associacao_jogo(self)
        self.ids.associacao_layout.add_widget(layout)

    def titulo1(self, texto):
        falar_resposta(texto)

    def animal_certo(self):
        audios_animais(self.ids.audio.text)


class Emocoes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.add_layout)

    def add_layout(self, dt):
        layout = emocoes_jogo(self)
        self.ids.emocoes_layout.add_widget(layout)

    def titulo(self, texto):
        falar_resposta(texto)


class Coordenacao_motora(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.add_layout)

    def add_layout(self, dt):
        layout = sigaotracejado()
        self.ids.cord_layout.add_widget(layout)

    def titulo(self, texto):
        falar_resposta(texto)


class MyApp(MDApp):
    def build(self):
        screen = Builder.load_file('telas.kv')
        return screen

    def mudar_tela(self, tela):
        self.root.current = tela


MyApp().run()
