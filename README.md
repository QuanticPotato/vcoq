                                                                     
             ___      ___  ______    ______      ______              
            |"  \    /"  |/" _  "\  /    " \    /    " \             
             \   \  //  /(: ( \___)// ____  \  // ____  \            
              \\  \/. ./  \/ \    /  /    ) :)/  /    )  )           
               \.    //   //  \ _(: (____/ //(: (____/ //            
                \\   /   (:   _) \\        /  \         \            
                 \__/     \_______)\"_____/    \"____/\__\           
                                                                     
      _______   ___       ____  ____   _______   __    _____  ___    
     |   __ "\ |"  |     ("  _||_ " | /" _   "| |" \  (\"   \|"  \   
     (. |__) :)||  |     |   (  ) : |(: ( \___) ||  | |.\\   \    |  
     |:  ____/ |:  |     (:  |  | . ) \/ \      |:  | |: \.   \\  |  
     (|  /      \  |___   \\ \__/ //  //  \ ___ |.  | |.  \    \. |  
    /|__/ \    ( \_|:  \  /\\ __ //\ (:   _(  _|/\  |\|    \    \ |  
    (_______)    \_______)(__________) \_______)(__\_|_)\___|\____\)  
                                                                     
                                                                     
Introduction
============

VCoq is a vim plugin. It provides a user-friendly interface in order to use the Coq Proof Assistant.


Installation
============

This plugin can be used as a bundle, with the [pathogen plugin][1]. Hence, you just have to clone this repository in your bundles directory (by default, it is ~/.vim/bundle) :

	cd ~/.vim/bundle
	git clone https://github.com/Choups314/vcoq.git


Using
=====

First of all, launch the plugin with <F9>.  
Then you can open a file with ```:O filename``` and write the current file with ```:W filename```. (The classical commands :w and :e will not work in the plugin)
To send a chunk to the coqtop process, use the <Ctrl+j> map. You can also backtrack the last chunk with <Ctrl+l>

[1]:https://github.com/tpope/vim-pathogen
