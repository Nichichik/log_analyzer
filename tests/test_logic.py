import pytest
import sys


from main import (
    process_log_file,
    create_report,
    main as main_function
)


def test_process_log_file_happy_path(tmp_path):
    log_content = (
        '{"url": "/api/A", "response_time": 0.1}\n'
        '{"url": "/api/B", "response_time": 0.2}\n'
        '{"url": "/api/A", "response_time": 0.3}\n'
    )
    log_file = tmp_path / "test.log"
    log_file.write_text(log_content)
    stats = process_log_file(log_file)
    assert len(stats) == 2
    assert stats["/api/A"]["count"] == 2
    assert stats["/api/A"]["total_time"] == pytest.approx(0.4)


def test_process_log_file_empty_file(tmp_path):
    log_file = tmp_path / "empty.log"
    log_file.write_text("")
    stats = process_log_file(log_file)
    assert stats == {}


def test_process_log_file_non_existent_file():
    stats = process_log_file("path/to/non_existent_file.log")
    assert stats is None

def test_create_report_happy_path():
    test_stats = {
        "/api/users": {'count': 3, 'total_time': 0.6},
        "/api/posts": {'count': 1, 'total_time': 0.12345}
    }
    report = create_report(test_stats)
    assert len(report) == 2
    user_report = next(item for item in report if item["handler"] == "/api/users")
    assert user_report['avg_response_time'] == 0.2
    post_report = next(item for item in report if item["handler"] == "/api/posts")
    assert post_report['avg_response_time'] == 0.123


def test_create_report_empty_stats():
    report = create_report({})
    assert report == []


def test_main_function_end_to_end(tmp_path, capsys):
    log1_content = '{"url": "/api/A", "response_time": 0.1}\n'
    log_file1 = tmp_path / "test1.log"
    log_file1.write_text(log1_content)

    log2_content = '{"url": "/api/A", "response_time": 0.3}\n'
    log_file2 = tmp_path / "test2.log"
    log_file2.write_text(log2_content)

    sys.argv = [
        'main.py',
        '--file',
        str(log_file1),
        str(log_file2),
        '--report',
        'average'
    ]
    main_function()
    captured = capsys.readouterr()
    output = captured.out
    assert "/api/A" in output
    assert "2" in output
    assert "0.2" in output


def test_main_with_no_files_argument(capsys):
    with pytest.raises(SystemExit):
        sys.argv = ['main.py']
        main_function()
    captured = capsys.readouterr()
    assert 'required: --file' in captured.err
    