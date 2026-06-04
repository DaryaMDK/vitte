import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd
from dataset import (
    recursive_digit_sum,
    get_color_schemes,
    get_default_cmap,
    get_student_marker,
    get_default_pen_settings
)


class DataDrawApp:
    def __init__(self, root):
        self.cmap_var = None
        self.root = root
        self.root.title("Визуализация данных с рисованием")
        self.root.geometry("1200x900")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.df = pd.read_csv("dataset.csv")
        self.numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(exclude=['number']).columns.tolist()
        self.all_cols = self.numeric_cols + self.categorical_cols
        self.color_schemes = get_color_schemes()
        first_letter = 'М'
        self.default_cmap = get_default_cmap(first_letter)
        self.current_cmap = self.default_cmap
        self.marker_style = get_student_marker(70227995)
        student_id = 70227995
        self.default_pen_width, self.default_pen_color = get_default_pen_settings(student_id)
        self.pen_width = self.default_pen_width
        self.pen_color = self.default_pen_color
        self.drawing_mode = False
        self.current_lines = []
        self.current_line_points = []
        self.current_line_obj = None
        self.drawing = False
        self.x_column = self.all_cols[0] if self.all_cols else None
        self.y_column = self.all_cols[1] if len(self.all_cols) > 1 else self.all_cols[0]
        self.create_widgets()
        self.print_drawing_info()
        self.setup_drawing_events()
        self.update_plot()

    def print_drawing_info(self):
        student_id = 70227995
        digit_sum = recursive_digit_sum(student_id)
        print(f"Студенческий ID: {student_id}")
        print(f"Рекурсивная сумма цифр: {digit_sum}")
        print(f"Толщина линии по умолчанию: {self.default_pen_width} пикселей")
        print(f"(формула: {digit_sum} // 2 + 5 = {self.default_pen_width})")
        print(f"Цвет кисти по умолчанию: {self.default_pen_color}")
        print(f"(из последних 6 цифр ID 70227995 → {str(student_id)[-6:]})")
        print(f"Красный (R): {int(self.default_pen_color[1:3], 16)}")
        print(f"Зелёный (G): {int(self.default_pen_color[3:5], 16)}")
        print(f"Синий  (B): {int(self.default_pen_color[5:7], 16)}")

    def get_cmap(self, cmap_name):
        try:
            return plt.colormaps[cmap_name]
        except AttributeError:
            return plt.cm.get_cmap(cmap_name)

    def on_closing(self):
        plt.close('all')
        self.root.quit()
        self.root.destroy()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky="we", pady=5)

        ttk.Label(top_frame, text="Цветовая схема:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        self.cmap_var = tk.StringVar(value=self.default_cmap)
        cmap_combo = ttk.Combobox(top_frame, textvariable=self.cmap_var,
                                  values=list(self.color_schemes.values()),
                                  state='readonly', width=15)
        cmap_combo.pack(side=tk.LEFT, padx=5)
        cmap_combo.bind('<<ComboboxSelected>>', self.on_cmap_change)

        toolbar_frame = ttk.Frame(self.root, padding="10")
        toolbar_frame.grid(row=1, column=0, sticky="we", pady=5)

        self.draw_button = ttk.Button(toolbar_frame, text="Рисовать", command=self.toggle_drawing_mode)
        self.draw_button.pack(side=tk.LEFT, padx=5)
        self.color_button = tk.Canvas(toolbar_frame, width=50, height=30, bg=self.pen_color,
                                      highlightthickness=1, highlightbackground="black")
        self.color_button.pack(side=tk.LEFT, padx=5)
        self.color_button.bind("<Button-1>", self.choose_color)
        ttk.Label(toolbar_frame, text="Толщина:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.IntVar(value=self.pen_width)
        self.width_slider = ttk.Scale(toolbar_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                      variable=self.width_var, command=self.change_width)
        self.width_slider.pack(side=tk.LEFT, padx=5)
        self.width_label = ttk.Label(toolbar_frame, text=f"{self.pen_width}px")
        self.width_label.pack(side=tk.LEFT, padx=5)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=2, column=0, sticky="nsew")

        # Левая панель - ось X
        x_frame = ttk.LabelFrame(main_frame, text="Выберите колонку для оси X", padding="10")
        x_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        x_canvas = tk.Canvas(x_frame, height=300)
        x_scrollbar = ttk.Scrollbar(x_frame, orient="vertical", command=x_canvas.yview)
        x_scrollable_frame = ttk.Frame(x_canvas)
        x_scrollable_frame.bind("<Configure>", lambda e: x_canvas.configure(scrollregion=x_canvas.bbox("all")))
        x_canvas.create_window((0, 0), window=x_scrollable_frame, anchor="nw")
        x_canvas.configure(yscrollcommand=x_scrollbar.set)

        for i, col in enumerate(self.all_cols):
            btn = ttk.Button(x_scrollable_frame, text=col, command=lambda c=col: self.set_x_column(c))
            btn.grid(row=i, column=0, pady=2, sticky=tk.W)

        x_canvas.pack(side="left", fill="both", expand=True)
        x_scrollbar.pack(side="right", fill="y")

        # Правая панель - ось Y
        y_frame = ttk.LabelFrame(main_frame, text="Выберите колонку для оси Y", padding="10")
        y_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        y_canvas = tk.Canvas(y_frame, height=300)
        y_scrollbar = ttk.Scrollbar(y_frame, orient="vertical", command=y_canvas.yview)
        y_scrollable_frame = ttk.Frame(y_canvas)
        y_scrollable_frame.bind("<Configure>", lambda e: y_canvas.configure(scrollregion=y_canvas.bbox("all")))
        y_canvas.create_window((0, 0), window=y_scrollable_frame, anchor="nw")
        y_canvas.configure(yscrollcommand=y_scrollbar.set)

        for i, col in enumerate(self.all_cols):
            btn = ttk.Button(y_scrollable_frame, text=col, command=lambda c=col: self.set_y_column(c))
            btn.grid(row=i, column=0, pady=2, sticky=tk.W)

        y_canvas.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")

        # График
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)

        self.fig, self.ax = plt.subplots(figsize=(11, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Нижняя панель
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Label(bottom_frame, text="Ось X: ", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5)
        for i, col in enumerate(self.all_cols):
            btn = ttk.Button(bottom_frame, text=col, command=lambda c=col: self.set_x_column(c))
            btn.grid(row=0, column=i + 1, padx=2)

        ttk.Label(bottom_frame, text="Ось Y: ", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=(5, 0))
        for i, col in enumerate(self.all_cols):
            btn = ttk.Button(bottom_frame, text=col, command=lambda c=col: self.set_y_column(c))
            btn.grid(row=1, column=i + 1, padx=2, pady=(5, 0))

        save_btn = ttk.Button(bottom_frame, text="Сохранить график", command=self.save_plot)
        save_btn.grid(row=2, column=0, columnspan=len(self.all_cols) + 1, pady=10)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

    def setup_drawing_events(self):
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.root.bind('<Control-z>', self.undo_last_line)
        self.root.bind('<Control-Z>', self.undo_last_line)
        self.root.bind('<Button-3>', self.exit_drawing_mode)

    def toggle_drawing_mode(self):
        self.drawing_mode = not self.drawing_mode

        if self.drawing_mode:
            self.draw_button.state(['pressed'])
            self.canvas.get_tk_widget().config(cursor="pencil")
        else:
            self.draw_button.state(['!pressed'])
            self.canvas.get_tk_widget().config(cursor="")

    def exit_drawing_mode(self, event=None):
        if self.drawing_mode:
            self.drawing_mode = False
            self.draw_button.state(['!pressed'])
            self.canvas.get_tk_widget().config(cursor="")

    def choose_color(self, event=None):
        color = colorchooser.askcolor(initialcolor=self.pen_color, title="Выберите цвет кисти")
        if color[1]:
            self.pen_color = color[1]
            self.color_button.config(bg=self.pen_color)

    def change_width(self, event=None):
        self.pen_width = int(self.width_var.get())
        self.width_label.config(text=f"{self.pen_width}px")

    def on_mouse_press(self, event):
        if not self.drawing_mode or event.inaxes != self.ax:
            return

        if event.button == 1:
            self.drawing = True
            self.current_line_points = [(event.xdata, event.ydata)]
            self.current_line_obj = None

    def on_mouse_release(self, event):
        if self.drawing:
            self.drawing = False
            if self.current_line_obj is not None and len(self.current_line_points) > 1:
                self.current_lines.append(self.current_line_obj)
            self.current_line_obj = None
            self.current_line_points = []
            self.canvas.draw_idle()

    def on_mouse_move(self, event):
        if not self.drawing or not self.drawing_mode or event.inaxes != self.ax:
            return

        self.current_line_points.append((event.xdata, event.ydata))

        if self.current_line_obj is not None:
            self.current_line_obj.remove()

        x_points = [p[0] for p in self.current_line_points]
        y_points = [p[1] for p in self.current_line_points]

        self.current_line_obj, = self.ax.plot(x_points, y_points,
                                              color=self.pen_color,
                                              linewidth=self.pen_width,
                                              solid_capstyle='round',
                                              solid_joinstyle='round')
        self.canvas.draw_idle()

    def undo_last_line(self, event=None):
        if self.drawing:
            return

        if self.current_lines:
            last_line = self.current_lines.pop()
            try:
                last_line.remove()
                self.canvas.draw_idle()
                print(f"Линия удалена. Осталось линий: {len(self.current_lines)}")
            except Exception as e:
                print(f"Ошибка при удалении линии: {e}")
        else:
            print("Нет линий для удаления")

    def on_cmap_change(self, event=None):
        self.current_cmap = self.cmap_var.get()
        self.exit_drawing_mode()
        self.update_plot()

    def set_x_column(self, col):
        self.x_column = col
        self.exit_drawing_mode()
        self.update_plot()

    def set_y_column(self, col):
        self.y_column = col
        self.exit_drawing_mode()
        self.update_plot()

    def determine_plot_type(self):
        if self.x_column is None or self.y_column is None:
            return 'scatter'

        x_type = 'numeric' if self.x_column in self.numeric_cols else 'categorical'
        y_type = 'numeric' if self.y_column in self.categorical_cols else 'categorical'

        if x_type == 'numeric' and self.x_column == self.y_column:
            return 'histogram'
        if x_type == 'categorical' and self.x_column == self.y_column:
            return 'pie'
        if x_type == 'categorical':
            return 'bar'
        if y_type == 'categorical':
            return 'boxplot'
        return 'scatter'

    def update_plot(self):
        self.ax.clear()
        self.current_lines = []
        self.current_line_points = []
        self.current_line_obj = None
        self.drawing = False

        plot_type = self.determine_plot_type()

        try:
            if plot_type == 'histogram':
                self.plot_histogram()
            elif plot_type == 'pie':
                self.plot_pie()
            elif plot_type == 'bar':
                self.plot_bar()
            elif plot_type == 'boxplot':
                self.plot_boxplot()
            else:
                self.plot_scatter()
        except Exception as e:
            self.ax.text(0.5, 0.5, f'Ошибка построения графика:\n{str(e)}',
                         ha='center', va='center', transform=self.ax.transAxes)

        self.canvas.draw()

    def plot_histogram(self):
        data = self.df[self.x_column].dropna()
        if len(data) == 0:
            self.ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=self.ax.transAxes)
            return
        cmap = self.get_cmap(self.current_cmap)
        self.ax.hist(data, bins=10, edgecolor='black', alpha=0.7, color=cmap(0.5))
        self.ax.set_xlabel(self.x_column, fontsize=12)
        self.ax.set_ylabel('Частота', fontsize=12)
        self.ax.set_title(f'Гистограмма: {self.x_column}', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--')

    def plot_pie(self):
        data = self.df[self.x_column].dropna()
        value_counts = data.value_counts()
        if len(value_counts) == 0:
            self.ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=self.ax.transAxes)
            return
        cmap = self.get_cmap(self.current_cmap)
        colors = [cmap(i / len(value_counts)) for i in range(len(value_counts))]
        self.ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%',
                    colors=colors, startangle=90)
        self.ax.set_title(f'Круговая диаграмма: {self.x_column}', fontsize=14, fontweight='bold')
        self.ax.axis('equal')

    def plot_bar(self):
        data = self.df[self.x_column].dropna()
        value_counts = data.value_counts()
        if len(value_counts) == 0:
            self.ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=self.ax.transAxes)
            return
        cmap = self.get_cmap(self.current_cmap)
        colors = [cmap(i / len(value_counts)) for i in range(len(value_counts))]
        self.ax.bar(range(len(value_counts)), value_counts.values, color=colors, edgecolor='black')
        self.ax.set_xticks(range(len(value_counts)))
        self.ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
        self.ax.set_xlabel(self.x_column, fontsize=12)
        self.ax.set_ylabel('Количество записей', fontsize=12)
        self.ax.set_title(f'Столбчатая диаграмма: {self.x_column}', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    def plot_boxplot(self):
        categories = self.df[self.y_column].dropna().unique()
        data_to_plot = []
        labels = []
        for cat in categories:
            cat_data = self.df[self.df[self.y_column] == cat][self.x_column].dropna()
            if len(cat_data) > 0:
                data_to_plot.append(cat_data.values)
                labels.append(str(cat))
        if len(data_to_plot) == 0:
            self.ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=self.ax.transAxes)
            return
        cmap = self.get_cmap(self.current_cmap)
        colors = [cmap(i / len(data_to_plot)) for i in range(len(data_to_plot))]
        try:
            bp = self.ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True)
        except TypeError:
            bp = self.ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        self.ax.set_xlabel(self.y_column, fontsize=12)
        self.ax.set_ylabel(self.x_column, fontsize=12)
        self.ax.set_title(f'Коробочная диаграмма: {self.x_column} по категориям {self.y_column}',
                          fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        plt.xticks(rotation=45, ha='right')

    def plot_scatter(self):
        combined_data = self.df[[self.x_column, self.y_column]].dropna()
        if len(combined_data) == 0:
            self.ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=self.ax.transAxes)
            return
        x_plot = combined_data[self.x_column]
        y_plot = combined_data[self.y_column]
        cmap = self.get_cmap(self.current_cmap)
        self.ax.scatter(x_plot, y_plot, marker=self.marker_style, alpha=0.6, s=30,
                        color=cmap(0.5), edgecolors='black', linewidth=0.5)
        self.ax.set_xlabel(self.x_column, fontsize=12)
        self.ax.set_ylabel(self.y_column, fontsize=12)
        self.ax.set_title(f'Точечная диаграмма: {self.x_column} vs {self.y_column}',
                          fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--')

    def save_plot(self):
        now = datetime.now()
        filename = f"graph{now.hour:02d}_{now.minute:02d}_{now.second:02d}.png"

        try:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Сохранение", f"График сохранён как:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить график:\n{str(e)}")


def main():
    root = tk.Tk()
    DataDrawApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
