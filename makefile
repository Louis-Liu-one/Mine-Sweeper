
NAME = Mine Sweeper

build: *.py images/*
	nuitka \
		--standalone \
		--enable-plugin='tk-inter' \
		--output-filename='$(NAME)' \
		--output-dir='build' \
		--remove-output \
		--assume-yes-for-download \
		--include-data-files='images/*=images/' \
		--macos-create-app-bundle \
		--macos-app-name='$(NAME)' \
		--macos-app-icon='favicon.icns' \
		--macos-app-version='1.0' \
		'main.py'
