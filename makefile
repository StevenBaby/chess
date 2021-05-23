
src/ui.py: src/ui.ui
	PySide2-uic $< -o $@

ui: src/ui.py

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
	pyinstaller $<

.PHONY: clean
clean:
	rm -rf build/build
	rm -rf build.spec
	rm -rf build