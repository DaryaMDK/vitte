import pandas as pd
from pathlib import Path
import sys


df = pd.read_csv("dataset.csv")


class Report:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)

    def flush(self):
        for f in self.files:
            f.flush()


def recursive_digit_sum(n: int) -> int:
    n = abs(int(n))
    if n < 10:
        return n
    return recursive_digit_sum(sum(int(d) for d in str(n)))


def get_marker_style(style_number: int) -> str:
    styles = {
        1: '^', 2: '>', 3: 'o', 4: 's', 5: 'P',
        6: 'h', 7: '*', 8: 'H', 9: '<'
    }
    return styles.get(style_number, 'o')


def get_color_schemes() -> dict:
    return {
        'А': 'viridis', 'Б': 'plasma', 'В': 'inferno', 'Г': 'magma',
        'Д': 'cividis', 'Е': 'Greys', 'Ё': 'Greys', 'Ж': 'Purples',
        'З': 'Blues', 'И': 'Greens', 'Й': 'Oranges', 'К': 'Reds',
        'Л': 'YlOrBr', 'М': 'YlOrRd', 'Н': 'OrRd', 'О': 'PuRd',
        'П': 'RdPu', 'Р': 'BuPu', 'С': 'GnBu', 'Т': 'PuBu',
        'У': 'YlGnBu', 'Ф': 'PuBuGn', 'Х': 'BuGn', 'Ц': 'YlGn',
        'Ч': 'binary', 'Ш': 'gist_yarg', 'Щ': 'spring', 'Э': 'summer',
        'Ю': 'autumn', 'Я': 'winter'
    }


def get_default_cmap(first_letter: str) -> str:
    schemes = get_color_schemes()
    return schemes.get(first_letter, 'viridis')


def get_student_marker(student_id: int = 70227995) -> str:
    style_num = recursive_digit_sum(student_id)
    return get_marker_style(style_num)


def get_default_pen_settings(student_id: int = 70227995) -> tuple:
    digit_sum = recursive_digit_sum(student_id)
    pen_width = digit_sum // 2 + 5
    id_str = str(student_id)
    last_6 = id_str[-6:]
    r = int(last_6[0:2])
    g = int(last_6[2:4])
    b = int(last_6[4:6])
    pen_color = f'#{r:02x}{g:02x}{b:02x}'

    return pen_width, pen_color


def calculate_digit_sum_steps(student_id: int):
    num_str = str(student_id)
    current_sum = sum(int(d) for d in num_str)
    steps = [f"{' + '.join(num_str)} = {current_sum}"]

    while current_sum >= 10:
        next_sum = sum(int(d) for d in str(current_sum))
        steps.append(f"{' + '.join(str(current_sum))} = {next_sum}")
        current_sum = next_sum

    return steps, current_sum


def main():
    student_id = 70227995
    first_letter = 'М'
    steps, final_result = calculate_digit_sum_steps(student_id)
    style = recursive_digit_sum(student_id)
    marker = get_marker_style(style)
    default_cmap = get_default_cmap(first_letter)
    pen_width, pen_color = get_default_pen_settings(student_id)
    original_stdout = sys.stdout
    report_path = Path("report.txt")
    report_file = open(report_path, "w", encoding="utf-8")
    sys.stdout = Report(original_stdout, report_file)

    try:
        print(student_id)
        print(f"Выбранный стиль: {style}")
        print(f"Символ для отображения точек на графике: '{marker}'")
        print(f"Первая буква фамилии: {first_letter}")
        print(f"Цветовая схема по умолчанию: '{default_cmap}'\n")
        print(f"Толщина линии по умолчанию: {pen_width}")
        print(f"Цвет кисти по умолчанию: {pen_color}")
        print(f"Красный (R): {int(pen_color[1:3], 16)}")
        print(f"Зелёный (G): {int(pen_color[3:5], 16)}")
        print(f"Синий (B):  {int(pen_color[5:7], 16)}")

        print(df.shape)
        df.info()
        print(df.isnull().sum().to_string())

        # статистика для числовых колонок
        print("Колонка>\tсреднее\tмедиана\tотклонение")
        num_cols = df.select_dtypes(include=["number"]).columns
        for col in num_cols:
            mean = df[col].mean()
            median = df[col].median()
            std = df[col].std()
            print(f"{col}>\t{mean:.2f};\t{median:.2f};\t{std:.2f}")

        # статистика для категориальных колонок
        cat_cols = df.select_dtypes(exclude=["number"]).columns
        for col in cat_cols:
            print(col)
            print(df[col].value_counts(dropna=False).to_string())

    finally:
        sys.stdout = original_stdout
        report_file.close()


if __name__ == "__main__":
    main()
