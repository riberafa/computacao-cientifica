# Importa as bibliotecas necessárias
import PySimpleGUI as sg
import os.path
import matplotlib
import matplotlib.figure
import cv2
import numpy as np
from matplotlib.image import imread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Define o backend do Matplotlib como TkAgg
matplotlib.use("TkAgg")

# IDs dos Canvas
CANVAS_IDS = [
    '-CANVAS1-', '-CANVAS2-', '-CANVAS3-', '-CANVAS4-', '-CANVAS5-', '-CANVAS6-', '-CANVAS7-', '-CANVAS8-', '-CANVAS9-'
]

# Valores de n para a decomposição SVD
N_VALS = [1, 2, 3, 4, 5, 10, 25, 50, 100]

# Layout da coluna do arquivo
file_list_column = [
    [
        sg.Text("Caminho da Imagem Base", background_color='lightgray', text_color='black'),
        sg.In(size=(40, 1), enable_events=True, key="-IMAGEPATH-"),
        sg.FileBrowse(button_color=('white', 'black')),
        sg.VSeparator(),
        sg.Text('Imagem Original:', background_color='lightgray', text_color='black'),
        sg.Canvas(key='-ORIGINAL-', background_color='lightgray')
    ],
    [
        sg.Button('Reconstruir minha imagem!', key="-GO-", button_color=('white', 'black')), 
        sg.Button('Limpar Imagens', key='-CLEAR-', button_color=('white', 'black')), 
        sg.Button('Sair', key='-EXIT-', button_color=('white', 'black'))
    ],
]

# Gera a coluna de visualização das reconstruções
def generate_reconstruction_column():
    image_viewer_column = []
    text_col = []
    image_col = []
    for i, (n, canvas_id) in enumerate(zip(N_VALS, CANVAS_IDS)):
        text_col.append(sg.Text(f'n={n}', size=(20,1), justification='center', background_color='lightgray', text_color='black'))
        image_col.append(sg.Canvas(key=canvas_id, background_color='lightgray'))
        if i % 3 == 2:
            image_viewer_column.append(text_col)
            image_viewer_column.append(image_col)
            text_col, image_col = [], []
    return image_viewer_column

# Layout geral
layout = [
    [
        sg.Column(file_list_column, background_color='lightgray'),
        sg.VSeparator(),
        sg.Column(generate_reconstruction_column(), background_color='lightgray'),
    ]
]

# Cria a janela com background color personalizado
window = sg.Window("Reconstrução de Imagem em Tons de Cinza com Decomposição de Valor Singular", layout, finalize=True, background_color='lightgray')

# Configuração adicional do backend Matplotlib
matplotlib.use("TKAgg")

# Função para obter a figura de aproximação
def get_approximation_figure(image_path, n, need_S=False):

    A = imread(image_path)
    A = cv2.resize(A, dsize=(150, 150), interpolation=cv2.INTER_CUBIC)
    X = np.mean(A, -1)

    U, S, VT = np.linalg.svd(X, full_matrices=False)
    S = np.diag(S)

    Xapprox = U[:,:n] @ S[0:n,:n] @ VT[:n,:]

    fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
    fig.figimage(Xapprox, cmap='gray', resize=True)

    if need_S: 
        return S, fig 
    return fig

# Função para obter a figura da imagem original redimensionada
def get_resized_original(img_path):
    A = imread(image_path)
    A = cv2.resize(A, dsize=(150, 150), interpolation=cv2.INTER_CUBIC)
    A = np.mean(A, -1)
    fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
    fig.figimage(A, cmap='gray', resize=True)
    return fig

# Configuração adicional do backend Matplotlib
matplotlib.use("TkAgg")

# Função para desenhar a figura em um canvas
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

# Lista de figuras
FIGURES = []

# Loop principal
while True:
    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == '-GO-':
        try:
            while FIGURES:
                figure = FIGURES.pop()
                figure.get_tk_widget().pack_forget()
            image_path = values['-IMAGEPATH-']
            fig = draw_figure(window['-ORIGINAL-'].TKCanvas, get_resized_original(image_path))
            FIGURES.append(fig)
            for n, canvas_id in zip(N_VALS, CANVAS_IDS):
                fig = draw_figure(window[canvas_id].TKCanvas, get_approximation_figure(image_path, n))  
                FIGURES.append(fig)
        except Exception as e:
            print(e)
    
    if event == '-CLEAR-':
        while FIGURES:
            figure = FIGURES.pop()
            figure.get_tk_widget().pack_forget()

# Fecha a janela
window.close()
