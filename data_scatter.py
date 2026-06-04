import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd
from dataset import recursive_digit_sum, get_marker_style


class ScatterPlotApp:
    def __init__(self, root):
        self.fig = None
        self.root = root
        self.root.title("Точечная диаграмма")
        self.root.geometry("900x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.df = pd.read_csv("dataset.csv")
        self.numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()

        student_id = 70227995
        style_num = recursive_digit_sum(student_id)
        self.marker_style = get_marker_style(style_num)

        self.x_column = self.numeric_cols[0]
        self.y_column = self.numeric_cols[1]
        self.create_widgets()
        self.update_plot()

    def on_closing(self):
        plt.close('all')
        self.root.quit()
        self.root.destroy()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Левая панель - ось X
        x_frame = ttk.LabelFrame(main_frame, text="Выберите колонку для оси X", padding="10")
        x_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        for i, col in enumerate(self.numeric_cols):
            btn = ttk.Button(x_frame, text=col, command=lambda c=col: self.set_x_column(c))
            btn.grid(row=i, column=0, pady=2, sticky=tk.W)

        # Правая панель - ось Y
        y_frame = ttk.LabelFrame(main_frame, text="Выберите колонку для оси Y", padding="10")
        y_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        for i, col in enumerate(self.numeric_cols):
            btn = ttk.Button(y_frame, text=col, command=lambda c=col: self.set_y_column(c))
            btn.grid(row=i, column=0, pady=2, sticky=tk.W)

        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # Кнопки оси X внизу
        ttk.Label(bottom_frame, text="Ось X: ", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5)
        for i, col in enumerate(self.numeric_cols):
            btn = ttk.Button(bottom_frame, text=col, command=lambda c=col: self.set_x_column(c))
            btn.grid(row=0, column=i + 1, padx=2)

        # Кнопки оси Y внизу
        ttk.Label(bottom_frame, text="Ось Y: ", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=(5, 0))
        for i, col in enumerate(self.numeric_cols):
            btn = ttk.Button(bottom_frame, text=col, command=lambda c=col: self.set_y_column(c))
            btn.grid(row=1, column=i + 1, padx=2, pady=(5, 0))

        save_btn = ttk.Button(bottom_frame, text="Сохранить график", command=self.save_plot)
        save_btn.grid(row=2, column=0, columnspan=len(self.numeric_cols) + 1, pady=10)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

    def set_x_column(self, col):
        self.x_column = col
        self.update_plot()

    def set_y_column(self, col):
        self.y_column = col
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        combined_data = self.df[[self.x_column, self.y_column]].dropna()
        x_plot = combined_data[self.x_column]
        y_plot = combined_data[self.y_column]

        self.ax.scatter(x_plot, y_plot, marker=self.marker_style, alpha=0.6, s=30, c='steelblue')
        self.ax.set_xlabel(self.x_column, fontsize=12)
        self.ax.set_ylabel(self.y_column, fontsize=12)
        self.ax.set_title(f'Точечная диаграмма: {self.x_column} vs {self.y_column}', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.canvas.draw()

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
    ScatterPlotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
