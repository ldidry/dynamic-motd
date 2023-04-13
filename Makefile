.PHONY: deb clean

deb: dynamic-motd.deb

clean:
	rm -rf deb dynamic-motd.deb

dynamic-motd.deb: DEBIAN/* update-motd.d/*
	rm -rf update-motd.d/.mypy_cache/
	mkdir -p deb/dynamic-motd/etc/
	cp -r update-motd.d/ deb/dynamic-motd/etc/
	cp -r DEBIAN deb/dynamic-motd/
	sed -e "s/LAST_TAG/`git tag --sort=v:refname | tail -n1`/" -i deb/dynamic-motd/DEBIAN/*
	cd deb && dpkg-deb --root-owner-group --build dynamic-motd
	mv deb/dynamic-motd.deb dynamic-motd.deb
	rm -rf deb/
