import PySimpleGUI as sg
import os
from PIL import Image
import shutil
import io

# Funcție pentru a crea un buffer de imagine compatibil cu PySimpleGUI
def image_to_data(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()

# Funcție pentru a afișa albumul cu toate imaginile
def display_album(image_list):
    if len(image_list) < 5:
        sg.popup("Trebuie să adaugi cel puțin 5 imagini pentru a vedea albumul!", title="Eroare")
        return
    elif len(image_list) > 10:
        sg.popup("Nu poți avea mai mult de 10 imagini în album!", title="Limită")
        return

    album_layout = []
    for image_path in image_list:
        try:
            with Image.open(image_path) as img:
                img.thumbnail((300, 300))
                img_data = image_to_data(img)
                album_layout.append(sg.Image(data=img_data, size=(300, 300), background_color="lightyellow"))
        except Exception as e:
            sg.popup_error(f"Eroare la încărcarea imaginii {image_path}: {e}")

    num_columns = 5 if len(image_list) > 5 else len(image_list)
    grid_layout = []
    for i in range(0, len(album_layout), num_columns):
        row = album_layout[i:i + num_columns]
        while len(row) < num_columns:
            row.append(sg.Image(size=(300, 300), background_color="lightyellow"))
        grid_layout.append(row)

    window_height = 700 if len(image_list) > 5 else 450
    album_window = sg.Window(
        "Album Foto",
        grid_layout,
        size=(1800, window_height),
        resizable=True,
        finalize=True,
        background_color="lightyellow"
    )
    album_window.read(close=True)

# Funcție pentru a salva albumul într-un folder
def save_album(album_name, image_list):
    albums_folder = "Albume"
    album_folder = os.path.join(albums_folder, album_name)

    if not os.path.exists(albums_folder):
        os.makedirs(albums_folder)

    if os.path.exists(album_folder):
        sg.popup_error(f"Albumul '{album_name}' deja există! Alege alt nume.")
        return

    os.makedirs(album_folder)

    for image_path in image_list:
        shutil.copy(image_path, album_folder)

    sg.popup(f"Albumul '{album_name}' a fost salvat cu succes în folderul '{album_folder}'!")

# Funcție pentru a adăuga imagini în listă
def handle_add_images(window, image_list):
    if len(image_list) >= 10:
        sg.popup("Nu poți adăuga mai mult de 10 imagini!", title="Limită atinsă")
        return

    file_paths = sg.popup_get_file(
        "Selectează imagini",
        size=(70, 50),
        file_types=[("Imagini", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")],
        multiple_files=True,
        background_color="lightyellow"
    )
    if file_paths:
        file_paths = file_paths.split(";")
        for file_path in file_paths:
            if os.path.exists(file_path) and file_path not in image_list:
                image_list.append(file_path)
        window["-IMAGE LIST-"].update([os.path.basename(p) for p in image_list])

# Funcție pentru a șterge o imagine din listă
def handle_remove_image(window, values, image_list):
    selected_image = values["-IMAGE LIST-"]
    if selected_image:
        selected_image_name = selected_image[0]
        full_path = next((p for p in image_list if os.path.basename(p) == selected_image_name), None)
        if full_path:
            image_list.remove(full_path)
            window["-IMAGE LIST-"].update([os.path.basename(p) for p in image_list])
        else:
            sg.popup_error("Imaginea selectată nu a fost găsită în listă!")

# Funcție pentru a salva albumul
def handle_save_album(window, values, image_list):
    if len(image_list) < 5:
        sg.popup("Trebuie să adaugi cel puțin 5 imagini pentru a salva albumul!", title="Eroare")
    elif len(image_list) > 10:
        sg.popup("Nu poți salva mai mult de 10 imagini într-un album!", title="Limită")
    else:
        album_name = sg.popup_get_text("Introdu numele albumului:", title="Salvează Album")
        if album_name:
            save_album(album_name, image_list)

# Funcție pentru a vizualiza albumul
def handle_view_album(window, image_list):
    display_album(image_list)

# Layout-ul aplicației
layout = [
    [sg.Text("Adaugă imagini pentru albumul tău:", font=("Arial", 16), text_color="white")],
    [sg.Listbox(values=[], size=(50, 10), key="-IMAGE LIST-", font=("Times New Roman", 12), select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)],
    [
        sg.Button("Adaugă Imagini", button_color=("white", "tan"), font=("Arial", 12)),
        sg.Button("Șterge Imagine", button_color=("red", "tan"), font=("Arial", 12)),
        sg.Button("Vezi Album", button_color=("white", "tan"), font=("Arial", 12)),
        sg.Button("Salvează Album", button_color=("green", "tan"), font=("Arial", 12)),
        sg.Button("Ieșire", button_color=("black", "tan"), font=("Arial", 12))
    ]
]

# Fereastra principală
window = sg.Window(
    "Creator Albume Foto",
    layout,
    size=(600, 300),
    background_color="lightyellow",
    resizable=True,
    element_justification="center",
    finalize=True
)

# Lista imaginilor din album
image_list = []

# Loop-ul principal al aplicației
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Ieșire":
        break
    elif event == "Adaugă Imagini":
        handle_add_images(window, image_list)
    elif event == "Șterge Imagine":
        handle_remove_image(window, values, image_list)
    elif event == "Vezi Album":
        handle_view_album(window, image_list)
    elif event == "Salvează Album":
        handle_save_album(window, values, image_list)

window.close()
