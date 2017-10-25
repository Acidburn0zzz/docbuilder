# GPLv3 (c) 2017 Peter Mosmans [Radically Open Security]
#
# Part of docbuilder, the official PenText toolchain
# https://pentext.com
#
# version 1.2

# The pathname on docbuilder where this parent directory can be found
VAGRANTMAPPING=repos

SHELL=/usr/bin/bash
SOURCE=$(shell echo $${PWD\#\#*/})
TARGET=target/report-latest.pdf
SUMMARY=target/summary-latest.pdf

SSH-CONFIG=docbuilder.ssh
VAGRANTID=$(shell vagrant global-status|awk '/docbuilder/{print $$1}')
VAGRANTSTATUS=$(shell vagrant global-status|awk '/docbuilder/{print $$4}')

.PHONY: clean $(TARGET) $(SUMMARY) reload test up

all: pdf

pdf: $(TARGET)

verbose: $(SSH-CONFIG)
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -cv"

$(TARGET): $(SSH-CONFIG)
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -c"

summary: $(SUMMARY)

$(SUMMARY):
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -v -c --xslt ../xslt/summary.xsl -i management_summary.xml -o ../$(SUMMARY)"

$(SSH-CONFIG):
	@vagrant ssh-config "$(VAGRANTID)" > $(SSH-CONFIG)
	@if [ $$? -ne 0 ]; then echo "SSH not working (try 'make reload')"; exit -1; fi

clean:
	rm $(SSH-CONFIG)

reload:
	@vagrant reload "$(VAGRANTID)"

test: test-box test-status test-connection test-path

test-box:
	@echo Verifying whether docbuilder exists as box...
	@if [ -z $(VAGRANTID) ]; then echo Could not find docbuilder box; exit -1; fi
	@echo OK

test-status:
	@echo Verifying the status of the box...
	@if [ ! "$(VAGRANTSTATUS)" == "running" ]; then echo "Box not running (try 'make up')"; exit -1; fi
	@echo OK

test-connection: $(SSH-CONFIG)
	@echo Verifying connection to the box...
	@ssh -F $(SSH-CONFIG) docbuilder id >/dev/null
	@if [ $$? -ne 0 ]; then echo "Cannot connect to docbuilder (try 'make clean' first) "; exit -1; fi
	@echo OK

test-path: $(SSH-CONFIG)
	@echo Verifying paths...
	@ssh -F $(SSH-CONFIG) docbuilder "ls /$(VAGRANTMAPPING)/$(SOURCE) 1>/dev/null" || exit -1
	@echo OK

up:
	@vagrant up "$(VAGRANTID)"
