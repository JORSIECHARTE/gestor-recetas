import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

RECETAS_FILE = "recetas.json"

if not os.path.exists("recetas_imagenes"):
    os.mkdir("recetas_imagenes")

FONDO_COLOR = "#ffe4e1"
BOTON_COLOR = "#ffb6c1"
BOTON_TEXTO_COLOR = "#ffffff"
TITULO_COLOR = "#ff69b4"

FONT_TITULO = ("Comic Sans MS", 20, "bold")
FONT_NORMAL = ("Comic Sans MS", 12)
FONT_BOTON = ("Comic Sans MS", 14, "bold")


class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Recetas")
        self.root.geometry("800x600")
        self.root.configure(bg=FONDO_COLOR)

        self.recetas = []
        self.cargar_recetas()
        self.ventana_agregar_abierta = False
        self.ventana_ver_abierta = False


        style = ttk.Style()
        style.configure(
            "TButton",
            background=BOTON_COLOR,
            foreground=BOTON_TEXTO_COLOR,
            font=FONT_BOTON,
            padding=10
        )
        style.map("TButton", background=[("active", "#ff8c94")])


        self.main_frame = tk.Frame(self.root, bg=FONDO_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)


        titulo_label = tk.Label(
            self.main_frame,
            text="Gestor de Recetas",
            bg=FONDO_COLOR,
            fg=TITULO_COLOR,
            font=FONT_TITULO
        )
        titulo_label.pack(pady=20)


        btn_añadir = ttk.Button(
            self.main_frame,
            text="Añadir Receta",
            command=self.abrir_formulario
        )
        btn_añadir.pack(pady=10, ipadx=20, ipady=5)

        btn_ver = ttk.Button(
            self.main_frame,
            text="Ver Recetas",
            command=self.ver_recetas
        )
        btn_ver.pack(pady=10, ipadx=20, ipady=5)


        dedicatoria_label = tk.Label(
            self.main_frame,
            text="Espacio para dedicatoria",
            bg=FONDO_COLOR,
            fg=TITULO_COLOR,
            font=("Comic Sans MS", 14, "italic")
        )
        dedicatoria_label.pack(pady=20)

    def guardar_recetas(self):
        try:
            with open(RECETAS_FILE, "w", encoding="utf-8") as file:
                json.dump(self.recetas, file, indent=4, ensure_ascii=False)
            print("Recetas guardadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar las recetas: {e}")

    def cargar_recetas(self):
        try:
            if os.path.exists(RECETAS_FILE):
                with open(RECETAS_FILE, "r", encoding="utf-8") as file:
                    self.recetas = json.load(file)
                print("Recetas cargadas correctamente.")
            else:
                self.recetas = []
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar las recetas: {e}")

    def abrir_formulario(self):
        if self.ventana_agregar_abierta:
            messagebox.showerror("Error", "Ya hay una ventana de agregar receta abierta.")
            return

        self.ventana_agregar_abierta = True


        formulario = tk.Toplevel(self.root)
        formulario.title("Añadir Receta")
        formulario.geometry("500x600")
        formulario.configure(bg=FONDO_COLOR)
        formulario.transient(self.root)
        formulario.grab_set()

        def cerrar_formulario():
            self.ventana_agregar_abierta = False
            formulario.destroy()

        formulario.protocol("WM_DELETE_WINDOW", cerrar_formulario)

        frame = tk.Frame(formulario, bg=FONDO_COLOR)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Título de la receta:", font=FONT_NORMAL).pack(pady=10, anchor="w")
        titulo_entry = ttk.Entry(frame, width=40)
        titulo_entry.pack(pady=5)

        ttk.Label(frame, text="Ingredientes:", font=FONT_NORMAL).pack(pady=10, anchor="w")
        ingredientes_text = tk.Text(frame, width=40, height=5)
        ingredientes_text.pack(pady=5)

        ttk.Label(frame, text="Pasos:", font=FONT_NORMAL).pack(pady=10, anchor="w")
        pasos_text = tk.Text(frame, width=40, height=5)
        pasos_text.pack(pady=5)


        imagen_label = ttk.Label(frame, text="No seleccionada", font=FONT_NORMAL)
        imagen_label.pack(pady=10)

        def cargar_imagen():
            ruta_imagen = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")])
            if ruta_imagen:
                imagen_label.config(text=os.path.basename(ruta_imagen))
                imagen_label.imagen = ruta_imagen


        ttk.Button(
            frame,
            text="Cargar Imagen",
            command=cargar_imagen
        ).pack(pady=10)


        ttk.Button(
            frame,
            text="Guardar",
            command=lambda: self.guardar_receta(titulo_entry, ingredientes_text, pasos_text, imagen_label, cerrar_formulario)
        ).pack(pady=20)

    def guardar_receta(self, titulo_entry, ingredientes_text, pasos_text, imagen_label, cerrar_formulario):
        titulo = titulo_entry.get().strip()
        ingredientes = ingredientes_text.get("1.0", "end").strip()
        pasos = pasos_text.get("1.0", "end").strip()
        imagen = getattr(imagen_label, "imagen", None)

        if not titulo or not ingredientes or not pasos:
            messagebox.showerror("Error", "Por favor completa todos los campos.")
            return

        if imagen:
            nueva_ruta = os.path.join("recetas_imagenes", os.path.basename(imagen))
            os.rename(imagen, nueva_ruta)
            imagen = nueva_ruta

        self.recetas.append({
            "titulo": titulo,
            "ingredientes": ingredientes,
            "pasos": pasos,
            "imagen": imagen
        })

        self.guardar_recetas()
        messagebox.showinfo("Éxito", "Receta guardada exitosamente.")
        cerrar_formulario()

    def ver_recetas(self):
        if self.ventana_ver_abierta:
            messagebox.showerror("Error", "Ya hay una ventana de ver recetas abierta.")
            return

        self.ventana_ver_abierta = True


        ventana_recetas = tk.Toplevel(self.root)
        ventana_recetas.title("Recetas Guardadas")
        ventana_recetas.geometry("1200x800")
        ventana_recetas.configure(bg=FONDO_COLOR)
        ventana_recetas.transient(self.root)
        ventana_recetas.grab_set()

        def cerrar_ventana():
            self.ventana_ver_abierta = False
            ventana_recetas.destroy()

        ventana_recetas.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        canvas = tk.Canvas(ventana_recetas, bg=FONDO_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(ventana_recetas, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Marco para buscador
        search_frame = ttk.Frame(ventana_recetas, padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="Buscar:", font=FONT_NORMAL).pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(search_frame, text="Buscar", command=lambda: buscar_recetas(search_entry.get().strip())).pack(side=tk.LEFT, padx=5)

        def buscar_recetas(filtro):
            filtro = filtro.lower()
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            for idx, receta in enumerate(self.recetas):
                if filtro in receta['titulo'].lower():
                    mostrar_receta(idx, receta, ventana_recetas)

        def mostrar_receta(idx, receta, ventana_recetas):
            receta_frame = ttk.Frame(scrollable_frame, padding=10)
            receta_frame.pack(fill=tk.BOTH, padx=10, pady=10)

            ttk.Label(
                receta_frame,
                text=f"{idx + 1}. {receta['titulo']}",
                font=FONT_TITULO,
                foreground=TITULO_COLOR
            ).pack(anchor="w")

            ttk.Label(
                receta_frame,
                text=f"Ingredientes: {receta['ingredientes']}",
                font=FONT_NORMAL
            ).pack(anchor="w")

            ttk.Label(
                receta_frame,
                text=f"Pasos: {receta['pasos']}",
                font=FONT_NORMAL
            ).pack(anchor="w")

            botones_frame = tk.Frame(receta_frame, bg=FONDO_COLOR)
            botones_frame.pack(anchor="w")

            ttk.Button(
                botones_frame, text="Editar",
                command=lambda: self.editar_receta(idx, ventana_recetas)
            ).pack(side=tk.LEFT, padx=5)

            ttk.Button(
                botones_frame, text="Exportar",
                command=lambda: self.exportar_receta(receta)
            ).pack(side=tk.LEFT, padx=5)

            ttk.Button(
                botones_frame, text="Eliminar",
                command=lambda: self.eliminar_receta(idx, ventana_recetas)
            ).pack(side=tk.LEFT, padx=5)

        for idx, receta in enumerate(self.recetas):
            mostrar_receta(idx, receta, ventana_recetas)

    def exportar_receta(self, receta):
        try:
            nombre_pdf = f"{receta['titulo']}.pdf"
            c = canvas.Canvas(nombre_pdf, pagesize=letter)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(100, 750, f"Receta: {receta['titulo']}")
            c.setFont("Helvetica", 14)
            c.drawString(100, 700, "Ingredientes:")
            c.setFont("Helvetica", 12)
            c.drawString(120, 680, receta['ingredientes'])
            c.setFont("Helvetica", 14)
            c.drawString(100, 640, "Pasos:")
            c.setFont("Helvetica", 12)
            c.drawString(120, 620, receta['pasos'])
            c.save()
            messagebox.showinfo("Éxito", f"Receta exportada como {nombre_pdf}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar la receta: {e}")

    def eliminar_receta(self, idx, ventana_recetas):
        """Elimina una receta de la lista y actualiza la interfaz."""
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar esta receta?")
        if confirm:

            receta_eliminada = self.recetas.pop(idx)


            if receta_eliminada.get("imagen") and os.path.exists(receta_eliminada["imagen"]):
                try:
                    os.remove(receta_eliminada["imagen"])
                    print(f"Imagen {receta_eliminada['imagen']} eliminada correctamente.")
                except Exception as e:
                    print(f"No se pudo eliminar la imagen {receta_eliminada['imagen']}: {e}")


            self.guardar_recetas()


            ventana_recetas.destroy()
            self.ventana_ver_abierta = False


            self.ver_recetas()


            messagebox.showinfo("Éxito", "Receta eliminada exitosamente.")

    def editar_receta(self, idx, ventana_recetas):
        receta = self.recetas[idx]
        ventana_recetas.destroy()
        self.ventana_ver_abierta = False

        ventana_editar = tk.Toplevel(self.root)
        ventana_editar.title(f"Editar Receta: {receta['titulo']}")
        ventana_editar.geometry("500x600")
        ventana_editar.configure(bg=FONDO_COLOR)
        ventana_editar.transient(self.root)
        ventana_editar.grab_set()

        def cerrar_ventana():
            ventana_editar.destroy()

        ventana_editar.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        frame = tk.Frame(ventana_editar, bg=FONDO_COLOR)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Título de la receta:", font=FONT_NORMAL).pack(pady=10, anchor="w")
        titulo_entry = ttk.Entry(frame, width=40)
        titulo_entry.insert(0, receta["titulo"])
        titulo_entry.pack(pady=5)

        ttk.Label(frame, text="Ingredientes:", font=FONT_NORMAL).pack(pady=10, anchor="w")
        ingredientes_text = tk.Text(frame, width=40, height=5)
        ingredientes_text.insert("1.0", receta["ingredientes"])
        ingredientes_text.pack(pady=5)

        ttk.Label(frame, text="Pasos:", font=FONT_NORMAL).pack(pady=10, anchor="w")
        pasos_text = tk.Text(frame, width=40, height=5)
        pasos_text.insert("1.0", receta["pasos"])
        pasos_text.pack(pady=5)

        imagen_label = ttk.Label(frame, text=os.path.basename(receta["imagen"]) if receta.get("imagen") else "No seleccionada", font=FONT_NORMAL)
        imagen_label.pack(pady=10)

        def cargar_imagen():
            ruta_imagen = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")])
            if ruta_imagen:
                imagen_label.config(text=os.path.basename(ruta_imagen))
                imagen_label.imagen = ruta_imagen

        ttk.Button(
            frame,
            text="Cargar Imagen",
            command=cargar_imagen
        ).pack(pady=10)

        def guardar_cambios():
            nuevo_titulo = titulo_entry.get().strip()
            nuevos_ingredientes = ingredientes_text.get("1.0", "end").strip()
            nuevos_pasos = pasos_text.get("1.0", "end").strip()
            nueva_imagen = getattr(imagen_label, "imagen", receta.get("imagen"))

            if not nuevo_titulo or not nuevos_ingredientes or not nuevos_pasos:
                messagebox.showerror("Error", "Por favor completa todos los campos.")
                return

            self.recetas[idx] = {
                "titulo": nuevo_titulo,
                "ingredientes": nuevos_ingredientes,
                "pasos": nuevos_pasos,
                "imagen": nueva_imagen
            }

            self.guardar_recetas()
            ventana_editar.destroy()
            self.ver_recetas()
            messagebox.showinfo("Éxito", "Receta actualizada exitosamente.")

        ttk.Button(
            frame,
            text="Guardar Cambios",
            command=guardar_cambios
        ).pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()