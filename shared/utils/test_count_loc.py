import pytest
import pathlib
from unittest.mock import patch
from your_module import count_lines_of_code  # replace 'your_module' with your actual module name

def test_count_lines_of_code_empty_directory(tmp_path):
    directory = tmp_path / 'empty_directory'
    directory.mkdir()
    assert count_lines_of_code(directory) == 0

def test_count_lines_of_code_single_line_file(tmp_path):
    directory = tmp_path / 'single_line_directory'
    directory.mkdir()
    file = directory / 'single_line_file.txt'
    file.write_text('single line\n')
    assert count_lines_of_code(directory) == 1

def test_count_lines_of_code_multiple_lines_file(tmp_path):
    directory = tmp_path / 'multiple_lines_directory'
    directory.mkdir()
    file = directory / 'multiple_lines_file.txt'
    file.write_text('line1\nline2\nline3\n')
    assert count_lines_of_code(directory) == 3

def test_count_lines_of_code_subdirectory(tmp_path):
    directory = tmp_path / 'parent_directory'
    directory.mkdir()
    subdirectory = directory / 'subdirectory'
    subdirectory.mkdir()
    file = subdirectory / 'file.txt'
    file.write_text('line1\nline2\n')
    assert count_lines_of_code(directory) == 2

def test_count_lines_of_code_non_readable_file(tmp_path, capsys):
    directory = tmp_path / 'non_readable_directory'
    directory.mkdir()
    file = directory / 'non_readable_file.txt'
    file.write_text('line1\nline2\n')
    file.chmod(0o000)  # make file non-readable
    count_lines_of_code(directory)
    captured = capsys.readouterr()
    assert 'Error reading file' in captured.out

def test_count_lines_of_code_non_existent_directory(tmp_path):
    directory = tmp_path / 'non_existent_directory'
    assert count_lines_of_code(directory) == 0

def test_main(capsys):
    with patch('sys.argv', ['your_module', '.']):
        with patch('builtins.print') as mock_print:
            import your_module  # replace 'your_module' with your actual module name
            mock_print.assert_called()