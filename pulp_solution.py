from pulp import LpProblem, LpVariable, LpMaximize, LpStatus, value

class SolucionPulp:
    def __init__(self, datos_quimicos, datos_materias, datos_ganancias_por_quimicos):
        self.datos_quimicos = datos_quimicos
        self.datos_materias = datos_materias
        self.datos_ganancias = datos_ganancias_por_quimicos
        self.problema = LpProblem("Maximizar_Ganancias", LpMaximize)
        self.variables = self.definir_variables()
        self.definir_funcion_objetivo()
        self.definir_restricciones()

    def definir_variables(self):
        variables = {}
        for quimico in self.datos_quimicos:
            nombre_variable = quimico[0].replace(" ", "")
            variables[quimico[0]] = LpVariable(nombre_variable, lowBound=0, cat="Integer")
        return variables

    def definir_funcion_objetivo(self):
        self.problema += sum(self.variables[quimico[0]] * ganancia[1] for quimico, ganancia in zip(self.datos_quimicos, self.datos_ganancias)), "Maximizar_Ganancias"

    def definir_restricciones(self):
        for i in range(2, len(self.datos_materias[0]) + 2):
            restriccion = sum(int(quimico[i]) * self.variables[quimico[0]] for quimico in self.datos_quimicos)
            self.problema += restriccion <= int(self.datos_materias[i - 2][2])  # Corrección en el índice

    def resolver(self):
        self.problema.solve()

    def obtener_resultados(self):
        estado = LpStatus[self.problema.status]
        ganancia_maxima = value(self.problema.objective)
        cantidades = {quimico[0]: value(self.variables[quimico[0]].varValue) for quimico in self.datos_quimicos}
        return estado, ganancia_maxima, cantidades

    def generar_codigo_minizinc(self, cantidades):
        codigo_minizinc = "int: num_quimicos;\n"
        codigo_minizinc += "set of int: quimicos = 1..num_quimicos;\n"

        # Definir parámetros
        # Convertir las ganancias a enteros
        ganancias_entero = [int(ganancia[1]) for ganancia in self.datos_ganancias]
        # Formatear ganancias como un solo array
        codigo_minizinc += f"array[quimicos] of int: ganancias = {ganancias_entero};\n"

        for quimico in self.datos_quimicos:
            # Redondear la cantidad a un entero antes de agregarla al código
            cantidad_entero = round(cantidades[quimico[0]])
            codigo_minizinc += f"var int: cantidad_{quimico[0]} = {cantidad_entero};\n"

        # Definir restricciones
        for i in range(2, len(self.datos_materias[0]) + 2):
            try:
                cantidad_disponible = self.validar_cantidad(self.datos_materias[i - 2][2])
            except ValueError:
                print(f"Error: La cantidad de materia prima {self.datos_materias[i - 2][0]} no es un número válido.")
                continue

            restriccion = sum(int(quimico[i]) * cantidades[quimico[0]] for quimico in self.datos_quimicos)
            codigo_minizinc += f"constraint {restriccion} <= {cantidad_disponible};\n"

        # Definir función objetivo
        objetivo = sum(cantidades[quimico[0]] * int(ganancia[1]) for quimico, ganancia in zip(self.datos_quimicos, self.datos_ganancias))
        # Redondear la cantidad total a un entero antes de agregarla al código
        objetivo_entero = round(objetivo)
        codigo_minizinc += f"var int: ganancia_total = {objetivo_entero};\n"
        codigo_minizinc += "solve maximize ganancia_total;\n"

        return codigo_minizinc




    def validar_cantidad(self, cantidad_str):
        cantidad_str = ''.join(filter(str.isdigit, cantidad_str))
        return int(cantidad_str)