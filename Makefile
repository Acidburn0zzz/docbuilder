# GPLv3 (c) 2017 Peter Mosmans [Radically Open Security]
#
# Part of docbuilder, the official PenText toolchain
# https://pentext.com
#
# version 1.6

# The pathname on docbuilder where this parent directory can be found
# Note that this can be supplied as parameter on the command line,
# e.g. make VAGRANTMAPPING=mymapping
VAGRANTMAPPING:="repos"

SHELL=/usr/bin/bash
SOURCE=$(shell echo $${PWD\#\#*/})
REPORT=target/report-latest.pdf
QUOTE=target/offerte-latest.pdf
SUMMARY=target/summary-latest.pdf

SSH-CONFIG=docbuilder.ssh
VAGRANTID=$(shell vagrant global-status|awk '/docbuilder/{print $$1}')
VAGRANTSTATUS=$(shell vagrant global-status|awk '/docbuilder/{print $$4}')

# Targets that will not generate specific files
.PHONY: all clean $(REPORT) $(SUMMARY) reload test up

all: report quote summary

# symlink
offerte: quote

quote: $(QUOTE)

# symlink
pdf: report

report: $(REPORT)

verbose: $(SSH-CONFIG)
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -cv"

$(REPORT): $(SSH-CONFIG)
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -c"

$(QUOTE): $(SSH-CONFIG)
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -i offerte.xml -o ../target/offerte-latest.pdf -x ../xslt/generate_offerte.xsl -c"

summary: $(SUMMARY)

$(SUMMARY):
	@ssh -F $(SSH-CONFIG) docbuilder "cd /$(VAGRANTMAPPING)/$(SOURCE)/source && docbuilder.py -v -c --xslt ../xslt/summary.xsl -i management_summary.xml -o ../$(SUMMARY)"

$(SSH-CONFIG):
	@vagrant ssh-config "$(VAGRANTID)" > $(SSH-CONFIG)
	@if [ $$? -ne 0 ]; then echo "SSH not working (try 'make reload')"; exit -1; fi

clean:
	@-rm $(SSH-CONFIG) $(QUOTE) $(REPORT) 2>/dev/null || true
	@echo "Removed $(SSH-CONFIG) $(QUOTE) $(REPORT)"

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
