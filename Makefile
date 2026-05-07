clr:
	rm ./dist/*

build:
	python3 -m build

upload: clr build
	python3 -m twine upload ./dist/*

uptest: clr build
	twine upload --repository testpypi ./dist/*
