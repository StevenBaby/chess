
.PHONY: build
build: src/main.py
	pyinstaller $< -i src/images/favicon.ico \
		--add-data 'src/images;images' \
		--add-data 'src/engines;engines' \
		--add-data 'src/audios;audios' \
		-F -w --name chess-$(VERSION)

.PHONY: main
main: ui
	python src/main.py


src/ui/%.py: src/ui/%.ui
	PySide2-uic $< -o $@

.PHONY:ui
ui: src/ui/settings.py src/ui/comments.py

VERSION:= $(shell python -c "from src.version import VERSION; print(VERSION)")


.PHONY: clean
clean:
	rm -rf build/*/*
	rm -rf build/*
	rm -rf build
	rm -rf *.spec
	rm -rf .qt_for_python/*/*
	rm -rf .qt_for_python/*
	rm -rf .qt_for_python
