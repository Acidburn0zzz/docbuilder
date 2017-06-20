# GPLv3 (c) 2017 Peter Mosmans [Radically Open Security]
#
# Part of docbuilder, the official PenText toolchain
# https://pentext.com
#
# version 0.1

# The pathname on docbuilder where this parent directory can be found
VAGRANTMAPPING=projects

SHELL=/usr/bin/bash
SOURCE=$(shell echo $${PWD\#\#*/})
TARGET=target/report-latest.pdf

SSH-CONFIG=docbuilder.ssh
VAGRANTID=$(shell vagrant global-status|awk '/docbuilder/{print $$1}')

.PHONY: clean $(TARGET)

all: pdf

pdf: $(TARGET)

$(TARGET): $(SSH-CONFIG)
	ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -v -c"

$(SSH-CONFIG):
	vagrant ssh-config "$(VAGRANTID)" > $(SSH-CONFIG)

clean:
	rm $(SSH-CONFIG)
