@ECHO OFF
@python "%~dp0Sources\py_pkg.py" "PySide2"
@python "%~dp0Sources\review-ui-application02.py" %*
pause