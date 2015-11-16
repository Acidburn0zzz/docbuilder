# docbuilder

Thanks for beta-testing the docbuilder toolchain!
This repository contains a number of tools to facilitate building PDF documents from XML sources. Instead of installing the toolchain on your own machine a Vagrant box will take care of the heavy lifting.


There are a number of ways to let the Vagrant box ("docbuilder") assist you for creating PDF reports from XML files.

1. The easiest way to use this Vagrant box is to login to the box, and run the build process by hand.
2. Slightly more complex to set up, but more convenient is running the build process straight from your local machine.
3. The most advanced an best workflow setup is integrating the build process into git, so that the report gets built/verified each time report.xml is changed.


## Prerequisites
+ Python (either 2 or 3)
+ VirtualBox
+ Vagrant
+ ssh

All programs have to be available in your current searchpath.

Clone this repository somewhere to your local machine, as you'll need all files.

## Initial setup
Regardless of your choice, you'll have to configure some things by hand. That's a one-time operation.

### Tell the Vagrantfile where your repository lives
* Edit the file Vagrantfile.
In the default Vagrantfile, as an example the local Windows folder Y:/ is mounted to the Vagrant folder /work.

Replace the first part (Y:/) with your local path, pointig to a repository containing a pentest.

Next, bring the vagrant machine up by starting a command shell/terminal window and issuing the command
`vagrant up`

If everything worked well, the machine is now up and running in the background.

## Login to the box, and run the build process by hand
Log in to the Vagrant box by issuing the command
`vagrant ssh`
You're now logged in to the Vagrant box, called docbuilder.
cd to the Vagrant folder that you specified for the repository (for example /work)
`cd /work`

Next, execute the build command
`docbuilder.py`
This should generate a PDF file from the sources in the repository folder, and will create the PDF output file as `Report/target/latest.pdf`
Specify the -c flag to overwrite an existing file, or -v to see debug messages of the build process. Specifying -h will show some other options.


## Running the build process from your local machine
Go to your local repository folder, and copy the following files there:
```
docbuilder_proxy.py
vagrant_proxy.py
docbuilder.yml
```

The first two files are the same for each repository. The third file (docbuilder.yml) contains repository-specific information, and has to be modified for each repository.

If you chose the name `/work` as Vagrant folder, then you don't have to change anything.
If you want to use more than one repository, then you'll have different Vagrant folders, e.g. `/repository`, `/work2`, etcetera.

Edit the file `docbuilder.yml`
Change the foldername (in the example file `/work`) to the Vagrant folder where this repositoriy is mapped to.

Example of docbuilder.yml:
```
host: docbuilder
command: cd /work; docbuilder.py
```

You shouldn't have to change the host parameter, as it points to the Vagrant box.
The command parameter contains information for what gets executed on the Vagrant box.

After you have edited `docbuilder.yml`, run the script `docbuilder_proxy.py` from your local repository.
It proxies the commands to  `docbuilder.py` on the Vagrant box, so you don't have to login anymore to build a report.

When running for the first time it will create a file containing the connection details to the Vagrant box, called `docbuilder.ssh-config`. It will use this file for the next runs, which speeds up the process.
The script will execute the same commands on the Vagrant machine. You don't have to log into the Vagrant box anymore.

## Integrating the build process into git, so that the report gets built/verified each time report.xml is changed.

(to be documented - works like a charm :smile:)


## Some Vagrant commands
The Vagrant box can be stopped using the command
`vagrant destroy`

Each time you add or modify a repository to the Vagrantfile, you'll have to stop the machine first.
The command `vagrant up` will take care of starting the machine again.




As this is BETA quality - Feedback, bugreports and issues are all welcome -  Thanks !


Peter Mosmans
