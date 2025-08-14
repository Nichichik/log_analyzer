import argparse
import json
from collections import defaultdict
from tabulate import tabulate


def process_log_file(file_path):
    """Обрабатывает один лог-файл и возвращает собранную статистику."""
    stats = defaultdict(lambda: defaultdict(float))
    try:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    url = log_entry.get('url')
                    response_time = log_entry.get('response_time')

                    if url and response_time:
                        stats[url]['count'] += 1
                        stats[url]['total_time'] += float(response_time)
                except (json.JSONDecodeError, TypeError):
                    continue
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден!")
        return None
    return stats


def create_report(stats):
    """Принимает статистику и готовит данные для таблицы."""
    report_data = []
    for url, data in stats.items():
        count = data['count']
        avg_time = data['total_time'] / count if count > 0 else 0
        report_data.append({
            'handler': url,
            'total': count,
            'avg_response_time': round(avg_time, 3)
        })
    return report_data


def main():
    parser = argparse.ArgumentParser(description="Анализатор лог-файлов")
    parser.add_argument(
        '--file',
        nargs='+',
        required=True,
        help="Пути к одному или нескольким лог-файлам"
    )
    parser.add_argument(
        '--report',
        default='average',
        help="Тип отчета"
    )
    args = parser.parse_args()

    log_files = args.file
    total_stats = defaultdict(lambda: defaultdict(float))

    for log_file in log_files:
        stats_from_file = process_log_file(log_file)
        if stats_from_file:
            for url, data in stats_from_file.items():
                total_stats[url]['count'] += data['count']
                total_stats[url]['total_time'] += data['total_time']

    if total_stats:
        final_report = create_report(total_stats)
        final_report.sort(key=lambda item: item['total'], reverse=True)
        print(tabulate(final_report, headers='keys', tablefmt='psql'))
    else:
        print("Не найдено данных для анализа в указанных файлах.")


if __name__ == "__main__":
    main()
