
ui.py: ui.ui
	PySide2-uic $< -o $@

sepc: main.spec
	pyinstaller $<

build.spec: main.spec
	python build.py

.PHONY:build
build: build.spec
# pyinstaller $< -i images/favicon.ico \
# 	--add-data 'images;images' \
# 	--add-data 'engines;engines' \
# 	--add-data 'audios;audios' \
# 	-F -w --version-file file_version_info.txt
	pyinstaller $< --name chess-1.0.0

.PHONY: clean
clean:
	rm -rf build
	rm -rf dist
	rm -rf build.spec