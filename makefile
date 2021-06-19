
.PHONY: build
build: src/main.py
	pyinstaller $< -i src/images/favicon.ico \
		--add-data 'src/images;images' \
		--add-data 'src/engines;engines' \
		--add-data 'src/audios;audios' \
		-F -w --name chess-$(VERSION)


src/ui/settings.py: src/ui/settings.ui
	PySide2-uic $< -o $@

.PHONY:ui
ui: src/ui/settings.py

VERSION:= $(shell python -c "from src.version import VERSION; print(VERSION)")


.PHONY: clean
clean:
	rm -rf build/*/*
	rm -rf build/*
	rm -rf build
	rm -rf *.spec
	rm -rf .qt_for_python
