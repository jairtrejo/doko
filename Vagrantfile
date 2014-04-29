Vagrant::Config.run do |config|

  config.vm.box = "lucid32"

  config.vm.forward_port 8000, 8000

  config.vm.share_folder "bootstrap", "/home/vagrant/bootstrap", "./bootstrap"
  config.vm.share_folder "app", "/home/vagrant/app", "./app"
  config.vm.share_folder "static_media", "/home/vagrant/static", "./static"
  config.vm.share_folder "uploaded_media", "/home/vagrant/uploads", "./uploads"

  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = "cookbooks"
    chef.run_list = ["recipe[rohan]"]
  end

end
