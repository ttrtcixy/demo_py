import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3

class SupplierManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def get_suppliers_for_material(self, material_id):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT s.id, s.supplier_name, s.supplier_type, 
                       s.inn, s.rating, s.start_date
                FROM Suppliers s
                JOIN Material_suppliers ms ON s.id = ms.supplier_id
                WHERE ms.material_id = ?
                ORDER BY s.rating DESC NULLS LAST
            """, (material_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения поставщиков: {e}")
            return []

class MaterialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Приложение учета материалов")
        self.root.geometry("1200x700")
        self.root.configure(bg='white')
        
        try:
            self.root.iconbitmap('resources/app_icon.ico')
        except:
            pass
        
        # Установка шрифта Gabriola
        self.set_fonts()
        
        self.db_connection = self.create_connection("demoDB.db")
        self.supplier_manager = SupplierManager(self.db_connection)
        
        self.create_widgets()
        self.load_materials()
    
    def set_fonts(self):
        # Создаем кастомные стили шрифтов
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Gabriola", size=10)
        
        text_font = font.nametofont("TkTextFont")
        text_font.configure(family="Gabriola", size=10)
        
        fixed_font = font.nametofont("TkFixedFont")
        fixed_font.configure(family="Gabriola", size=10)
        
        # Стили для Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        font=("Gabriola", 10),
                        rowheight=25)
        style.configure("Treeview.Heading", 
                       font=("Gabriola", 10, "bold"))
    
    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к базе данных:\n{e}")
            return None
    
    def create_widgets(self):
        # Создаем Notebook для вкладок
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Вкладка материалов
        self.materials_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.materials_tab, text='Материалы')
        
        # Вкладка поставщиков
        self.suppliers_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.suppliers_tab, text='Поставщики')
        
        # Содержимое вкладки материалов
        self.create_materials_tab()
        # Содержимое вкладки поставщиков
        self.create_suppliers_tab()
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, background="#BBD9B2")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_materials_tab(self):
        # Основной фрейм материалов
        main_frame = ttk.Frame(self.materials_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview для материалов
        self.tree = ttk.Treeview(main_frame, columns=('type', 'name', 'min_qty', 'stock', 'price', 'unit'), 
                                show='headings', style="Custom.Treeview")
        self.tree.heading('type', text='Тип')
        self.tree.heading('name', text='Наименование')
        self.tree.heading('min_qty', text='Мин. кол-во')
        self.tree.heading('stock', text='На складе')
        self.tree.heading('price', text='Цена')
        self.tree.heading('unit', text='Ед. изм.')
        
        # Настройка стиля Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview", 
                       background="white",
                       fieldbackground="white",
                       foreground="black")
        style.map("Custom.Treeview", 
                 background=[('selected', '#BBD9B2')])
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.materials_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        add_btn = tk.Button(btn_frame, text="Добавить материал", 
                           bg="#2D6033", fg="white", font=("Gabriola", 10),
                           command=self.open_add_form)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = tk.Button(btn_frame, text="Редактировать", 
                            bg="#2D6033", fg="white", font=("Gabriola", 10),
                            command=self.open_edit_form)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(btn_frame, text="Обновить", 
                               bg="#2D6033", fg="white", font=("Gabriola", 10),
                               command=self.load_materials)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_suppliers_tab(self):
        # Основной фрейм для поставщиков
        main_frame = ttk.Frame(self.suppliers_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Фрейм для списка материалов
        materials_frame = ttk.Frame(main_frame, width=300)
        materials_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Label(materials_frame, text="Список материалов", 
                bg="#BBD9B2", fg="black", font=("Gabriola", 12, "bold")).pack(fill=tk.X, pady=5)
        
        # Treeview для материалов
        self.materials_tree_suppliers = ttk.Treeview(
            materials_frame, 
            columns=('name',), 
            show='headings',
            style="Custom.Treeview"
        )
        self.materials_tree_suppliers.heading('name', text='Наименование')
        self.materials_tree_suppliers.column('name', width=250)
        self.materials_tree_suppliers.pack(fill=tk.BOTH, expand=True)
        
        # Привязка события выбора материала
        self.materials_tree_suppliers.bind('<<TreeviewSelect>>', self.on_material_select)
        
        # Фрейм для списка поставщиков
        suppliers_frame = ttk.Frame(main_frame)
        suppliers_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(suppliers_frame, text="Поставщики выбранного материала", 
                bg="#BBD9B2", fg="black", font=("Gabriola", 12, "bold")).pack(fill=tk.X, pady=5)
        
        # Treeview для поставщиков
        self.suppliers_tree = ttk.Treeview(
            suppliers_frame, 
            columns=('name', 'type', 'inn', 'rating', 'date'), 
            show='headings',
            style="Custom.Treeview"
        )
        
        self.suppliers_tree.heading('name', text='Поставщик')
        self.suppliers_tree.heading('type', text='Тип')
        self.suppliers_tree.heading('inn', text='ИНН')
        self.suppliers_tree.heading('rating', text='Рейтинг')
        self.suppliers_tree.heading('date', text='Дата начала работы')
        
        self.suppliers_tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка обновления
        refresh_btn = tk.Button(
            suppliers_frame, 
            text="Обновить список", 
            bg="#2D6033", fg="white", font=("Gabriola", 10),
            command=self.load_suppliers_for_selected
        )
        refresh_btn.pack(pady=5)
    
    def on_material_select(self, event):
        """Обработчик выбора материала в списке поставщиков"""
        self.load_suppliers_for_selected()
    
    def load_suppliers_for_selected(self):
        """Загрузка поставщиков для выбранного материала"""
        selected_item = self.materials_tree_suppliers.selection()
        if not selected_item:
            return
            
        material_id = int(selected_item[0])
        suppliers = self.supplier_manager.get_suppliers_for_material(material_id)
        
        self.suppliers_tree.delete(*self.suppliers_tree.get_children())
        
        for supplier in suppliers:
            self.suppliers_tree.insert('', tk.END, values=(
                supplier['supplier_name'],
                supplier['supplier_type'],
                supplier['inn'],
                supplier['rating'],
                supplier['start_date']
            ))
    
    def load_materials(self):
        try:
            # Очищаем оба treeview
            self.tree.delete(*self.tree.get_children())
            self.materials_tree_suppliers.delete(*self.materials_tree_suppliers.get_children())
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT m.id, m.material_name, mt.material_type as type_name, 
                       m.min_quantity, m.stock_quantity, m.unit_price, m.unit_of_measure
                FROM Materials m
                JOIN Material_type mt ON m.material_type_id = mt.id
                ORDER BY m.material_name
            """)
            
            for row in cursor.fetchall():
                # Заполняем основной список
                self.tree.insert('', tk.END, values=(
                    row['type_name'],
                    row['material_name'],
                    row['min_quantity'],
                    row['stock_quantity'],
                    row['unit_price'],
                    row['unit_of_measure']
                ), iid=row['id'])
                
                # Заполняем список для вкладки поставщиков
                self.materials_tree_suppliers.insert('', tk.END, values=(
                    row['material_name'],
                ), iid=row['id'])
            
            self.status_var.set(f"Загружено материалов: {len(self.tree.get_children())}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить материалы:\n{e}")
    
    def open_add_form(self):
        form = MaterialForm(self.root, self.db_connection)
        if form.result:
            self.load_materials()
    
    def open_edit_form(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите материал для редактирования")
            return
            
        material_id = int(selected_item[0])
        form = MaterialForm(self.root, self.db_connection, material_id)
        if form.result:
            self.load_materials()

class MaterialForm:
    def __init__(self, parent, db_connection, material_id=None):
        self.db_connection = db_connection
        self.material_id = material_id
        self.result = False
        
        self.top = tk.Toplevel(parent)
        self.top.title("Добавить материал" if material_id is None else "Редактировать материал")
        self.top.geometry("400x500")
        self.top.configure(bg='white')
        
        self.create_widgets()
        if material_id is not None:
            self.load_material_data()
        
        self.top.grab_set()
        self.top.wait_window()
    
    def create_widgets(self):
        main_frame = tk.Frame(self.top, bg='white', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля формы
        tk.Label(main_frame, text="Наименование:", bg='white', 
                font=("Gabriola", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(main_frame, font=("Gabriola", 10))
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        tk.Label(main_frame, text="Тип материала:", bg='white', 
                font=("Gabriola", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_combo = ttk.Combobox(main_frame, font=("Gabriola", 10))
        self.type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.load_material_types()
        
        tk.Label(main_frame, text="Количество на складе:", bg='white', 
                font=("Gabriola", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.stock_entry = tk.Entry(main_frame, font=("Gabriola", 10))
        self.stock_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        tk.Label(main_frame, text="Единица измерения:", bg='white', 
                font=("Gabriola", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.unit_entry = tk.Entry(main_frame, font=("Gabriola", 10))
        self.unit_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        tk.Label(main_frame, text="Количество в упаковке:", bg='white', 
                font=("Gabriola", 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.package_entry = tk.Entry(main_frame, font=("Gabriola", 10))
        self.package_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        tk.Label(main_frame, text="Минимальное количество:", bg='white', 
                font=("Gabriola", 10)).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.min_qty_entry = tk.Entry(main_frame, font=("Gabriola", 10))
        self.min_qty_entry.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        tk.Label(main_frame, text="Цена за единицу:", bg='white', 
                font=("Gabriola", 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.price_entry = tk.Entry(main_frame, font=("Gabriola", 10))
        self.price_entry.grid(row=6, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(btn_frame, text="Сохранить", 
                            bg="#2D6033", fg="white", font=("Gabriola", 10),
                            command=self.save_material)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(btn_frame, text="Отмена", 
                              bg="#2D6033", fg="white", font=("Gabriola", 10),
                              command=self.top.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        main_frame.columnconfigure(1, weight=1)
    
    def load_material_types(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, material_type FROM Material_type")
            self.material_types = {row['material_type']: row['id'] for row in cursor.fetchall()}
            self.type_combo['values'] = list(self.material_types.keys())
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить типы материалов:\n{e}")
    
    def load_material_data(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT m.*, mt.material_type 
                FROM Materials m
                JOIN Material_type mt ON m.material_type_id = mt.id
                WHERE m.id = ?
            """, (self.material_id,))
            
            material = cursor.fetchone()
            if material:
                self.name_entry.insert(0, material['material_name'])
                self.type_combo.set(material['material_type'])
                self.stock_entry.insert(0, str(material['stock_quantity']))
                self.unit_entry.insert(0, material['unit_of_measure'])
                self.package_entry.insert(0, str(material['package_quantity']))
                self.min_qty_entry.insert(0, str(material['min_quantity']))
                self.price_entry.insert(0, str(material['unit_price']))
                
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные материала:\n{e}")
    
    def save_material(self):
        try:
            data = {
                'name': self.name_entry.get().strip(),
                'type': self.type_combo.get(),
                'stock': float(self.stock_entry.get()),
                'unit': self.unit_entry.get().strip(),
                'package': float(self.package_entry.get()),
                'min_qty': float(self.min_qty_entry.get()),
                'price': float(self.price_entry.get())
            }
            
            if not data['name']:
                messagebox.showwarning("Ошибка", "Введите наименование материала")
                return
                
            if not data['type']:
                messagebox.showwarning("Ошибка", "Выберите тип материала")
                return
                
            if data['stock'] < 0 or data['package'] <= 0 or data['min_qty'] < 0 or data['price'] <= 0:
                messagebox.showwarning("Ошибка", "Все числовые значения должны быть положительными")
                return
            
            cursor = self.db_connection.cursor()
            material_data = (
                data['name'],
                self.material_types[data['type']],
                data['price'],
                data['stock'],
                data['min_qty'],
                data['package'],
                data['unit']
            )
            
            if self.material_id is None:
                cursor.execute("""
                    INSERT INTO Materials 
                    (material_name, material_type_id, unit_price, stock_quantity, 
                     min_quantity, package_quantity, unit_of_measure)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, material_data)
            else:
                cursor.execute("""
                    UPDATE Materials SET
                    material_name = ?,
                    material_type_id = ?,
                    unit_price = ?,
                    stock_quantity = ?,
                    min_quantity = ?,
                    package_quantity = ?,
                    unit_of_measure = ?
                    WHERE id = ?
                """, material_data + (self.material_id,))
            
            self.db_connection.commit()
            self.result = True
            self.top.destroy()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные числовые значения")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MaterialApp(root)
    root.mainloop()