VERSION:= $(shell python -c "from src import version; print(version.VERSION) ")

.PHONY: build
build: dist/chess-$(VERSION).exe dist/chess.exe
	-

dist/chess-$(VERSION).exe: src/main.py
	pyinstaller $< -i src/images/favicon.ico \
		--add-data 'src/images;images' \
		--add-data 'src/engines;engines' \
		--add-data 'src/audios;audios' \
		-F -w --name chess-$(VERSION)
	python -c "from src import version; version.increase();"

dist/chess.exe: dist/chess-$(VERSION).exe
	cp $< $@

.PHONY: debug
debug: dist/chess-$(VERSION)-debug.exe
	-

dist/chess-$(VERSION)-debug.exe: src/main.py
	pyinstaller $< -i src/images/favicon.ico \
		--add-data 'src/images;images' \
		--add-data 'src/engines;engines' \
		--add-data 'src/audios;audios' \
		-F --name chess-$(VERSION)-debug 
	cp $@ dist/chess.exe

.PHONY: main
main: ui
	python src/main.py


src/ui/%.py: src/ui/%.ui
	PySide2-uic $< -o $@

.PHONY:ui
ui: src/ui/settings.py src/ui/method.py

.PHONY: clean
clean:
	rm -rf build/*/*
	rm -rf build/*
	rm -rf build
	rm -rf *.spec
	rm -rf .qt_for_python/*/*
	rm -rf .qt_for_python/*
	rm -rf .qt_for_python
