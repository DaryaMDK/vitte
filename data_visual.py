import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd
from dataset import (get_color_schemes, get_default_cmap, get_student_marker)
import dataset


class DataVisualApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация данных")
        self.root.geometry("1100x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.df = dataset.df
        self.numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(exclude=['number']).columns.tolist()
        self.all_cols = self.numeric_cols + self.categorical_cols
        self.color_schemes = get_color_schemes()
        first_letter = 'М'
        self.default_cmap = get_default_cmap(first_letter)
        self.current_cmap = self.default_cmap
        self.marker_style = get_student_marker(70227995)
        self.x_column = self.all_cols[0] if self.all_cols else None
        self.y_column = self.all_cols[1] if len(self.all_cols) > 1 else self.all_cols[0]
        self.create_widgets()
        self.print_color_scheme_info()
        self.update_plot()

    def get_cmap(self, cmap_name):
        try:
            return plt.colormaps[cmap_name]
        except AttributeError:
            return plt.cm.get_cmap(cmap_name)

    def print_color_scheme_info(self):
        print(f"Первая буква фамилии: М")
        print(f"Выбранная цветовая схема по умолчанию: '{self.default_cmap}'")
        print(f"Стиль маркера для точечной диаграммы: '{self.marker_style}'")

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

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky="nsew")

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

        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)

        self.fig, self.ax = plt.subplots(figsize=(10, 7))
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

        # Кнопка сохранения
        save_btn = ttk.Button(bottom_frame, text="Сохранить график", command=self.save_plot)
        save_btn.grid(row=2, column=0, columnspan=len(self.all_cols) + 1, pady=10)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

    def on_cmap_change(self, event=None):
        self.current_cmap = self.cmap_var.get()
        self.update_plot()

    def set_x_column(self, col):
        self.x_column = col
        self.update_plot()

    def set_y_column(self, col):
        self.y_column = col
        self.update_plot()

    def determine_plot_type(self):
        if not self.x_column or not self.y_column:
            return 'scatter'

        x_num = self.x_column in self.numeric_cols
        y_num = self.y_column in self.numeric_cols
        same = self.x_column == self.y_column

        if x_num and y_num:
            return 'histogram' if same else 'scatter'
        if not x_num and not y_num:
            return 'pie' if same else 'bar'
        if not x_num and y_num:
            return 'bar'
        if x_num and not y_num:
            return 'boxplot'

        return 'scatter'

    def update_plot(self):
        self.ax.clear()
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
            self.ax.text(0.5, 0.5, f'{str(e)}',
                         ha='center', va='center', transform=self.ax.transAxes)
        self.canvas.draw()

    def plot_histogram(self):
        data = self.df[self.x_column].dropna()

        if len(data) == 0:
            self.ax.text(0.5, 0.5, 'Нет данных для отображения',
                         ha='center', va='center', transform=self.ax.transAxes)
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
            self.ax.text(0.5, 0.5, 'Нет данных для отображения',
                         ha='center', va='center', transform=self.ax.transAxes)
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
            self.ax.text(0.5, 0.5, 'Нет данных для отображения',
                         ha='center', va='center', transform=self.ax.transAxes)
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
            self.ax.text(0.5, 0.5, 'Нет данных для отображения',
                         ha='center', va='center', transform=self.ax.transAxes)
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
            self.ax.text(0.5, 0.5, 'Нет данных для отображения',
                         ha='center', va='center', transform=self.ax.transAxes)
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
    DataVisualApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
