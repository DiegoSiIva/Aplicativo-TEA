import threading
import time
import pygame
import requests
import speech_recognition as sr
import pyttsx3
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.gridlayout import MDGridLayout
from random import sample
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivy.graphics import Line, Color
from kivy.uix.widget import Widget
import math
from kivy.clock import Clock

recognizer = sr.Recognizer()  #transforma a fala em texto
engine = pyttsx3.init()  #trasnforma o texto em fala
link = ''
requisições = requests.get(f'{link}/.json')


class UserDatabase:
    def __init__(self, link):
        self.link = link
        self.dados = {}
        self.update_interval = 0
        self.keep_running = True
        self.start_update_thread()

    def start_update_thread(self):
        """Inicia uma thread para atualizar os dados periodicamente."""
        thread = threading.Thread(target=self.update_data)
        thread.daemon = True
        thread.start()

    def update_data(self):
        """Atualiza os dados a partir do Firebase a cada intervalo definido."""
        while self.keep_running:
            try:
                response = requests.get(f"{self.link}/Usuarios.json")
                if response.status_code == 200:
                    self.dados = response.json()
                else:
                    print(f"Erro ao obter dados: {response.status_code}")
            except requests.RequestException as e:
                print(f"Erro de conexão: {e}")

            time.sleep(self.update_interval)  # Espera o intervalo definido antes de atualizar novamente
            return self.dados

    def stop_update_thread(self):
        """Para a thread de atualização."""
        self.keep_running = False


class Login:
    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        self.link = link
        self.requisições = requisições
        self.login_timer = None

    def set_error_empty(self, instance_textfield):
        instance_textfield.helper_text = "Campo obrigatório!"
        instance_textfield.helper_text_mode = "on_error"
        instance_textfield.error = True

    def set_error_wrong(self, instance_textfield, msg):
        instance_textfield.helper_text = f"{msg}"
        instance_textfield.helper_text_mode = "on_error"
        instance_textfield.error = True

    def autenticacao(self):
        user = self.screen.ids.user.text.capitalize()
        password = self.screen.ids.password.text
        userdb = UserDatabase(f'{link}')
        dados = userdb.update_data()

        for i in range(len(dados)):
            if user == '':
                self.set_error_empty(self.screen.ids.user)
                return
            elif user == dados[f'User{i}']['User']:
                self.screen.ids.user.helper_text = ""
                if password == '':
                    self.set_error_empty(self.screen.ids.password)
                    return
                elif password != dados[f'User{i}']['Senha']:
                    mensagem = 'Senha incorreta!'
                    self.set_error_wrong(self.screen.ids.password, mensagem)
                    return
                else:
                    self.screen.manager.current = 'inicio'
                    self.screen.ids.user.text = ""
                    self.screen.ids.password.text = ""
                    self.start_logout_timer()
                    return
        mensagem = 'Usuário não existe!'
        self.set_error_wrong(self.screen.ids.user, mensagem)

    def start_logout_timer(self):
        """Inicia o timer para desconexão automática após 2 horas."""
        if self.login_timer:
            Clock.unschedule(self.login_timer)

        self.login_timer = Clock.schedule_once(lambda dt: self.force_logout(), 2 * 60 * 60)

    def force_logout(self, *args):
        """Desconecta o usuário e redireciona para a tela de login."""
        self.screen.manager.current = 'login'
        self.screen.ids.user.text = ""
        self.screen.ids.password.text = ""


