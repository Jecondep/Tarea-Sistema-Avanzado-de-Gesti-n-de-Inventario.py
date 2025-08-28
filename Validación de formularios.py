import sqlite3

class Producto:
    """
    Representa un producto en el inventario con ID único, nombre, cantidad y precio.
    """
    def __init__(self, id_producto, nombre, cantidad, precio):
        self._id = id_producto
        self._nombre = nombre
        self._cantidad = cantidad
        self._precio = precio

    # Métodos para obtener y modificar atributos
    def obtener_id(self):
        return self._id

    def obtener_nombre(self):
        return self._nombre

    def establecer_nombre(self, nuevo_nombre):
        self._nombre = nuevo_nombre

    def obtener_cantidad(self):
        return self._cantidad

    def establecer_cantidad(self, nueva_cantidad):
        self._cantidad = nueva_cantidad

    def obtener_precio(self):
        return self._precio

    def establecer_precio(self, nuevo_precio):
        self._precio = nuevo_precio

    def __repr__(self):
        return (f"Producto[ID={self._id}, Nombre='{self._nombre}', "
                f"Cantidad={self._cantidad}, Precio=${self._precio:.2f}]")


class Inventario:
    """
    Gestiona un conjunto de productos usando un diccionario para acceso rápido por ID.
    Además sincroniza los datos con una base de datos SQLite.
    """
    def __init__(self, nombre_db="libreria_inventario.db"):
        self._nombre_db = nombre_db
        self._productos = {}  # Diccionario: clave=ID, valor=Producto
        self._conexion = sqlite3.connect(self._nombre_db)
        self._cursor = self._conexion.cursor()
        self._crear_tabla_si_no_existe()
        self._cargar_productos()

    def _crear_tabla_si_no_existe(self):
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL
            )
        """)
        self._conexion.commit()

    def _cargar_productos(self):
        self._cursor.execute("SELECT id, nombre, cantidad, precio FROM productos")
        filas = self._cursor.fetchall()
        for id_producto, nombre, cantidad, precio in filas:
            self._productos[id_producto] = Producto(id_producto, nombre, cantidad, precio)

    def agregar_producto(self, producto):
        if producto.obtener_id() in self._productos:
            print(f"Ya existe un producto con ID {producto.obtener_id()}.")
            return False
        self._productos[producto.obtener_id()] = producto
        self._cursor.execute(
            "INSERT INTO productos (id, nombre, cantidad, precio) VALUES (?, ?, ?, ?)",
            (producto.obtener_id(), producto.obtener_nombre(),
             producto.obtener_cantidad(), producto.obtener_precio())
        )
        self._conexion.commit()
        print(f"Producto '{producto.obtener_nombre()}' agregado con éxito.")
        return True

    def eliminar_producto_por_id(self, id_producto):
        if id_producto not in self._productos:
            print(f"No se encontró producto con ID {id_producto}.")
            return False
        del self._productos[id_producto]
        self._cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        self._conexion.commit()
        print(f"Producto con ID {id_producto} eliminado.")
        return True

    def actualizar_producto(self, id_producto, nueva_cantidad=None, nuevo_precio=None):
        if id_producto not in self._productos:
            print(f"No existe producto con ID {id_producto}.")
            return False
        producto = self._productos[id_producto]
        if nueva_cantidad is not None:
            producto.establecer_cantidad(nueva_cantidad)
        if nuevo_precio is not None:
            producto.establecer_precio(nuevo_precio)
        self._cursor.execute(
            "UPDATE productos SET cantidad = ?, precio = ? WHERE id = ?",
            (producto.obtener_cantidad(), producto.obtener_precio(), id_producto)
        )
        self._conexion.commit()
        print(f"Producto con ID {id_producto} actualizado.")
        return True

    def buscar_productos_por_nombre(self, texto_busqueda):
        texto_busqueda = texto_busqueda.lower()
        encontrados = [p for p in self._productos.values() if texto_busqueda in p.obtener_nombre().lower()]
        if encontrados:
            print(f"Productos que contienen '{texto_busqueda}':")
            for p in encontrados:
                print(p)
        else:
            print(f"No se encontraron productos con nombre que contenga '{texto_busqueda}'.")

    def mostrar_todos_los_productos(self):
        if not self._productos:
            print("El inventario está vacío.")
            return
        print("Listado completo de productos en inventario:")
        for producto in self._productos.values():
            print(producto)

    def cerrar_conexion(self):
        self._conexion.close()


def mostrar_menu():
    print("\n=== Sistema de Gestión de Inventario - Librería ===")
    print("1. Agregar producto")
    print("2. Eliminar producto por ID")
    print("3. Actualizar cantidad o precio")
    print("4. Buscar producto por nombre")
    print("5. Mostrar todos los productos")
    print("6. Salir")


def main():
    inventario = Inventario()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":
            try:
                id_producto = int(input("ID del producto (entero): "))
                nombre = input("Nombre del producto: ").strip()
                cantidad = int(input("Cantidad disponible: "))
                precio = float(input("Precio unitario: "))
                nuevo_producto = Producto(id_producto, nombre, cantidad, precio)
                inventario.agregar_producto(nuevo_producto)
            except ValueError:
                print("Error: Por favor ingrese valores válidos para ID, cantidad y precio.")

        elif opcion == "2":
            try:
                id_producto = int(input("Ingrese el ID del producto a eliminar: "))
                inventario.eliminar_producto_por_id(id_producto)
            except ValueError:
                print("Error: El ID debe ser un número entero.")

        elif opcion == "3":
            try:
                id_producto = int(input("ID del producto a actualizar: "))
                cantidad_str = input("Nueva cantidad (dejar vacío para no cambiar): ").strip()
                precio_str = input("Nuevo precio (dejar vacío para no cambiar): ").strip()

                cantidad = int(cantidad_str) if cantidad_str else None
                precio = float(precio_str) if precio_str else None

                if cantidad is None and precio is None:
                    print("No se ingresaron cambios.")
                else:
                    inventario.actualizar_producto(id_producto, cantidad, precio)
            except ValueError:
                print("Error: Cantidad y precio deben ser números válidos.")

        elif opcion == "4":
            texto = input("Ingrese texto para buscar en el nombre: ").strip()
            inventario.buscar_productos_por_nombre(texto)

        elif opcion == "5":
            inventario.mostrar_todos_los_productos()

        elif opcion == "6":
            inventario.cerrar_conexion()
            print("Gracias por usar el sistema. ¡Hasta pronto!")
            break

        else:
            print("Opción inválida. Por favor seleccione una opción del 1 al 6.")


if __name__ == "__main__":
    main()
