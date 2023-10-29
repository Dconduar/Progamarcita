import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, messagebox
from tkcalendar import Calendar
import sqlite3
import yagmail


yag = yagmail.SMTP('HospitaldeJalapa@gmail.com', 'dhpp olgw pwia nnzk')

# Funcion para cargar las citas al inicio 
def cargar_citas():
    listbox_citas.delete(0, 'end')  # Limpia las citas
    cursor.execute('SELECT nombre, edad, telefono, motivo, correo, fecha FROM citas')
    citas = cursor.fetchall()
    for cita in citas:
        # Muestra todos los detalles de la cita 
        detalles = f'Nombre: {cita[0]}, Edad: {cita[1]}, Teléfono: {cita[2]}, Motivo: {cita[3]}, Correo: {cita[4]}, Fecha: {cita[5]}'
        listbox_citas.insert('end', detalles)

# Conectar a la base de datos
conn = sqlite3.connect('citas.db')
cursor = conn.cursor()

# Crea una tabla para almacenar
cursor.execute('''
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        edad INTEGER,
        telefono TEXT,
        motivo TEXT,
        correo TEXT,
        fecha TEXT
    )
''')
conn.commit()

def abrir_calendario():
    fecha_seleccionada = cal.get_date()
    print("Fecha seleccionada:", fecha_seleccionada)

def toggle_calendario():
    if cal.winfo_viewable():
        cal.grid_remove()
    else:
        cal.grid()

def guardar_cita():
    nombre = entry_nombre.get()
    edad = entry_edad.get()
    telefono = entry_telefono.get()
    motivo = entry_motivo.get()
    correo = entry_correo.get()
    fecha = cal.get_date()  # Extrae la fecha que este seleccionada en el calendario

    # Insertar la cita en la base de datos
    cursor.execute('INSERT INTO citas (nombre, edad, telefono, motivo, correo, fecha) VALUES (?, ?, ?, ?, ?, ?)',
                   (nombre, edad, telefono, motivo, correo, fecha))
    conn.commit()
    print("Cita guardada en la base de datos")

    # Enviar un correo 
    contenido_correo = f"Su cita para el {fecha} ha sido programada. Motivo: {motivo}"
    yag.send(to=correo, subject="Confirmación de Cita", contents=contenido_correo)

    # Actualizar la lista de citas
    cargar_citas()

    # Borrar el contenido en los labels
    entry_nombre.delete(0, 'end')
    entry_edad.delete(0, 'end')
    entry_telefono.delete(0, 'end')
    entry_motivo.delete(0, 'end')
    entry_correo.delete(0, 'end')
    cal.set_date('')  # Borrar la fecha 

def editar_cita():
    # Obtener el índice seleccionado en la Listbox
    seleccion = listbox_citas.curselection()
    if not seleccion:
        messagebox.showwarning("Editar Cita", "Seleccione una cita para editar.")
        return

    index = seleccion[0]
    cita_seleccionada = listbox_citas.get(index)
    valores_cita = cita_seleccionada.split(", ")

    # Crear una ventana emergente para la edición
    ventana_editar = Toplevel(ventana)
    ventana_editar.title("Editar Cita")
    ventana_editar.geometry("300x200")

    label_fecha = Label(ventana_editar, text="Fecha:")
    entry_fecha = Entry(ventana_editar)
    label_motivo = Label(ventana_editar, text="Motivo:")
    entry_motivo = Entry(ventana_editar)
    label_nombre = Label(ventana_editar, text="Nombre:")
    entry_nombre = Entry(ventana_editar)
    label_telefono = Label(ventana_editar, text="Teléfono:")
    entry_telefono = Entry(ventana_editar)

    entry_fecha.insert(0, valores_cita[5].split(": ")[1])  
    entry_motivo.insert(0, valores_cita[3].split(": ")[1])  
    entry_nombre.insert(0, valores_cita[0].split(": ")[1])  
    entry_telefono.insert(0, valores_cita[2].split(": ")[1])  

    # Función para guardar los cambios en la cita
    def guardar_cambios():
        fecha = entry_fecha.get()
        motivo = entry_motivo.get()
        nombre = entry_nombre.get()
        telefono = entry_telefono.get()

        # Actualizar la cita en la base de datos
        cursor.execute('UPDATE citas SET fecha=?, motivo=?, nombre=?, telefono=? WHERE fecha=?',
                       (fecha, motivo, nombre, telefono, valores_cita[5].split(": ")[1]))
        conn.commit()
        ventana_editar.destroy()
        messagebox.showinfo("Editar Cita", "Cita modificada con éxito.")
        
        # Actualiza las citas
        cargar_citas()

    boton_guardar_cambios = Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios)

    label_fecha.pack()
    entry_fecha.pack()
    label_motivo.pack()
    entry_motivo.pack()
    label_nombre.pack()
    entry_nombre.pack()
    label_telefono.pack()
    entry_telefono.pack()
    boton_guardar_cambios.pack()

