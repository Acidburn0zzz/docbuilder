# GPLv3 (c) 2017 Peter Mosmans [Radically Open Security]
#
# Part of docbuilder, the official PenText toolchain
# https://pentext.com
#
# version 1.0

# The pathname on docbuilder where this parent directory can be found
VAGRANTMAPPING=projects

SHELL=/usr/bin/bash
SOURCE=$(shell echo $${PWD\#\#*/})
TARGET=target/report-latest.pdf

SSH-CONFIG=docbuilder.ssh
VAGRANTID=$(shell vagrant global-status|awk '/docbuilder/{print $$1}')
VAGRANTSTATUS=$(shell vagrant global-status|awk '/docbuilder/{print $$4}')

.PHONY: clean $(TARGET) test

all: pdf

pdf: $(TARGET)

$(TARGET): $(SSH-CONFIG)
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -v -c"

$(SSH-CONFIG):
	@vagrant ssh-config "$(VAGRANTID)" > $(SSH-CONFIG)

clean:
	rm $(SSH-CONFIG)

test: test-box test-status test-connection test-path

test-box:
	@echo Verifying whether docbuilder exists as box...
	@if [ -z $(VAGRANTID) ]; then echo Could not find docbuilder box; exit -1; fi
	@echo OK

test-status:
	@echo Verifying the status of the box...
	@if [ ! "$(VAGRANTSTATUS)" == "running" ]; then echo Box not running ; exit -1; fi
	@echo OK

test-connection: $(SSH-CONFIG)
	@echo Verifying connection to the box...
	@ssh -F $(SSH-CONFIG) docbuilder id 1>/dev/null || exit -1
	@echo OK

test-path: $(SSH-CONFIG)
	@echo Verifying paths...
	@ssh -F $(SSH-CONFIG) docbuilder "ls /$(VAGRANTMAPPING)/$(SOURCE) 1>/dev/null" || exit -1
	@echo OK
