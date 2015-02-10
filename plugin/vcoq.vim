let s:current_dir=expand("<sfile>:p:h")
py import sys, vim
py if not vim.eval("s:current_dir") in sys.path:
	\  sys.path.append(vim.eval("s:current_dir"))
py import vcoq

" User commands and mappings

function! LaunchC() 
	py vcoq.main.launch()
endfunction

function! Next()
	py vcoq.main.next()
endfunction

map <F9> :call LaunchC()<CR>

function! MapVcoq()
	" WARNING : 	imaps.vim already use the <c-j> map. To avoid any conflicts,
	" 		we first unmap this key sequence (You might want to change
	" 		it if <c-j> is already in use in another plugin)
	unmap <c-j>
	map <c-j>  :call Next()<CR>
	imap <c-j> <Esc>:call Next()<CR>a
endfunction

function! SetupHighlights()
	highlight ErrorMessage ctermbg=Red ctermfg=White
	" The following highlights correspond to the python Color enum
	highlight Red ctermbg=Red ctermfg=White
	highlight Blue ctermbg=Blue ctermfg=White
	highlight Yellow ctermbg=Yellow ctermfg=Black
	highlight White ctermbg=White ctermfg=Black
	highlight Green ctermbg=Green ctermfg=White
	highlight Purple ctermbg=Magenta ctermfg=White
endfunction

call SetupHighlights()

autocmd BufEnter * py vcoq.main.onBufferFocus(True)
autocmd BufLeave * py vcoq.main.onBufferFocus(False)
autocmd BufWinLeave * py vcoq.main.onClose()
autocmd VimResized * py vcoq.main.onVimResized()

function! UpdateWindows()
	call UpdateWindowsNumber()
	py vcoq.main.onWindowsUpdated()
endfunction

" Fill the editWindow, goalsWindow, tagbarWindow ... script variables
function! UpdateWindowsNumber()
	let s:editWindow = UpdateWindowNr('Edit')
	let s:consoleWindow = UpdateWindowNr('Console_output')
	let s:tagbarWindow = UpdateWindowNr('Tags')
	let s:compiledWindow = UpdateWindowNr('Accepted_statements')
	let s:goalsWindow = UpdateWindowNr('Goals')
	let s:inputWindow = UpdateWindowNr('Console_input')
endfunction

function! UpdateWindowNr(buffName)
	let l:windowNumber = bufwinnr(a:buffName)
	if l:windowNumber == -1
		py vccoq.main.shutdown()
		echoe 'The ' . a:buffName . ' window has been closed ! (Vcoq is going to close ..)'	
		" TODO kill the vcoq
	endif
	return l:windowNumber
endfunction