def eliminar_cita():

    seleccion = listbox_citas.curselection()
    if not seleccion:
        messagebox.showwarning("Eliminar Cita", "Seleccione una cita para eliminar.")
        return

    # Obtener la cita seleccionada
    index = seleccion[0]
    cita_seleccionada = listbox_citas.get(index)
    fecha_cita = cita_seleccionada.split(", ")[5].split(": ")[1]


    cursor.execute('DELETE FROM citas WHERE fecha=?', (fecha_cita,))
    conn.commit()


    listbox_citas.delete(index)

    messagebox.showinfo("Eliminar Cita", "Cita eliminada con éxito")

ventana = tk.Tk()
ventana.title("Aplicación de Citas")
ventana.geometry("800x600")

label_nombre = tk.Label(ventana, text="Nombre:")
label_edad = tk.Label(ventana, text="Edad:")
label_telefono = tk.Label(ventana, text="Teléfono:")
label_motivo = tk.Label(ventana, text="Motivo de Cita:")
label_correo = tk.Label(ventana, text="Correo Electrónico")

entry_nombre = tk.Entry(ventana)
entry_edad = tk.Entry(ventana)
entry_telefono = tk.Entry(ventana)
entry_motivo = tk.Entry(ventana)
entry_correo = tk.Entry(ventana)

boton_guardar = tk.Button(ventana, text="Guardar", command=guardar_cita)
boton_editar = tk.Button(ventana, text="Editar", command=editar_cita)
boton_eliminar = tk.Button(ventana, text="Eliminar", command=eliminar_cita)

cal = Calendar(ventana, selectmode="day", date_pattern="dd/MM/yyyy")
cal.grid(row=1, column=6, columnspan=2, padx=10, pady=10)
cal.grid_remove()

cal.bind("<Button-1>", lambda e: "break")  

boton_mostrar_calendario = tk.Button(ventana, text="Mostrar Calendario", command=toggle_calendario)

listbox_citas = tk.Listbox(ventana, selectmode=tk.SINGLE,width=120, height=10)
listbox_citas.grid(row=8, column=1, rowspan=7, padx=10, pady=10)

label_nombre.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
entry_nombre.grid(row=0, column=1, padx=10, pady=5)
label_edad.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
entry_edad.grid(row=1, column=1, padx=10, pady=5)
label_telefono.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
entry_telefono.grid(row=2, column=1, padx=10, pady=5)
label_motivo.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
entry_motivo.grid(row=3, column=1, padx=10, pady=5)
label_correo.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
entry_correo.grid(row=4, column=1, padx=10, pady=5)

boton_guardar.grid(row=5, column=0, padx=10, pady=10)
boton_editar.grid(row=5, column=1, padx=10, pady=10)
boton_eliminar.grid(row=5, column=2, padx=10, pady=10)
boton_mostrar_calendario.grid(row=0, column=4, columnspan=2, padx=10, pady=10)

# Cargar las citas al inicio
cargar_citas()

ventana.mainloop()

# Cerrar la conexión a la base de datos al finalizar la aplicación
conn.close()