class Register:
    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        self.link = link  # O mesmo link utilizado para obter os dados no Login
        self.requisições = requisições

    def set_error_empty(self, instance_textfield):
        instance_textfield.helper_text = "Campo obrigatório!"
        instance_textfield.helper_text_mode = "on_error"
        instance_textfield.error = True

    def set_error_message(self, instance_textfield, msg):
        instance_textfield.helper_text = f"{msg}"
        instance_textfield.helper_text_mode = "on_error"
        instance_textfield.error = True

    def clear_error(self, instance_textfield):
        instance_textfield.helper_text = ""
        instance_textfield.error = False

    def validacao(self):
        """Valida os campos e registra o usuário."""
        username = self.screen.ids.new_user.text.capitalize()
        password = self.screen.ids.new_password.text
        confirm_password = self.screen.ids.confirm_password.text
        userdb = UserDatabase(f'{link}')
        dados = userdb.update_data()

        if username == '':
            self.set_error_empty(self.screen.ids.new_user)
            return
        else:
            self.clear_error(self.screen.ids.new_user)

        if password == '':
            self.set_error_empty(self.screen.ids.new_password)
            return

        elif len(password) < 8:
            self.set_error_message(self.screen.ids.new_password, "Minimo 8 caracteres!")
            return

        else:
            self.clear_error(self.screen.ids.new_password)

        if confirm_password == '':
            self.set_error_empty(self.screen.ids.confirm_password)
            return
        else:
            self.clear_error(self.screen.ids.confirm_password)

        for i in range(len(dados)):
            if username == dados[f'User{i}']['User']:
                self.set_error_message(self.screen.ids.new_user, "Usuário já existe!")
                return

        if password != confirm_password:
            self.set_error_message(self.screen.ids.confirm_password, "Senhas não coincidem!")
            return
        else:
            self.clear_error(self.screen.ids.confirm_password)

        new_user_id = f"User{len(dados)}"
        dados[new_user_id] = {
            "User": username,
            "Senha": password
        }

        self.save_data(dados)

        self.screen.ids.new_user.text = ""
        self.screen.ids.new_password.text = ""
        self.screen.ids.confirm_password.text = ""
        # Exibir Snackbar de sucesso
        # Exibir um Card de confirmação
        success_card = MDCard(
            size_hint=(0.7, None),
            height="70dp",
            md_bg_color=(0.278, 0.306, 0.365, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            radius=[10, 10, 10, 10],
            padding="10dp",
        )

        # Adicionar texto ao Card
        from kivymd.uix.label import MDLabel
        success_card.add_widget(MDLabel(
            text="Cadastro concluído!",
            halign="center",
            valign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        ))

        self.screen.add_widget(success_card)

        Clock.schedule_once(lambda dt: self.screen.remove_widget(success_card), 3)

        Clock.schedule_once(lambda dt: setattr(self.screen.manager, 'current', 'login'), 3.5)

    def save_data(self, dados):
        """Atualiza os dados no banco de dados Firebase."""
        try:
            # Envia os dados atualizados para o Firebase usando uma requisição PUT
            response = requests.put(f'{self.link}/Usuarios.json', json=dados)
            if response.status_code == 200:
                print("Dados salvos com sucesso!")
            else:
                print(f"Erro ao salvar os dados: {response.status_code}")
                print(response.json())  # Exibe a resposta do erro
        except requests.RequestException as e:
            print(f"Erro de conexão: {e}")


class SigaTracejadoWidget(Widget):
    def __init__(self, result_label, **kwargs):
        super().__init__(**kwargs)
        self.result_label = result_label
        self.drawing = False
        self.points = []
        self.tolerancia = 15
        self.espiral_pontos = []
        self.desenhar_espiral()

    def desenhar_espiral(self):
        largura, altura = self.size
        cx, cy = largura / 2, altura / 2  # Mantém a espiral centralizada
        raio_inicial = 5
        giros = 5
        incremento_raio = 6
        incremento_theta = 0.04
        theta = math.pi / 2  # Início no topo

        # Fatores para alongar na vertical
        escala_x = 1.0
        escala_y = 1.1

        # Limpar a lista de pontos da espiral
        self.espiral_pontos.clear()

        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)
            while theta < 2 * math.pi * giros + math.pi / 2:
                raio = raio_inicial + incremento_raio * theta
                x1 = cx + raio * math.cos(theta) * escala_x
                y1 = cy + raio * math.sin(theta) * escala_y

                # Armazenar pontos da espiral
                self.espiral_pontos.append((x1, y1))

                theta += incremento_theta
                raio = raio_inicial + incremento_raio * theta
                x2 = cx + raio * math.cos(theta) * escala_x
                y2 = cy + raio * math.sin(theta) * escala_y

                Line(points=[x1, y1, x2, y2], width=1)

                # Armazenar o segundo ponto da linha
                self.espiral_pontos.append((x2, y2))

                theta += incremento_theta * 0.8

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False

        # Limitar a área de toque à área da espiral
        largura, altura = self.size
        cx, cy = largura / 2, altura / 2  # Centro da espiral
        raio_max = 20 * 13 + 5  # Raio máximo da espiral

        # Calcular a distância entre o toque e o centro
        distancia_toque = math.sqrt((touch.x - cx) ** 2 + (touch.y - cy) ** 2)

        # Permitir o toque somente dentro do raio máximo da espiral
        if distancia_toque <= raio_max:
            self.drawing = True
            self.prev_x, self.prev_y = touch.x, touch.y
            self.points = [(self.prev_x, self.prev_y)]
            return True
        return False

    def on_touch_move(self, touch):
        if self.drawing:
            largura, altura = self.size
            cx, cy = largura / 2, altura / 2
            raio_max = 20 * 13 + 5  # Raio máximo da espiral
            distancia_toque = math.sqrt((touch.x - cx) ** 2 + (touch.y - cy) ** 2)

            # Permitir o desenho apenas dentro da área da espiral
            if distancia_toque <= raio_max:
                with self.canvas:
                    Color(1, 0, 0, 1)
                    Line(points=[self.prev_x, self.prev_y, touch.x, touch.y], width=2)
                self.points.append((touch.x, touch.y))
                self.prev_x, self.prev_y = touch.x, touch.y
        return True

    def on_touch_up(self, touch):
        if self.drawing:
            self.drawing = False
            if len(self.points) > 0:
                if self.verificar_acerto():
                    falar_resposta('Parabéns, você acertou!')
                else:
                    falar_resposta('Não acertou, tente novamente!')
                Clock.schedule_once(self.reset, 2)

    def verificar_acerto(self):
        if len(self.points) < 50:
            return False

        distancia_percorrida = sum(
            self.distancia_ponto(self.points[i], self.points[i + 1])
            for i in range(len(self.points) - 1)
        )

        distancia_minima = 0.7 * sum(
            self.distancia_ponto(self.espiral_pontos[i], self.espiral_pontos[i + 1])
            for i in range(len(self.espiral_pontos) - 1)
        )

        pontos_corretos = sum(
            1
            for ponto_usuario in self.points
            if any(
                self.distancia_ponto(ponto_usuario, ponto_espiral) <= self.tolerancia
                for ponto_espiral in self.espiral_pontos
            )
        )

        return distancia_percorrida >= distancia_minima and pontos_corretos / len(self.points) >= 0.7

    def distancia_ponto(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def reset(self, dt):
        self.points = []
        self.canvas.clear()
        self.espiral_pontos = []
        self.desenhar_espiral()
        self.result_label.text = ""


class ClickableCard(MDCard):
    def __init__(self, source, is_correct, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.is_correct = is_correct
        self.on_click = on_click

        self.orientation = "vertical"
        self.ripple_behavior = True
        self.padding = 10
        self.md_bg_color = [1, 1, 1, 1]

        self.image = Image(source=self.source, size_hint=(1, 1))
        self.add_widget(self.image)

    def on_release(self):
        if self.on_click:
            self.on_click(self, self.is_correct)


class ClickableCard1(MDCard):
    def __init__(self, source, is_correct, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.is_correct = is_correct
        self.on_click = on_click

        self.orientation = "vertical"
        self.ripple_behavior = True
        self.padding = 10
        self.md_bg_color = [0, 0, 0, 0]

        self.image = Image(source=self.source, size_hint=(1, 1))
        self.add_widget(self.image)

    def on_release(self):
        if self.on_click:
            self.on_click(self, self.is_correct)


class EmocoesJogo:
    def __init__(self, grid_layout, screen):
        self.grid_layout = grid_layout
        self.numeros_disponiveis = list(range(8))
        self.numero_anterior = None
        self.screen = screen

    def update_images(self):
        self.grid_layout.clear_widgets()
        image_sources = [
            "./imagens/alegria.png", "./imagens/desconforto.png", "./imagens/felicidade.png", "./imagens/raiva.png",
            "./imagens/calma.png", "./imagens/tranquila.png", "./imagens/tristeza.png", "./imagens/surpresa.png"
        ]

        self.num_aleatorio = self.sortear_numeros()
        self.numero = self.sortear_numero_correto()

        screen = self.screen
        screen.ids.texto.text = self.texto()
        screen.ids.emocao.text = self.nome()

        for source in self.num_aleatorio:
            is_correct = (source == self.numero)
            card = ClickableCard(
                source=image_sources[source],
                is_correct=is_correct,
                on_click=self.on_card_click,
                size_hint=(1, None),
                height=150,
            )
            self.grid_layout.add_widget(card)

    def sortear_numeros(self):
        if len(self.numeros_disponiveis) < 4:
            self.numeros_disponiveis = list(range(8))

        return sample(self.numeros_disponiveis, 4)

    def sortear_numero_correto(self):
        numeros_possiveis = [n for n in self.num_aleatorio if n != self.numero_anterior]
        if not numeros_possiveis:
            numeros_possiveis = self.num_aleatorio

        numero_correto = sample(numeros_possiveis, 1)[0]
        self.numero_anterior = numero_correto
        return numero_correto

    def on_card_click(self, card, is_correct):
        if is_correct:
            card.md_bg_color = [0, 1, 0, 1]
            Clock.schedule_once(lambda dt: self.load_new_images(), 2)
        else:
            card.md_bg_color = [1, 0, 0, 1]

    def load_new_images(self, *args):
        self.num_aleatorio = self.sortear_numeros()
        self.numero = self.sortear_numero_correto()
        self.update_images()

    def texto(self):
        emocao_texto = [
            'A felicidade assim como a alegria, ela é frequentemente expressa por sorrisos, mas também'
            ' envolve um brilho nos olhos e uma expressão relaxada e serena.',

            'A angústia é caracterizada por sobrancelhas franzidas e erguidas no centro, olhos ligeiramente'
            ' arregalados e lábios comprimidos. A expressão facial reflete tensão e desconforto.',

            'Alegria é uma emoção associada a um sorriso largo e sincero. Os olhos tendem a se estreitar '
            'e apresentar rugas nos cantos, o que indica um sorriso genuíno.',

            'A raiva é facilmente reconhecível por sobrancelhas baixas e juntas, olhos fixos e intensos,'
            ' e boca tensa, muitas vezes com os lábios pressionados ou os dentes à mostra.',

            'A Confiança é facilmente reconhecível por sobrancelhas em posição neutra, olhos relaxados'
            ' e boca com um pequeno sorriso.',

            'A calma é facilmente reconhecida por uma expressão facial relaxada, olhos'
            ' abertos, e um leve sorriso.',

            'A tristeza é associada a sobrancelhas levantadas e inclinadas para o centro,'
            ' olhos levemente fechados ou lacrimejantes, e boca curvada para baixo.',

            'A surpresa é caracterizada por sobrancelhas levantadas e arqueadas, olhos bem abertos'
            ' com pupilas dilatadas, e boca aberta formando um “O”.'
        ]
        return emocao_texto[self.numero]

    def nome(self):
        emocao_nome = ['Felicidade', 'Angústia', 'Alegria', 'Raiva', 'Confiança', 'Calma', 'Tristeza', 'Surpresa']
        return emocao_nome[self.numero]


class AssociacaoJogo:
    def __init__(self, grid_layout, screen):
        self.grid_layout = grid_layout
        self.numeros_disponiveis = list(range(4))
        self.numero_anterior = None
        self.screen = screen

    def update_images(self):
        self.grid_layout.clear_widgets()
        image_sources = [
            "./imagens/cachorro.png", "./imagens/gato.png", "./imagens/ovelha.png", "./imagens/cow.jpg"
        ]

        self.num_aleatorio = self.sortear_numeros()
        self.numero = self.sortear_numero_correto()

        screen = self.screen
        screen.ids.audio.text = self.nome()

        for source in self.num_aleatorio:
            is_correct = (source == self.numero)
            card = ClickableCard1(
                source=image_sources[source],
                is_correct=is_correct,
                on_click=self.on_card_click,
                size_hint=(1, None),
                height=150,
            )
            self.grid_layout.add_widget(card)

    def sortear_numeros(self):
        if len(self.numeros_disponiveis) < 4:
            self.numeros_disponiveis = list(range(4))

        return sample(self.numeros_disponiveis, 4)

    def sortear_numero_correto(self):
        numeros_possiveis = [n for n in self.num_aleatorio if n != self.numero_anterior]
        if not numeros_possiveis:
            numeros_possiveis = self.num_aleatorio

        numero_correto = sample(numeros_possiveis, 1)[0]
        self.numero_anterior = numero_correto
        return numero_correto

    def on_card_click(self, card, is_correct):
        if is_correct:
            card.md_bg_color = [0, 1, 0, 1]
            Clock.schedule_once(lambda dt: self.load_new_images(), 2)
        else:
            card.md_bg_color = [1, 0, 0, 1]

    def load_new_images(self, *args):
        self.num_aleatorio = self.sortear_numeros()
        self.numero = self.sortear_numero_correto()
        self.update_images()

    def nome(self):
        animal_nome = ['Cachorro', 'Gato', 'Ovelha', 'Vaca']
        return animal_nome[self.numero]


def logar(screen):
    login = Login(screen)
    login.autenticacao()


def registrar(screen):
    registro = Register(screen)
    registro.validacao()


def falar_resposta(texto):
    engine.say(texto)
    engine.runAndWait()


def ouvir_fala():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.listen(source)

        try:
            texto = recognizer.recognize_google(audio, language='pt-BR')
            return texto.lower()
        except sr.UnknownValueError:
            falar_resposta("Não consegui entender o que você disse.")
            return None
        except sr.RequestError as e:
            print(f"Erro na solicitação: {e}")
            return None


count = 0
frase_correta = ["Estou me sentindo bem", 'Eu gosto de comer maçã e banana', 'O cachorro está correndo no parque',
                 'O céu é azul e o sol brilha muito', 'Eu gosto de desenhar e colorir com lápis de cor']


def verificar_fala(self):
    global count

    if count < len(frase_correta):
        texto_falado = ouvir_fala()
        if texto_falado == frase_correta[count].lower():
            falar_resposta("Você falou corretamente!")
            self.ids.frases.text = frase_correta[count+1]
            count += 1

        else:
            falar_resposta("Você falou errado.")
            print(texto_falado)
    else:
        falar_resposta('Parabens, você acertou todas!')
        count = 0


def ouvir_frase():
    global count
    falar_resposta(frase_correta[count])


def audios_animais(animal):
    pygame.mixer.init()
    pygame.mixer.music.load(f'audios/{animal}.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass


def sigaotracejado():
    layout = MDFloatLayout()

    result_label = MDLabel(
        text="", font_style="H5", size_hint=(None, None), size=("250dp", "250dp"),
        pos_hint={"center_x": 0.5, "center_y": 0.7}, halign="center"
    )
    result_label.color = (0, 0, 0, 1)
    layout.add_widget(result_label)

    desenho_widget = SigaTracejadoWidget(result_label, size=(400, 596))
    layout.add_widget(desenho_widget)

    return layout


def emocoes_jogo(self):
    screen = MDScreen()
    layout = MDBoxLayout(orientation="vertical", padding=15, spacing=15)

    grid_layout = MDGridLayout(cols=2, spacing=10, padding=10)
    layout.add_widget(grid_layout)

    screen.add_widget(layout)

    image_updater = EmocoesJogo(grid_layout, self)
    image_updater.update_images()

    return screen


def associacao_jogo(self):
    screen = MDScreen()
    layout = MDBoxLayout(orientation="vertical", padding=15, spacing=15)

    grid_layout = MDGridLayout(cols=2, spacing=10, padding=10)
    layout.add_widget(grid_layout)

    screen.add_widget(layout)

    image_updater = AssociacaoJogo(grid_layout, self)
    image_updater.update_images()

    return screen
