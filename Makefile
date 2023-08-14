# run anki version 21.54
# with gldriver6 > software
docker_img_tag="0.3"
dockeranki:
	xhost +
	docker run -it --rm -e DISPLAY=$$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/valence/.local/share/Anki2:/root/.local/share/Anki2 -v $$(pwd):/home krop_anki:"${docker_img_tag}"
	xhost -

# from running container
# have to runanki.sh .. see README **hold shift**
ankirun:
	. /etc/default/locale
	export LANG
	export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"
	anki --no-sandbox

anki:
	xhost + 
	docker run -it --rm -e DISPLAY=$$DISPLAY  -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/valence/.local/share/Anki2:/root/.local/share/Anki2 -v $$(pwd):/home krop_anki:0.2 /bin/bash -c '. /etc/default/locale; export LANG; export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"; anki --in-process-gpu --no-sandbox;'

anki20:
	xhost +
	docker run -it -e DISPLAY=$DISPLAY  -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/valence/.local/share/Anki2:/root/.local/share/Anki2 -v $(pwd):/home ubuntu/anki20:latest -e DISPLAY -e XAUTHORITY=$XAUTH -e QT_X11_NO_MITSHM=1 /bin/bash -c '. /etc/default/locale; export LANG; anki;'

readme:
	pandoc -s README.md -o readme.html	
	qutebrowser readme.html

cp:
	cp -r /home/valence/Projects/AnkiScripts/[]  /home/valence/.local/share/Anki2/addons21/[] 	


