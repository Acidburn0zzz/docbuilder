# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile for docbuilder
# Version 0.1

Vagrant.configure(2) do |config|
  # Mount your local folder to a Vagrant box folder
  # syntax:
  #   config.vm.synced_folder "LOCALFOLDER", "/VAGRANTFOLDER"
  #
  # For example, if you use Windows and your repository is located in R:\,
  # You would add the following line:
  #   config.vm.synced_folder "R:/", "/repository"
  #
  # This lets docbuilder access your repository using /repository
  # The mount name (2nd part) can be anything, as long as it is unique
  # and starts with a forward slash (absolute path).
  #
  # Example for mounting a Unix-like filesystem folder:
  #   config.vm.synced_folder "/home/user/my/repository", "/work"
  #
  #
  # You can mount as much folders as you want, as long as the mount names
  # are unique.
  config.vm.synced_folder "Y:/", "/work"

  # Please don't modify the values below  
  config.vm.box = "ROS/docbuilder"
  config.vm.define "docbuilder"
  config.vm.box_url = "docbuilder.json"
  config.vm.box_check_update = false
  config.vbguest.auto_update = false
  config.vm.synced_folder ".", "/vagrant", disabled: true
end
