import tkinter as tk
from tkinter import ttk, messagebox
from pulp_solution import SolucionPulp

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto MiniZinc")

        # Crear TextArea para ingresar datos
        self.textarea_frame = ttk.Frame(root)
        self.textarea_frame.pack(pady=10)
        self.textarea = tk.Text(self.textarea_frame, width=50, height=10)
        self.textarea.pack()

        # Crear botón para resolver el problema
        self.boton_resolver = ttk.Button(root, text="Resolver Problema", command=self.resolver_problema)
        self.boton_resolver.pack(pady=10)

        # Crear Text widget para mostrar resultados
        self.resultados_text = tk.Text(root, wrap="word", width=50, height=10)
        self.resultados_text.pack(pady=10)

    def obtener_datos_tabla(self, treeview):
        # Obtener datos de la tabla
        datos = []
        for item in treeview.get_children():
            values = [treeview.item(item, "values")[i] for i in range(len(treeview["columns"]))]
            datos.append(values)
        return datos

    def resolver_problema(self):
        datos_str = self.textarea.get("1.0", tk.END)
        lineas = datos_str.split("\n")
        datos_quimicos = []
        datos_materias = []
        datos_ganancias_por_quimicos = []

        try:
            n_quimicos = int(lineas[0])
            n_materias = int(lineas[1])
            total_materias = 0

            if n_quimicos < 1 or n_materias < 1:
                raise ValueError("La cantidad de químicos y materias primas debe ser mayor o igual a 1")

            for i in range(2, 2 + n_quimicos):
                datos_quimicos.append(tuple(map(str, lineas[i].split())))

            for i in range(2 + n_quimicos, 2 + n_quimicos + n_materias):
                datos_materias.append(tuple(map(str, lineas[i].split())))
                total_materias += 1

            for cantidad_materia in datos_quimicos:
                nombre_quimico = cantidad_materia[0]
                precio_venta = int(cantidad_materia[1])
                costo_total = sum(int(cantidad_materia[i]) * int(datos_materias[i - 2][1]) for i in range(2, len(cantidad_materia)))
                ganancia = precio_venta - costo_total
                datos_ganancias_por_quimicos.append((nombre_quimico, ganancia))

            # Crear instancia de SolucionPulp
            solucion_pulp = SolucionPulp(datos_quimicos, datos_materias, datos_ganancias_por_quimicos)

            # Resolver el problema
            solucion_pulp.resolver()

            # Obtener y mostrar resultados en la consola
            estado, ganancia_maxima, cantidades = solucion_pulp.obtener_resultados()
            print("Estado:", estado)
            print("Ganancia máxima:", ganancia_maxima)
            print("Cantidad de cada producto químico a producir:")
            for quimico, cantidad in cantidades.items():
                print(f"{quimico}: {cantidad}")

            # Mostrar resultados en la GUI
            self.mostrar_resultados(estado, ganancia_maxima, cantidades)

            # Crear instancia de SolucionPulp
            solucion_pulp = SolucionPulp(datos_quimicos, datos_materias, datos_ganancias_por_quimicos)

            # Resolver el problema
            solucion_pulp.resolver()

            # Obtener resultados
            estado, ganancia_maxima, cantidades = solucion_pulp.obtener_resultados()

            # Generar código MiniZinc
            codigo_minizinc = solucion_pulp.generar_codigo_minizinc(cantidades)

            # Limpiar el Text widget y agregar el código MiniZinc
            self.resultados_text.delete(1.0, tk.END)
            self.resultados_text.insert(tk.END, codigo_minizinc)


        except ValueError as e:
            messagebox.showerror("Error", f"Error al procesar los datos: {str(e)}")

    def mostrar_resultados(self, estado, ganancia_maxima, cantidades):
        resultados_text = f"Estado: {estado}\n"
        resultados_text += f"Ganancia máxima: {ganancia_maxima}\n"
        resultados_text += "Cantidad de cada producto químico a producir:\n"
        for quimico, cantidad in cantidades.items():
            resultados_text += f"{quimico}: {cantidad}\n"

        # Limpiar el Text widget y agregar los nuevos resultados
        self.resultados_text.delete(1.0, tk.END)
        self.resultados_text.insert(tk.END, resultados_text)

# Crear ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
