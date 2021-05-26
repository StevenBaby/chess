
src/ui.py: src/ui.ui
	PySide2-uic $< -o $@

ui: src/ui.py

VERSION:= $(shell python -c "from src.version import VERSION; print(VERSION)")

build.spec: main.spec
	sed 's/version/$(VERSION)/' $< > $@

.PHONY:build
build: src/main.py
	pyinstaller $< -i src/images/favicon.ico \
		--add-data 'src/images;images' \
		--add-data 'src/engines;engines' \
		--add-data 'src/audios;audios' \
		-F -w --name chess-$(VERSION)

.PHONY: test
test:
	echo $(VERSION)

.PHONY: clean
clean:
	rm -rf build/*/*
	rm -rf build/*
	rm -rf build
	rm -rf *.spec
