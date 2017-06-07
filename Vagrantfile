# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile for docbuilder
# Version 0.3

Vagrant.configure(2) do |config|
  # Mount your local folder to a Vagrant box folder
  # syntax:
  #   config.vm.synced_folder "LOCALFOLDER", "/VAGRANTFOLDER"
  #
  # For example, if you use Windows and your repository is located in R:\,
  # You would add the following line:
  #   config.vm.synced_folder "R:/", "/repos"
  #
  # This lets the guest, docbuilder, access your repository using /repos
  #
  # Example for mounting a Unix-like filesystem folder:
  #   config.vm.synced_folder "/home/user/my/repository", "/repos"
  #
  #
  # You can mount as much folders as you want, as long as the mount names
  # (the 2nd part of the statement) are unique
  # config.vm.synced_folder "c://media//repos//projects//", "/p/"
  #
  # config.vm.synced_folder "LOCALFOLDER", "/repos"
  config.vm.provider "virtualbox" do |vb|
    # Increase / decrease for performance changes
    vb.memory = "1024"
    vb.cpus = "1"
    # workaround for some OS'es: make sure cable is plugged in
    vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
  end
  # Please don't modify the values below
  config.vm.box = "ROS/docbuilder"
  config.vm.define "docbuilder"
  config.vm.box_url = "file://docbuilder.json"
  config.vm.box_check_update = true
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.boot_timeout = 600
end
